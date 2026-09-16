"""Probe camera: a generated still image, no stream and no network, for the camera mirror."""
from __future__ import annotations

import struct
import zlib

from homeassistant.components.camera import Camera, CameraEntityFeature
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
    async_add_entities([ProbeCamera(entry)])


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


STILL_IMAGE = _solid_png(32, 32, (10, 132, 255))


class ProbeCamera(ProbeEntity, Camera):
    """Still-only camera: supported_features stays empty so HA never asks for a stream."""

    _attr_supported_features = CameraEntityFeature(0)
    _attr_is_streaming = False

    def __init__(self, entry: ConfigEntry) -> None:
        ProbeEntity.__init__(self, entry, "camera_still", "still", FAMILY_MEDIA)
        Camera.__init__(self)
        self.content_type = "image/png"
        self._attr_extra_state_attributes.update(
            {"still_source": "generated", "still_bytes": len(STILL_IMAGE)}
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes:
        return STILL_IMAGE
