"""Probe switch: the simplest round trip, switch.turn_on / switch.turn_off arriving over MQTT."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
    async_add_entities([ProbeSwitch(entry)])


class ProbeSwitch(ProbeEntity, SwitchEntity):
    """A switch that starts off and counts how many commands reached it."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "switch_main", "main", FAMILY_CORE)
        self._attr_is_on = False
        self._attr_extra_state_attributes["command_count"] = 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._apply(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._apply(False)

    def _apply(self, is_on: bool) -> None:
        self._attr_is_on = is_on
        self._attr_extra_state_attributes["command_count"] += 1
        self.async_write_ha_state()
