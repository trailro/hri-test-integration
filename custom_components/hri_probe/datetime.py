"""A datetime entity that keeps whatever datetime.set_value sends it, timezone included."""
from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.components.datetime import DateTimeEntity
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
    async_add_entities([ProbeDateTime(entry)])


class ProbeDateTime(ProbeEntity, DateTimeEntity):
    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "datetime", "datetime", FAMILY_CORE)
        self._attr_native_value = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    async def async_set_value(self, value: datetime) -> None:
        # The component has already made a naive value timezone aware before calling us.
        self._attr_native_value = value
        self.async_write_ha_state()
