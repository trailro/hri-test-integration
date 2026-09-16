"""A probe select, so select.select_option can be exercised against a fixed option list."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity

# "eco mode" contains a space, so a round trip that slugifies or splits options fails loudly.
OPTIONS = ["idle", "eco mode", "boost"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeSelect(entry)])


class ProbeSelect(ProbeEntity, SelectEntity):
    """An option that is not in `options` is rejected by SelectEntity before it reaches us."""

    _attr_options = OPTIONS
    _attr_current_option = OPTIONS[0]

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "select", "select", FAMILY_CORE)

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()
