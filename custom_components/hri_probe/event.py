"""An event entity fired from hri_probe.tick: exercises event_types and the last event payload."""
from __future__ import annotations

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE, SIGNAL_TICK
from .entity import ProbeEntity

EVENT_TYPES = ["single", "double", "hold"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeEvent(entry)])


class ProbeEvent(ProbeEntity, EventEntity):
    """Each tick fires the next event type, so a consumer sees all three in order."""

    _attr_device_class = EventDeviceClass.BUTTON
    _attr_event_types = EVENT_TYPES

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "event", "event", FAMILY_CORE)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_TICK, self._tick))

    @callback
    def _tick(self, n: int) -> None:
        self._trigger_event(EVENT_TYPES[n % len(EVENT_TYPES)], {"tick": n})
        self.async_write_ha_state()
