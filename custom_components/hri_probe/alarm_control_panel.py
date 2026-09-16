"""An alarm panel guarded by code 1234, so every arm and disarm command carries a code."""
from __future__ import annotations

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import FAMILY_SECURITY
from .entity import ProbeEntity

CODE = "1234"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ProbeAlarm(entry)])


class ProbeAlarm(ProbeEntity, AlarmControlPanelEntity):
    """States change instantly: no arming or pending delay, so a test can assert straight away."""

    _attr_code_format = CodeFormat.NUMBER
    _attr_code_arm_required = True
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
        | AlarmControlPanelEntityFeature.ARM_VACATION
        | AlarmControlPanelEntityFeature.ARM_CUSTOM_BYPASS
        | AlarmControlPanelEntityFeature.TRIGGER
    )

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "alarm_control_panel", "alarm", FAMILY_SECURITY)
        self._attr_alarm_state = AlarmControlPanelState.DISARMED

    @callback
    def _set(
        self, state: AlarmControlPanelState, code: str | None, *, code_required: bool = True
    ) -> None:
        # Home Assistant only checks that a code was supplied (check_code_arm_required);
        # comparing it against the real one is the integration's job.
        if code_required and code != CODE:
            raise ServiceValidationError(f"Wrong code for {self.entity_id}")
        self._attr_alarm_state = state
        self._attr_changed_by = "hri_probe"
        self.async_write_ha_state()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.DISARMED, code)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.ARMED_HOME, code)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.ARMED_AWAY, code)

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.ARMED_NIGHT, code)

    async def async_alarm_arm_vacation(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.ARMED_VACATION, code)

    async def async_alarm_arm_custom_bypass(self, code: str | None = None) -> None:
        self._set(AlarmControlPanelState.ARMED_CUSTOM_BYPASS, code)

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        # Like a real panel, triggering is not code protected: a siren button has no keypad.
        self._set(AlarmControlPanelState.TRIGGERED, code, code_required=False)
