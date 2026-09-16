"""A probe humidifier, so turn_on/turn_off, humidifier.set_humidity and humidifier.set_mode
can be exercised against reported bounds, modes, a current humidity and an action."""
from __future__ import annotations

from typing import Any

from homeassistant.components.humidifier import (
    MODE_BOOST,
    MODE_ECO,
    MODE_NORMAL,
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeHumidifier(entry)])


class ProbeHumidifier(ProbeEntity, HumidifierEntity):
    """The action follows on/off and the gap between current and target humidity, so every
    command changes something a test can read back."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_available_modes = [MODE_NORMAL, MODE_ECO, MODE_BOOST]
    _attr_min_humidity = 30
    _attr_max_humidity = 80
    _attr_current_humidity = 45
    _attr_target_humidity = 55
    _attr_mode = MODE_NORMAL
    _attr_is_on = False
    _attr_action = HumidifierAction.OFF

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "humidifier", "humidifier", FAMILY_COMFORT)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._update_action()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._update_action()

    async def async_set_humidity(self, humidity: int) -> None:
        self._attr_target_humidity = humidity
        self._update_action()

    async def async_set_mode(self, mode: str) -> None:
        self._attr_mode = mode
        self.async_write_ha_state()

    def _update_action(self) -> None:
        if not self._attr_is_on:
            self._attr_action = HumidifierAction.OFF
        elif self._attr_current_humidity < self._attr_target_humidity:
            self._attr_action = HumidifierAction.HUMIDIFYING
        else:
            self._attr_action = HumidifierAction.IDLE
        self.async_write_ha_state()
