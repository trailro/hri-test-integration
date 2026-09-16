"""Probe update: update.install with a visible progress ramp and a backup flag to assert on."""
from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity

INSTALL_STEPS = 5
STEP_DELAY = 0.2


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeUpdate(entry)])


class ProbeUpdate(ProbeEntity, UpdateEntity):
    """An update that is always pending, so install can be called again and again."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL
        | UpdateEntityFeature.BACKUP
        | UpdateEntityFeature.PROGRESS
    )
    _attr_title = "HRI Probe firmware"
    _attr_release_summary = "Probe firmware with every platform enabled."
    _attr_release_url = "https://github.com/trailro/hri-test-integration/releases"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "update_firmware", "firmware", FAMILY_CORE)
        self._attr_installed_version = "6.0.0"
        self._attr_latest_version = "6.1.0"
        self._attr_extra_state_attributes["last_install_backup"] = None

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        self._attr_extra_state_attributes["last_install_backup"] = backup
        self._attr_in_progress = True
        for step in range(INSTALL_STEPS):
            self._attr_update_percentage = round(step * 100 / INSTALL_STEPS)
            self.async_write_ha_state()
            await asyncio.sleep(STEP_DELAY)

        self._attr_in_progress = False
        self._attr_update_percentage = None
        self._attr_installed_version = version or self._attr_latest_version
        # Keep offering a newer build so the entity never settles on "up to date".
        self._attr_latest_version = _bump(self._attr_installed_version)
        self.async_write_ha_state()


def _bump(version: str) -> str:
    major, minor, _patch = version.split(".")
    return f"{major}.{int(minor) + 1}.0"
