"""A fan that answers every fan command HRI maps: percentage, preset, oscillation and direction."""
from __future__ import annotations

from typing import Any

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeFan(entry)])


class ProbeFan(ProbeEntity, FanEntity):
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.OSCILLATE
        | FanEntityFeature.DIRECTION
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes = ["auto", "sleep", "boost"]
    _attr_speed_count = 4  # makes percentage_step 25

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "fan", "fan", FAMILY_COMFORT)
        self._attr_percentage = 0
        self._attr_preset_mode = None
        self._attr_oscillating = False
        self._attr_current_direction = DIRECTION_FORWARD

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return
        await self.async_set_percentage(50 if percentage is None else percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_set_percentage(0)

    async def async_set_percentage(self, percentage: int) -> None:
        # is_on is "percentage above zero OR a preset set", so only one of the two may be live.
        self._attr_percentage = percentage
        self._attr_preset_mode = None
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode
        self._attr_percentage = None
        self.async_write_ha_state()

    async def async_oscillate(self, oscillating: bool) -> None:
        self._attr_oscillating = oscillating
        self.async_write_ha_state()

    async def async_set_direction(self, direction: str) -> None:
        self._attr_current_direction = direction
        self.async_write_ha_state()
