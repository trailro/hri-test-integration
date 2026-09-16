"""Probe media player: playing track with full media metadata, plus the usual local services."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import FAMILY_MEDIA
from .entity import ProbeEntity

SOURCES = ["spotify", "radio", "line in"]
TRACKS = [
    ("Rondo alla Turca", "Wolfgang Amadeus Mozart", 214),
    ("Clair de Lune", "Claude Debussy", 302),
    ("Gymnopedie No.1", "Erik Satie", 209),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeMediaPlayer(entry)])


class ProbeMediaPlayer(ProbeEntity, MediaPlayerEntity):
    """Starts playing, so the mirror on the other side has a state worth reading."""

    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.SEEK
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )
    _attr_media_content_type = MediaType.MUSIC
    _attr_source_list = SOURCES

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "media_player_deck", "deck", FAMILY_MEDIA)
        self._track = 0
        self._attr_state = MediaPlayerState.PLAYING
        self._attr_volume_level = 0.4
        self._attr_is_volume_muted = False
        self._attr_source = SOURCES[0]
        self._attr_media_album_name = "Probe playlist"
        self._attr_media_position = 42
        self._load_track(0)

    def _load_track(self, index: int) -> None:
        title, artist, duration = TRACKS[index % len(TRACKS)]
        self._track = index % len(TRACKS)
        self._attr_media_title = title
        self._attr_media_artist = artist
        self._attr_media_duration = duration
        self._attr_media_content_id = f"probe://track/{self._track}"
        self._attr_media_position_updated_at = dt_util.utcnow()

    async def async_turn_on(self) -> None:
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        self._attr_state = MediaPlayerState.PLAYING
        self._attr_media_position_updated_at = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        self._attr_state = MediaPlayerState.PAUSED
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        self._attr_state = MediaPlayerState.IDLE
        self._attr_media_position = 0
        self.async_write_ha_state()

    async def async_media_next_track(self) -> None:
        self._skip(1)

    async def async_media_previous_track(self) -> None:
        self._skip(-1)

    def _skip(self, step: int) -> None:
        self._load_track(self._track + step)
        self._attr_media_position = 0
        self.async_write_ha_state()

    async def async_media_seek(self, position: float) -> None:
        self._attr_media_position = int(position)
        self._attr_media_position_updated_at = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        self._attr_volume_level = volume
        self.async_write_ha_state()

    async def async_mute_volume(self, mute: bool) -> None:
        self._attr_is_volume_muted = mute
        self.async_write_ha_state()

    async def async_select_source(self, source: str) -> None:
        self._attr_source = source
        self.async_write_ha_state()
