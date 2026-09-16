"""Probe time: time.set_value round trip, so a time payload can be checked end to end."""
from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
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
    async_add_entities([ProbeTime(entry)])


class ProbeTime(ProbeEntity, TimeEntity):
    """A wake-up time that any client may rewrite."""

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "time_alarm", "alarm", FAMILY_CORE)
        self._attr_native_value = time(7, 30)

    async def async_set_value(self, value: time) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
