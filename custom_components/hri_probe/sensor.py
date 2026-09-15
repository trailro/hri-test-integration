"""HRI Probe 1.0.0 sensor (YAML)."""
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, VERSION


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return
    conf = hass.data[DOMAIN]
    async_add_entities([ProbeSensor(conf["name"], conf["value"], "yaml")])


class ProbeSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, name, value, source):
        self._attr_name = f"Probe {name}"
        self._attr_unique_id = f"hri_probe_{name}"
        self._attr_native_value = value
        self._attr_extra_state_attributes = {"source": source, "version": VERSION}
