"""A probe scene, so scene.turn_on can be exercised: the only state is the activation timestamp."""
from __future__ import annotations

from typing import Any

from homeassistant.components.scene import Scene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeScene(entry)])


class ProbeScene(ProbeEntity, Scene):
    """Scene._async_activate stamps the timestamp and writes the state before calling us
    (scene/__init__.py:150), so there is nothing left to apply."""

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "scene", "scene", FAMILY_CORE)

    async def async_activate(self, **kwargs: Any) -> None:
        """No devices behind this scene: activation only has to succeed."""
