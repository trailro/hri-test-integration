"""A motion binary sensor that flips on every hri_probe tick: the read-only state path."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE, SIGNAL_PULSE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeBinarySensor(entry)])


class ProbeBinarySensor(ProbeEntity, BinarySensorEntity):
    """No service can change a binary sensor, so hri_probe.tick is the only way to move it:
    it toggles once per call, so any count moves it, not only an odd one."""

    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "binary_sensor", "motion", FAMILY_CORE)
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_PULSE, self._tick))

    @callback
    def _tick(self) -> None:
        self._attr_is_on = not self._attr_is_on
        self.async_write_ha_state()
