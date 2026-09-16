"""Probe water heater: set_temperature, set_operation_mode and away mode over MQTT."""
from __future__ import annotations

from typing import Any

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HEAT_PUMP,
    STATE_HIGH_DEMAND,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, STATE_OFF, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeWaterHeater(entry)])


class ProbeWaterHeater(ProbeEntity, WaterHeaterEntity):
    """A tank in Celsius: the operation mode is the entity state."""

    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.AWAY_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 35.0
    _attr_max_temp = 65.0
    _attr_target_temperature_step = 0.5
    _attr_operation_list = [
        STATE_ECO,
        STATE_ELECTRIC,
        STATE_HEAT_PUMP,
        STATE_HIGH_DEMAND,
        STATE_PERFORMANCE,
        STATE_OFF,
    ]

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "water_heater_tank", "tank", FAMILY_COMFORT)
        self._attr_current_temperature = 48.5
        self._attr_target_temperature = 55.0
        self._attr_current_operation = STATE_ECO
        self._attr_is_away_mode_on = False

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self._attr_target_temperature = temperature
            self.async_write_ha_state()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        self._attr_current_operation = operation_mode
        self.async_write_ha_state()

    async def async_turn_away_mode_on(self) -> None:
        self._set_away(True)

    async def async_turn_away_mode_off(self) -> None:
        self._set_away(False)

    def _set_away(self, away: bool) -> None:
        self._attr_is_away_mode_on = away
        self.async_write_ha_state()
