"""Probe valves: one reporting a position and one not, so both valve state shapes are covered."""
from __future__ import annotations

from homeassistant.components.valve import ValveEntity, ValveEntityFeature
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
    async_add_entities([ProbePositionValve(entry), ProbePlainValve(entry)])


class ProbePositionValve(ProbeEntity, ValveEntity):
    """Position reporting valve: state and is_closed are derived from current_position."""

    _attr_reports_position = True
    _attr_supported_features = (
        ValveEntityFeature.OPEN
        | ValveEntityFeature.CLOSE
        | ValveEntityFeature.SET_POSITION
        | ValveEntityFeature.STOP
    )

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "valve_position", "position", FAMILY_COMFORT)
        self._attr_current_valve_position = 0
        self._attr_is_opening = False
        self._attr_is_closing = False
        self._attr_extra_state_attributes["last_service"] = None

    # open_valve / close_valve are never called on this entity: because SET_POSITION is
    # supported, HA rewrites both services into async_set_valve_position(100 / 0).
    async def async_set_valve_position(self, position: int) -> None:
        self._attr_current_valve_position = position
        self._apply("set_valve_position")

    async def async_stop_valve(self) -> None:
        # Moves are instant here, so stop only has to leave a valid position behind.
        self._apply("stop_valve")

    def _apply(self, service: str) -> None:
        self._attr_extra_state_attributes["last_service"] = service
        self.async_write_ha_state()


class ProbePlainValve(ProbeEntity, ValveEntity):
    """Positionless valve: state comes from is_closed only, never from a position."""

    _attr_reports_position = False
    _attr_supported_features = (
        ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE | ValveEntityFeature.STOP
    )

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "valve_plain", "plain", FAMILY_COMFORT)
        self._attr_is_closed = True
        self._attr_is_opening = False
        self._attr_is_closing = False
        self._attr_extra_state_attributes["last_service"] = None

    async def async_open_valve(self) -> None:
        self._attr_is_closed = False
        self._apply("open_valve")

    async def async_close_valve(self) -> None:
        self._attr_is_closed = True
        self._apply("close_valve")

    async def async_stop_valve(self) -> None:
        # Without a position there is no half-open state to freeze, so stop keeps the
        # current is_closed rather than leaving the entity with an unknown state.
        self._attr_is_opening = False
        self._attr_is_closing = False
        self._apply("stop_valve")

    def _apply(self, service: str) -> None:
        self._attr_extra_state_attributes["last_service"] = service
        self.async_write_ha_state()
