"""Probe vacuum: every vacuum service, with the last send_command kept as an attribute."""
from __future__ import annotations

from typing import Any

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity

FAN_SPEEDS = ["quiet", "standard", "turbo"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeVacuum(entry)])


class ProbeVacuum(ProbeEntity, StateVacuumEntity):
    """Docked at startup; every service moves it to a different activity."""

    _attr_supported_features = (
        VacuumEntityFeature.STATE
        | VacuumEntityFeature.START
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.CLEAN_SPOT
        | VacuumEntityFeature.LOCATE
        | VacuumEntityFeature.FAN_SPEED
        | VacuumEntityFeature.SEND_COMMAND
    )
    _attr_fan_speed_list = FAN_SPEEDS

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "vacuum_bot", "bot", FAMILY_COMFORT)
        self._attr_activity = VacuumActivity.DOCKED
        self._attr_fan_speed = FAN_SPEEDS[1]
        self._attr_extra_state_attributes.update(
            {"last_service": None, "last_command": None, "last_command_params": None}
        )

    async def async_start(self) -> None:
        self._apply("start", VacuumActivity.CLEANING)

    async def async_pause(self) -> None:
        self._apply("pause", VacuumActivity.PAUSED)

    async def async_stop(self, **kwargs: Any) -> None:
        self._apply("stop", VacuumActivity.IDLE)

    async def async_return_to_base(self, **kwargs: Any) -> None:
        self._apply("return_to_base", VacuumActivity.RETURNING)

    async def async_clean_spot(self, **kwargs: Any) -> None:
        self._apply("clean_spot", VacuumActivity.CLEANING)

    async def async_locate(self, **kwargs: Any) -> None:
        # Locate only beeps on a real vacuum, so the activity deliberately stays put.
        self._apply("locate", self._attr_activity)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        self._attr_fan_speed = fan_speed
        self._apply("set_fan_speed", self._attr_activity)

    async def async_send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._attr_extra_state_attributes["last_command"] = command
        self._attr_extra_state_attributes["last_command_params"] = params
        self._apply("send_command", self._attr_activity)

    def _apply(self, service: str, activity: VacuumActivity | None) -> None:
        self._attr_extra_state_attributes["last_service"] = service
        self._attr_activity = activity
        self.async_write_ha_state()
