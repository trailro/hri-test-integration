"""Four probe sensors covering the shapes discovery treats differently: numeric, enum,
timestamp, and one that goes unknown; the numeric and the flaky one follow hri_probe.tick."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import FAMILY_CORE, SIGNAL_TICK
from .entity import ProbeEntity

MODES = ["idle", "heating", "cooling"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities(
        [
            ProbePowerSensor(entry),
            ProbeModeSensor(entry),
            ProbeTimestampSensor(entry),
            ProbeFlakySensor(entry),
        ]
    )


class ProbeSensor(ProbeEntity, SensorEntity):
    """A sensor with a fixed value: no service and no tick can change it."""


class ProbeTickingSensor(ProbeSensor):
    """A sensor driven by hri_probe.tick, since sensors have no service of their own."""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_TICK, self._on_tick))

    @callback
    def _on_tick(self, n: int) -> None:
        self._attr_native_value = self._value_for(n)
        self.async_write_ha_state()

    def _value_for(self, n: int) -> object:
        raise NotImplementedError


class ProbePowerSensor(ProbeTickingSensor):
    """Numeric: device class, state class and a unit, so statistics apply on the other side."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_value = 100

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "sensor_power", "sensor_power", FAMILY_CORE)

    def _value_for(self, n: int) -> object:
        return 100 + (n % 20) * 5


class ProbeFlakySensor(ProbeTickingSensor):
    """Goes unknown on every third tick, so a stale value on the other side is visible."""

    _attr_native_value = 0

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "sensor_flaky", "sensor_flaky", FAMILY_CORE)

    def _value_for(self, n: int) -> object:
        return None if n % 3 == 0 else n


class ProbeModeSensor(ProbeSensor):
    """Enum: SensorEntity rejects a unit or a state class here, and any value outside
    `options` (sensor/__init__.py:709)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = MODES
    _attr_native_value = MODES[0]

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "sensor_mode", "sensor_mode", FAMILY_CORE)


class ProbeTimestampSensor(ProbeSensor):
    """Timestamp: the value must be a timezone-aware datetime (sensor/__init__.py:663)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "sensor_timestamp", "sensor_timestamp", FAMILY_CORE)
        self._attr_native_value = dt_util.utcnow()
