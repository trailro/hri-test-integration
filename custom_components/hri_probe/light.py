"""Two probe lights, so light.turn_on can be exercised with brightness, colour temperature, rgb_color and effect."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    EFFECT_OFF,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_CORE
from .entity import ProbeEntity

EFFECT_LIST = [EFFECT_OFF, "rainbow", "slow pulse"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ProbeColorTempLight(entry), ProbeRgbLight(entry)])


class ProbeLight(ProbeEntity, LightEntity):
    """On/off and brightness, shared by both lights."""

    _attr_is_on = False
    _attr_brightness = 128

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()


class ProbeColorTempLight(ProbeLight):
    """Brightness plus colour temperature."""

    # COLOR_TEMP already implies brightness: adding ColorMode.BRIGHTNESS next to it is
    # rejected by valid_supported_color_modes (light/__init__.py:83).
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_min_color_temp_kelvin = 2200
    _attr_max_color_temp_kelvin = 6500
    _attr_color_temp_kelvin = 3000

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "light", "light", FAMILY_CORE)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._attr_color_temp_kelvin = kwargs[ATTR_COLOR_TEMP_KELVIN]
        await super().async_turn_on(**kwargs)


class ProbeRgbLight(ProbeLight):
    """RGB colour plus an effect list."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = EFFECT_LIST
    _attr_effect = EFFECT_OFF
    _attr_rgb_color = (255, 180, 80)

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "light_rgb", "light_rgb", FAMILY_CORE)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
        if ATTR_EFFECT in kwargs:
            self._attr_effect = kwargs[ATTR_EFFECT]
        await super().async_turn_on(**kwargs)
