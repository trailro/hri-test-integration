"""A probe number, so number.set_value can be exercised against a bounded slider with a unit."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeNumber(entry)])


class ProbeNumber(ProbeEntity, NumberEntity):
    """Only the native_* API is used: overriding value/step/set_value logs a deprecation
    warning from NumberEntity.__init_subclass__ (number/__init__.py:216)."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = 42.0

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "number", "number", FAMILY_CORE)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
