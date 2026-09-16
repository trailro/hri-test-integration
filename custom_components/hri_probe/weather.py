"""Probe weather: current conditions plus a daily forecast served through the forecast API."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SUNNY,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import FAMILY_MEDIA
from .entity import ProbeEntity

# condition, high, low, precipitation probability
DAILY = [
    (ATTR_CONDITION_PARTLYCLOUDY, 23.0, 12.0, 10),
    (ATTR_CONDITION_RAINY, 19.0, 11.0, 80),
    (ATTR_CONDITION_SUNNY, 25.0, 13.0, 0),
    (ATTR_CONDITION_CLOUDY, 21.0, 12.0, 20),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeWeather(entry)])


class ProbeWeather(ProbeEntity, WeatherEntity):
    """The condition is the state; every measurement is published in native units."""

    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_condition = ATTR_CONDITION_PARTLYCLOUDY
    _attr_native_temperature = 21.5
    _attr_native_apparent_temperature = 20.8
    _attr_native_dew_point = 11.2
    _attr_humidity = 47
    _attr_native_pressure = 1013.2
    _attr_native_wind_speed = 11.5
    _attr_native_wind_gust_speed = 24.0
    _attr_wind_bearing = 220

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "weather_local", "local", FAMILY_MEDIA)
        # HA no longer exposes the forecast as a state attribute, so a read-only mirror
        # would otherwise see none of it: publish a compact copy for the mirror to carry.
        self._attr_extra_state_attributes["forecast_preview"] = [
            {"condition": condition, "temperature": high, "templow": low}
            for condition, high, low, _ in DAILY
        ]

    async def async_forecast_daily(self) -> list[Forecast]:
        start = dt_util.start_of_local_day()
        return [
            Forecast(
                datetime=(start + timedelta(days=day)).isoformat(),
                condition=condition,
                native_temperature=high,
                native_templow=low,
                precipitation_probability=probability,
            )
            for day, (condition, high, low, probability) in enumerate(DAILY)
        ]
