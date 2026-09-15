"""HRI Probe 2.0.0 sensor (config entry)."""
from homeassistant.components.sensor import SensorEntity

from .const import VERSION


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ProbeSensor(entry.data["name"], entry.data.get("value", 1), "entry")])


class ProbeSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, name, value, source):
        self._attr_name = f"Probe {name}"
        self._attr_unique_id = f"hri_probe_{name}"
        self._attr_native_value = value
        self._attr_extra_state_attributes = {"source": source, "version": VERSION}
