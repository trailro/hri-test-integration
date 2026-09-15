"""HRI Probe 1.0.0: configured in YAML only."""
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({vol.Required("name"): cv.string, vol.Optional("value", default=1): vol.Coerce(int)})},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    if DOMAIN not in config:
        return True
    hass.data[DOMAIN] = config[DOMAIN]
    hass.async_create_task(discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config))
    return True
