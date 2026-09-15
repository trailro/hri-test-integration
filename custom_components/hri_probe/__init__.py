"""HRI Probe 3.0.0: config entry version 2 (migrated from 1), options flow; YAML is no longer read."""
import logging

import voluptuous as vol

from .const import DOMAIN
from . import legacy  # noqa: F401

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]
CONFIG_SCHEMA = vol.Schema({DOMAIN: dict}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    if DOMAIN in config:
        _LOGGER.warning("YAML configuration for hri_probe is no longer read since 3.0.0: remove it")
    return True


async def async_migrate_entry(hass, entry):
    if entry.version > 2:
        return False
    if entry.version == 1:
        data = dict(entry.data)
        data["initial"] = data.pop("value", 1)
        hass.config_entries.async_update_entry(entry, data=data, options={"step": 1, **entry.options}, version=2)
        _LOGGER.info("migrated hri_probe entry %s from version 1 to 2", entry.entry_id)
    return True


async def async_setup_entry(hass, entry):
    entry.async_on_unload(entry.add_update_listener(_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
