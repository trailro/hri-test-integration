"""A probe siren, so siren.turn_on can be exercised with a tone, a duration and a volume level."""
from __future__ import annotations

from typing import Any

from homeassistant.components.siren import (
    ATTR_DURATION,
    ATTR_TONE,
    ATTR_VOLUME_LEVEL,
    SirenEntity,
    SirenEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_SECURITY
from .entity import ProbeEntity

# "slow whoop" contains a space; a tone outside this list is rejected by the siren
# component before async_turn_on is reached (siren/__init__.py:70).
TONES = ["alarm", "chime", "slow whoop"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeSiren(entry)])


class ProbeSiren(ProbeEntity, SirenEntity):
    """The turn_on parameters are echoed into the attributes, so a test can read back
    what actually arrived."""

    _attr_supported_features = (
        SirenEntityFeature.TURN_ON
        | SirenEntityFeature.TURN_OFF
        | SirenEntityFeature.TONES
        | SirenEntityFeature.DURATION
        | SirenEntityFeature.VOLUME_SET
    )
    _attr_available_tones = TONES
    _attr_is_on = False

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "siren", "siren", FAMILY_SECURITY)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._attr_extra_state_attributes.update(
            {
                "last_tone": kwargs.get(ATTR_TONE),
                "last_duration": kwargs.get(ATTR_DURATION),
                "last_volume_level": kwargs.get(ATTR_VOLUME_LEVEL),
            }
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
