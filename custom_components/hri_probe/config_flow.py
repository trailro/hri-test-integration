"""HRI Probe 7.0.0 flows (entry version 3): every shape a flow renderer can meet.

A multi-step user flow with a menu, an advanced step holding one field per selector
kind, per-field and base errors, the three aborts (already_configured, unknown,
reconfigure_successful), reconfigure, reauth, a progress step, and an options flow
whose second step depends on what the first one chose.
"""
from __future__ import annotations

import asyncio
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from .const import CRASH_NAME, DEFAULT_OPTIONS, DOMAIN, PROBE_SECONDS, REAUTH_TOKEN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema({vol.Required("name"): str, vol.Optional("initial", default=1): int})

RECONFIGURE_SCHEMA = vol.Schema({
    vol.Required("initial", default=1): selector.NumberSelector(
        selector.NumberSelectorConfig(min=0, max=1000, step=1, mode=selector.NumberSelectorMode.BOX)
    ),
    vol.Optional("label", default=""): selector.TextSelector(),
})

REAUTH_SCHEMA = vol.Schema({
    vol.Required("token"): selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
    ),
})

TUNING_SCHEMA = vol.Schema({
    vol.Required("step", default=1): selector.NumberSelector(
        selector.NumberSelectorConfig(min=1, max=50, step=1, mode=selector.NumberSelectorMode.BOX)
    ),
    vol.Required("profile", default="balanced"): selector.SelectSelector(
        selector.SelectSelectorConfig(options=["quiet", "balanced", "aggressive"])
    ),
})

# the two shapes async_step_tuning_detail picks between, on the profile chosen above
AGGRESSIVE_SCHEMA = vol.Schema({
    vol.Required("burst", default=5): selector.NumberSelector(
        selector.NumberSelectorConfig(min=1, max=20, step=1, mode=selector.NumberSelectorMode.SLIDER)
    ),
    vol.Required("confirm", default=False): selector.BooleanSelector(),
})

CALM_SCHEMA = vol.Schema({
    vol.Required("idle_minutes", default=10): selector.NumberSelector(
        selector.NumberSelectorConfig(min=1, max=60, step=1, mode=selector.NumberSelectorMode.BOX)
    ),
})

REPORTING_SCHEMA = vol.Schema({
    vol.Required("channels", default=["log"]): selector.SelectSelector(
        selector.SelectSelectorConfig(options=["log", "mqtt", "notification"], multiple=True)
    ),
    vol.Required("include_attributes", default=True): selector.BooleanSelector(),
})


def advanced_schema():
    """One field per selector kind a flow renderer has to cope with."""
    return vol.Schema({
        vol.Required("label", default="probe"): selector.TextSelector(),
        vol.Optional("note", default=""): selector.TextSelector(
            selector.TextSelectorConfig(multiline=True)
        ),
        vol.Required("level", default=50): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, max=100, step=5, mode=selector.NumberSelectorMode.SLIDER, unit_of_measurement="%"
            )
        ),
        vol.Required("retries", default=3): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=10, step=1, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required("verbose", default=False): selector.BooleanSelector(),
        vol.Required("profile", default="balanced"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=["quiet", "balanced", "eco mode"],  # the space must survive the round trip
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required("speed", default="normal"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"value": "slow", "label": "Slow and careful"},
                    {"value": "normal", "label": "Normal"},
                    {"value": "fast", "label": "Fast"},
                ],
                mode=selector.SelectSelectorMode.LIST,
            )
        ),
        vol.Required("families", default=["core"]): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=["core", "comfort", "security", "media"], multiple=True
            )
        ),
        vol.Optional("extra", default={"scale": 1}): selector.ObjectSelector(),
        # a value the options do not list, and a list that takes typed values: a renderer that
        # only draws the listed options drops these without saying so
        vol.Required("flavour", default="vanilla"): selector.SelectSelector(
            selector.SelectSelectorConfig(options=["sweet", "salty"], custom_value=True)
        ),
        vol.Required("tags", default=["core", "custom"]): selector.SelectSelector(
            selector.SelectSelectorConfig(options=["core", "comfort"], multiple=True, custom_value=True)
        ),
        # Home Assistant accepts a fractional duration; a whole-number input cannot submit these
        vol.Optional("grace", default={"hours": 0, "minutes": 0, "seconds": 0.5}): selector.DurationSelector(),
        vol.Optional("lag", default={"hours": 0, "minutes": 1.5, "seconds": 0}): selector.DurationSelector(),
        # no renderer is obliged to know this one: it is here to find out what happens
        vol.Optional("window", default={"hours": 0, "minutes": 5, "seconds": 0}): selector.DurationSelector(),
        vol.Required("limits"): section(
            vol.Schema({
                vol.Optional("ceiling", default=100): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=100, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Optional("strict", default=False): selector.BooleanSelector(),
            }),
            {"collapsed": False},
        ),
    })


def advanced_errors(user_input):
    """A per-field error and a base error, both returned as errors, never raised."""
    errors = {}
    extra = user_input.get("extra") or {}
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in extra.values()):
        errors["extra"] = "invalid_object"
    if user_input["speed"] == "fast" and user_input["retries"] > 5:
        errors["base"] = "incompatible"
    return errors


class ProbeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 3

    def __init__(self) -> None:
        self._data: dict = {}
        self._probe_task: asyncio.Task | None = None

    # ----- the user flow: name, then a menu ------------------------------

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            name = user_input["name"]
            if name == CRASH_NAME:
                return self._unknown()
            if not name.strip() or name != name.strip():
                errors["name"] = "invalid_name"
            else:
                await self.async_set_unique_id(name)
                self._abort_if_unique_id_configured()
                self._data = {"name": name, "initial": user_input["initial"], "auth_ok": True}
                return await self.async_step_path()
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(USER_SCHEMA, user_input or {}),
            errors=errors,
        )

    async def async_step_path(self, user_input=None):
        # the flow manager routes the choice itself; this step exists because it
        # insists that a step with the id the menu was shown under is callable
        return self.async_show_menu(step_id="path", menu_options=["basic", "advanced", "probe"])

    async def async_step_basic(self, user_input=None):
        """The menu branch that needs nothing else: menu straight to create_entry."""
        return self._create({**self._data, "path": "basic"})

    async def async_step_advanced(self, user_input=None):
        errors = {}
        if user_input is not None:
            errors = advanced_errors(user_input)
            if not errors:
                return self._create({**self._data, "path": "advanced", **user_input})
        return self.async_show_form(
            step_id="advanced",
            data_schema=self.add_suggested_values_to_schema(advanced_schema(), user_input or {}),
            errors=errors,
            description_placeholders={"name": self._data.get("name", "")},
            last_step=True,
        )

    async def async_step_probe(self, user_input=None):
        if self._probe_task is None:
            self._probe_task = self.hass.async_create_task(self._probing(), eager_start=False)
        if not self._probe_task.done():
            return self.async_show_progress(
                step_id="probe",
                progress_action="probing",
                description_placeholders={"seconds": str(PROBE_SECONDS)},
                progress_task=self._probe_task,
            )
        return self.async_show_progress_done(next_step_id="probe_done")

    async def async_step_probe_done(self, user_input=None):
        return self._create({**self._data, "path": "probe"})

    async def _probing(self) -> None:
        await asyncio.sleep(PROBE_SECONDS)

    # ----- reconfigure and reauth ----------------------------------------

    async def async_step_reconfigure(self, user_input=None):
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data_updates=user_input)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(RECONFIGURE_SCHEMA, entry.data),
            description_placeholders={"title": entry.title},
        )

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            if user_input["token"] != REAUTH_TOKEN:
                errors["token"] = "invalid_auth"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(), data_updates={"auth_ok": True}
                )
        return self.async_show_form(step_id="reauth_confirm", data_schema=REAUTH_SCHEMA, errors=errors)

    # ----- helpers --------------------------------------------------------

    def _create(self, data):
        return self.async_create_entry(title=data["name"], data=data, options=dict(DEFAULT_OPTIONS))

    def _unknown(self):
        """What a flow does with an error it did not expect: abort, not a traceback."""
        try:
            raise RuntimeError("hri_probe was asked to fail this flow")
        except RuntimeError:
            _LOGGER.exception("hri_probe config flow failed")
            return self.async_abort(reason="unknown")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ProbeOptionsFlow()


class ProbeOptionsFlow(OptionsFlowWithReload):
    def __init__(self) -> None:
        self._tuning: dict = {}

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["tuning", "reporting"])

    async def async_step_tuning(self, user_input=None):
        if user_input is not None:
            self._tuning = user_input
            return await self.async_step_tuning_detail()
        return self.async_show_form(
            step_id="tuning",
            data_schema=self.add_suggested_values_to_schema(TUNING_SCHEMA, self.config_entry.options),
        )

    async def async_step_tuning_detail(self, user_input=None):
        aggressive = self._tuning.get("profile") == "aggressive"
        if user_input is not None:
            return self.async_create_entry(
                data={**self.config_entry.options, **self._tuning, **user_input}
            )
        return self.async_show_form(
            step_id="tuning_detail",
            data_schema=AGGRESSIVE_SCHEMA if aggressive else CALM_SCHEMA,
            description_placeholders={"profile": str(self._tuning.get("profile", ""))},
            last_step=True,
        )

    async def async_step_reporting(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data={**self.config_entry.options, **user_input})
        return self.async_show_form(
            step_id="reporting",
            data_schema=self.add_suggested_values_to_schema(REPORTING_SCHEMA, self.config_entry.options),
            last_step=True,
        )
