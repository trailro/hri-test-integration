"""A GPS tracker that walks away from home on every hri_probe tick.

TrackerEntity, not ScannerEntity: a ScannerEntity forces unique_id to be the MAC address and
its device_info to None, which neither a config entry platform nor ProbeEntity can satisfy.
"""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_SECURITY, SIGNAL_TICK
from .entity import ProbeEntity

STEP = 0.0005  # ~55 m per tick, so the tracker leaves the home zone after a few ticks


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeDeviceTracker(entry)])


class ProbeDeviceTracker(ProbeEntity, TrackerEntity):
    """Ten positions on a straight line out of the home zone, then back to the start."""

    _attr_source_type = SourceType.GPS

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "device_tracker", "tracker", FAMILY_SECURITY)
        self._attr_location_accuracy = 10  # published as the gps_accuracy state attribute
        self._home = (0.0, 0.0)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # hass is only available now, and the walk has to start from this instance's own home.
        self._home = (self.hass.config.latitude, self.hass.config.longitude)
        self._move(0)
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_TICK, self._tick))

    @callback
    def _tick(self, n: int) -> None:
        self._move(n)
        self.async_write_ha_state()

    @callback
    def _move(self, n: int) -> None:
        offset = (n % 10) * STEP
        self._attr_latitude = self._home[0] + offset
        self._attr_longitude = self._home[1] + offset
