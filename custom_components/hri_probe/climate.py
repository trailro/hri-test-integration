"""A climate entity that accepts every climate command HRI maps: a single target temperature,
a high/low range, and the hvac, preset, fan and swing modes."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity

# hvac_action follows the mode, so setting a mode changes two published values at once.
HVAC_ACTIONS = {
    HVACMode.OFF: HVACAction.OFF,
    HVACMode.HEAT: HVACAction.HEATING,
    HVACMode.COOL: HVACAction.COOLING,
    HVACMode.HEAT_COOL: HVACAction.IDLE,
    HVACMode.AUTO: HVACAction.IDLE,
    HVACMode.DRY: HVACAction.DRYING,
    HVACMode.FAN_ONLY: HVACAction.FAN,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeClimate(entry)])


class ProbeClimate(ProbeEntity, ClimateEntity):
    """Both TARGET_TEMPERATURE and TARGET_TEMPERATURE_RANGE, so either shape of
    climate.set_temperature is accepted."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = list(HVACMode)
    _attr_preset_modes = ["none", "eco", "away", "boost"]
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_swing_modes = ["off", "vertical", "horizontal", "both"]
    _attr_min_temp = 7
    _attr_max_temp = 35
    _attr_target_temperature_step = 0.5
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "climate", "climate", FAMILY_COMFORT)
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_action = HVACAction.HEATING
        self._attr_target_temperature = 21
        self._attr_target_temperature_high = 24
        self._attr_target_temperature_low = 18
        self._attr_current_temperature = 21.5
        self._attr_current_humidity = 45
        self._attr_preset_mode = "none"
        self._attr_fan_mode = "auto"
        self._attr_swing_mode = "off"

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self._attr_target_temperature = temperature
        if (high := kwargs.get(ATTR_TARGET_TEMP_HIGH)) is not None:
            self._attr_target_temperature_high = high
        if (low := kwargs.get(ATTR_TARGET_TEMP_LOW)) is not None:
            self._attr_target_temperature_low = low
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self._attr_hvac_mode = hvac_mode
        self._attr_hvac_action = HVAC_ACTIONS[hvac_mode]
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        self._attr_fan_mode = fan_mode
        self.async_write_ha_state()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        self._attr_swing_mode = swing_mode
        self.async_write_ha_state()
