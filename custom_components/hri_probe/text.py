"""Probe text: text.set_value round trip, with min/max/mode published alongside the value."""
from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
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
    async_add_entities([ProbeText(entry)])


class ProbeText(ProbeEntity, TextEntity):
    """Plain text entity: a value between 3 and 32 characters, no pattern."""

    _attr_mode = TextMode.TEXT
    _attr_native_min = 3
    _attr_native_max = 32

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "text_note", "note", FAMILY_CORE)
        self._attr_native_value = "hello probe"
        self._attr_extra_state_attributes["previous_value"] = None

    async def async_set_value(self, value: str) -> None:
        self._attr_extra_state_attributes["previous_value"] = self._attr_native_value
        self._attr_native_value = value
        self.async_write_ha_state()
