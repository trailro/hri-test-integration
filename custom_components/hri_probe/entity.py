"""Base class for every hri_probe entity.

Naming rule for the whole integration: `Probe <entry name> <label>`, so the entity id is
`<platform>.probe_<entry name>_<label>` and a test can predict every topic from the entry name.
Unique ids never change between releases: a consuming Home Assistant keeps its customisations.
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .const import DOMAIN, FAMILY_CORE, FAMILY_NAMES, SIGNAL_FLAP, VERSION


def probe_name(entry: ConfigEntry) -> str:
    return str(entry.data.get("name") or entry.title or "probe")


class ProbeEntity(Entity):
    """Common behaviour: stable ids, a device per family, and the flap service."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, entry: ConfigEntry, key: str, label: str, family: str = FAMILY_CORE) -> None:
        self._entry = entry
        self._key = key
        name = probe_name(entry)
        self._attr_name = f"Probe {name} {label}"
        # Home Assistant composes an entity id from area, device and name, so the device below
        # would prefix every id. Setting it here keeps the rule in the docstring; the platform
        # module is named after its domain, which is the domain of the entity it creates.
        self.entity_id = f"{type(self).__module__.rsplit('.', 1)[-1]}.probe_{slugify(name)}_{slugify(label)}"
        self._attr_unique_id = f"{DOMAIN}_{name}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{family}")},
            name=f"{FAMILY_NAMES[family]} ({name})",
            manufacturer="trailro",
            model=f"hri_probe {family}",
            sw_version=VERSION,
        )
        self._attr_extra_state_attributes = {"probe_key": key, "probe_version": VERSION}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_FLAP, self._flap))

    @callback
    def _flap(self, available: bool) -> None:
        """hri_probe.flap: every entity goes unavailable and comes back, so the consuming
        side can be checked for availability handling instead of stale values."""
        self._attr_available = available
        self.async_write_ha_state()
