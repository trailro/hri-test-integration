"""Probe image: a tiny generated PNG whose timestamp state changes on every refresh."""
from __future__ import annotations

import struct
import zlib

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import FAMILY_MEDIA
from .entity import ProbeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeImage(hass, entry)])


def _solid_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Build a solid colour PNG in memory: a few dozen bytes, no file and no dependency."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8 bit truecolour
    scanlines = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(scanlines))
        + chunk(b"IEND", b"")
    )


BADGE_IMAGE = _solid_png(16, 16, (16, 185, 129))


class ProbeImage(ProbeEntity, ImageEntity):
    """The image state is image_last_updated, so it only changes when the bytes do."""

    _attr_content_type = "image/png"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        ProbeEntity.__init__(self, entry, "image_badge", "badge", FAMILY_MEDIA)
        ImageEntity.__init__(self, hass)  # ImageEntity needs hass for its http client
        self._attr_extra_state_attributes["image_bytes"] = len(BADGE_IMAGE)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._attr_image_last_updated = dt_util.utcnow()

    async def async_image(self) -> bytes | None:
        return BADGE_IMAGE
