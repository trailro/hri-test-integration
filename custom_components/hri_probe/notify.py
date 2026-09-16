"""A probe notify entity, so notify.send_message can be exercised and the message that
arrived can be read back from the attributes."""
from __future__ import annotations

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeNotify(entry)])


class ProbeNotify(ProbeEntity, NotifyEntity):
    """The state is only the timestamp of the last notification, so the message itself is
    kept in the attributes."""

    _attr_supported_features = NotifyEntityFeature.TITLE

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "notify", "notify", FAMILY_CORE)

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        self._attr_extra_state_attributes.update({"last_message": message, "last_title": title})
        # NotifyEntity records the timestamp and writes the state right after this returns.
