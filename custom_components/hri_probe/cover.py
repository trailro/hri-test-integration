"""Two covers, one with position and tilt and one tilt only, so both cover command shapes are
testable. Movement is instant: a test can assert the end state without waiting for steps."""
from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_COMFORT
from .entity import ProbeEntity

POSITION_FEATURES = (
    CoverEntityFeature.OPEN
    | CoverEntityFeature.CLOSE
    | CoverEntityFeature.STOP
    | CoverEntityFeature.SET_POSITION
)
TILT_FEATURES = (
    CoverEntityFeature.OPEN_TILT
    | CoverEntityFeature.CLOSE_TILT
    | CoverEntityFeature.STOP_TILT
    | CoverEntityFeature.SET_TILT_POSITION
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(
        [
            ProbeCover(entry, "cover", "cover", POSITION_FEATURES | TILT_FEATURES),
            ProbeCover(entry, "cover_tilt", "cover_tilt", TILT_FEATURES),
        ]
    )


class ProbeCover(ProbeEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.SHUTTER

    def __init__(
        self, entry: ConfigEntry, key: str, label: str, features: CoverEntityFeature
    ) -> None:
        super().__init__(entry, key, label, FAMILY_COMFORT)
        self._attr_supported_features = features
        if CoverEntityFeature.SET_POSITION in features:
            self._attr_current_cover_position = 0
        if CoverEntityFeature.SET_TILT_POSITION in features:
            self._attr_current_cover_tilt_position = 0

    @property
    def is_closed(self) -> bool:
        """A tilt only cover has no position, so its tilt decides whether it counts as closed."""
        if self._attr_current_cover_position is not None:
            return self._attr_current_cover_position == 0
        return self._attr_current_cover_tilt_position == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        self._move(100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        self._move(0)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        self._move(kwargs[ATTR_POSITION])

    async def async_stop_cover(self, **kwargs: Any) -> None:
        # Movement is instant, so there is never anything to interrupt: the call only has to
        # succeed and republish where the cover already is.
        self.async_write_ha_state()

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        self._move_tilt(100)

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        self._move_tilt(0)

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        self._move_tilt(kwargs[ATTR_TILT_POSITION])

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        self.async_write_ha_state()

    @callback
    def _move(self, position: int) -> None:
        self._attr_current_cover_position = position
        self.async_write_ha_state()

    @callback
    def _move_tilt(self, tilt_position: int) -> None:
        self._attr_current_cover_tilt_position = tilt_position
        self.async_write_ha_state()
