"""A probe lock that supports OPEN, so lock.lock, lock.unlock and lock.open are all testable."""
from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_SECURITY
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeLock(entry)])


class ProbeLock(ProbeEntity, LockEntity):
    """LockEntity.state derives `open` from is_open before it looks at is_locked
    (lock/__init__.py:268), so both flags are set on every transition."""

    _attr_supported_features = LockEntityFeature.OPEN
    _attr_is_locked = True
    _attr_is_open = False

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "lock", "lock", FAMILY_SECURITY)

    async def async_lock(self, **kwargs: Any) -> None:
        self._set(locked=True, is_open=False)

    async def async_unlock(self, **kwargs: Any) -> None:
        self._set(locked=False, is_open=False)

    async def async_open(self, **kwargs: Any) -> None:
        self._set(locked=False, is_open=True)

    def _set(self, locked: bool, is_open: bool) -> None:
        self._attr_is_locked = locked
        self._attr_is_open = is_open
        self.async_write_ha_state()
