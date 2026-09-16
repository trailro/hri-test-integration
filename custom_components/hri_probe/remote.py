"""Probe remote: on/off plus remote.send_command, whose last command stays readable."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_MEDIA
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeRemote(entry)])


class ProbeRemote(ProbeEntity, RemoteEntity):
    """remote.send_command needs no feature flag, so the plain entity already accepts it."""

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "remote_hub", "hub", FAMILY_MEDIA)
        self._attr_is_on = True
        self._attr_extra_state_attributes.update({"last_command": None, "command_count": 0})

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        commands = list(command)
        self._attr_extra_state_attributes["last_command"] = commands[-1] if commands else None
        self._attr_extra_state_attributes["command_count"] += len(commands)
        self.async_write_ha_state()
