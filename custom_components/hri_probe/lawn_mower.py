"""A probe lawn mower, so lawn_mower.start_mowing, lawn_mower.pause and lawn_mower.dock
each move the entity to a different activity."""
from __future__ import annotations

from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeLawnMower(entry)])


class ProbeLawnMower(ProbeEntity, LawnMowerEntity):
    """The state is the activity itself (lawn_mower/__init__.py:90)."""

    _attr_supported_features = (
        LawnMowerEntityFeature.START_MOWING
        | LawnMowerEntityFeature.PAUSE
        | LawnMowerEntityFeature.DOCK
    )
    _attr_activity = LawnMowerActivity.DOCKED

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "lawn_mower", "lawn_mower", FAMILY_COMFORT)

    async def async_start_mowing(self) -> None:
        self._set(LawnMowerActivity.MOWING)

    async def async_pause(self) -> None:
        self._set(LawnMowerActivity.PAUSED)

    async def async_dock(self) -> None:
        self._set(LawnMowerActivity.DOCKED)

    def _set(self, activity: LawnMowerActivity) -> None:
        self._attr_activity = activity
        self.async_write_ha_state()
