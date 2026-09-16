"""HRI Probe 7.0.0: every entity platform Home Assistant has, the services a test needs, and the flows.

The entity platforms cover the service calls a consuming Home Assistant can make (light.turn_on,
climate.set_temperature, vacuum.start...). The services here are the ones no entity provides:
driving the entities that have no service of their own, making everything unavailable and back,
a service that answers, one that fails, one that takes too long, one that creates persistent
notifications, the stuck executor thread from 5.0.0, and hri_probe.expire_auth, which makes the
entry fail authentication so Home Assistant starts the reauth flow the way it does for real.
"""
from __future__ import annotations

import asyncio
import logging
import threading

import voluptuous as vol

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, PLATFORMS, SIGNAL_FLAP, SIGNAL_PULSE, SIGNAL_TICK, VERSION

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema({DOMAIN: dict}, extra=vol.ALLOW_EXTRA)

_FOREVER = threading.Event()  # never set


def _block_forever() -> None:
    _LOGGER.warning("hri_probe.stuck: an executor thread now waits forever")
    _FOREVER.wait()


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    if DOMAIN in config:
        _LOGGER.warning("YAML configuration for hri_probe is no longer read since 3.0.0: remove it")
    data = hass.data.setdefault(DOMAIN, {"ticks": 0})

    async def _tick(call: ServiceCall) -> None:
        """Drive the entities no service can change: sensors, binary sensors, events, the tracker."""
        for _ in range(call.data["count"]):
            data["ticks"] += 1
            async_dispatcher_send(hass, SIGNAL_TICK, data["ticks"])
        # once per call: an entity that toggles would be back where it started after an even count
        async_dispatcher_send(hass, SIGNAL_PULSE)

    async def _flap(call: ServiceCall) -> None:
        """Every entity goes unavailable and comes back: the consumer must show unavailable, not a stale value."""
        async_dispatcher_send(hass, SIGNAL_FLAP, False)
        await asyncio.sleep(call.data["seconds"])
        async_dispatcher_send(hass, SIGNAL_FLAP, True)

    async def _notify(call: ServiceCall) -> None:
        notification_id = call.data["notification_id"]
        if call.data["dismiss"]:
            persistent_notification.async_dismiss(hass, notification_id)
            return
        persistent_notification.async_create(hass, call.data["message"], call.data["title"], notification_id)

    async def _echo(call: ServiceCall) -> ServiceResponse:
        """A service with a response, to check that the answer travels back with the call."""
        return {"echo": dict(call.data), "ticks": data["ticks"], "version": VERSION}

    async def _fail(call: ServiceCall) -> None:
        raise HomeAssistantError(call.data["message"])

    async def _slow(call: ServiceCall) -> None:
        """Longer than HRI_CALL_TIMEOUT (60 s by default): the caller must get a timeout, not a hang."""
        await asyncio.sleep(call.data["seconds"])

    async def _stuck(call: ServiceCall) -> None:
        hass.async_add_executor_job(_block_forever)  # not awaited: the loop stays free, only the thread is gone

    async def _expire_auth(call: ServiceCall) -> None:
        """Mark the entry unauthenticated and reload it: setup then raises ConfigEntryAuthFailed
        and Home Assistant starts the reauth flow itself, which is the only way a real one starts."""
        wanted = call.data["entry_id"]
        for entry in hass.config_entries.async_entries(DOMAIN):
            if wanted and entry.entry_id != wanted:
                continue
            hass.config_entries.async_update_entry(entry, data={**entry.data, "auth_ok": False})
            hass.config_entries.async_schedule_reload(entry.entry_id)

    text = vol.All(str, vol.Length(max=255))
    for name, handler, schema, response in (
        ("tick", _tick, {vol.Optional("count", default=1): vol.All(int, vol.Range(min=1, max=100))}, None),
        ("flap", _flap, {vol.Optional("seconds", default=5): vol.All(int, vol.Range(min=1, max=600))}, None),
        ("notify", _notify, {
            vol.Optional("title", default="HRI Probe"): text,
            vol.Optional("message", default="Persistent notification from hri_probe."): text,
            vol.Optional("notification_id", default=f"{DOMAIN}_manual"): text,
            vol.Optional("dismiss", default=False): bool,
        }, None),
        ("echo", _echo, {vol.Optional("payload", default={}): dict,
                         vol.Optional("words", default=[]): vol.All(cv.ensure_list, [cv.string])}, SupportsResponse.ONLY),
        ("fail", _fail, {vol.Optional("message", default="hri_probe.fail was called"): text}, None),
        ("slow", _slow, {vol.Optional("seconds", default=90): vol.All(int, vol.Range(min=1, max=600))}, None),
        ("stuck", _stuck, {}, None),
        ("expire_auth", _expire_auth, {vol.Optional("entry_id", default=""): text}, None),
    ):
        kwargs = {"schema": vol.Schema(schema)}
        if response is not None:
            kwargs["supports_response"] = response
        hass.services.async_register(DOMAIN, name, handler, **kwargs)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version > 3:
        return False
    was = entry.version
    data, options = dict(entry.data), dict(entry.options)
    if was == 1:
        data["initial"] = data.pop("value", 1)
        options.setdefault("step", 1)
    if was < 3:
        # 7.0.0 keeps the auth state and the branch the user flow took in the entry
        data.setdefault("auth_ok", True)
        data.setdefault("path", "basic")
        options.setdefault("profile", "balanced")
    hass.config_entries.async_update_entry(entry, data=data, options=options, version=3)
    _LOGGER.info("migrated hri_probe entry %s from version %s to 3", entry.entry_id, was)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not entry.data.get("auth_ok", True):
        raise ConfigEntryAuthFailed("the probe token expired; hri_probe.expire_auth was called")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # a notification on every setup: it must show up on the consuming side too
    persistent_notification.async_create(
        hass,
        f"hri_probe {VERSION} set up '{entry.title}' with {len(PLATFORMS)} platforms.",
        "HRI Probe ready",
        f"{DOMAIN}_{entry.entry_id}_setup",
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    persistent_notification.async_dismiss(hass, f"{DOMAIN}_{entry.entry_id}_setup")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
