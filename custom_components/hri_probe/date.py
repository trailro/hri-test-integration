"""A date entity that keeps whatever date.set_value sends it: the set-value command path."""
from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeDate(entry)])


class ProbeDate(ProbeEntity, DateEntity):
    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "date", "date", FAMILY_CORE)
        self._attr_native_value = date(2026, 1, 1)

    async def async_set_value(self, value: date) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
