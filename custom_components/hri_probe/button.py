"""A button that counts its presses, so a button.press round trip is visible in the attributes."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeButton(entry)])


class ProbeButton(ProbeEntity, ButtonEntity):
    """The state of a button is only a timestamp, so the press count carries the evidence."""

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "button", "button", FAMILY_CORE)
        self._presses = 0
        self._attr_extra_state_attributes["presses"] = 0

    async def async_press(self) -> None:
        self._presses += 1
        self._attr_extra_state_attributes["presses"] = self._presses
        # ButtonEntity stamps the timestamp and writes the state BEFORE calling us,
        # so the new count needs a write of its own.
        self.async_write_ha_state()
