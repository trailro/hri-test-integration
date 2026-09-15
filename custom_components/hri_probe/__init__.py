"""HRI Probe 2.0.0: config flow; YAML is imported into a config entry."""
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

PLATFORMS = ["sensor"]
CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Required("name"): cv.string, vol.Optional("value", default=1): vol.Coerce(int)})},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config[DOMAIN]))
        )
    return True


async def async_setup_entry(hass, entry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
