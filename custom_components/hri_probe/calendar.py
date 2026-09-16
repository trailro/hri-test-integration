"""Probe calendar: one event running now (state on) and one later today."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    async_add_entities([ProbeCalendar(entry)])


class ProbeCalendar(ProbeEntity, CalendarEntity):
    """Read-only calendar: the events are rebuilt around the time the entry was set up."""

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "calendar_agenda", "agenda", FAMILY_MEDIA)
        now = dt_util.now()
        self._current = CalendarEvent(
            start=now - timedelta(minutes=15),
            end=now + timedelta(minutes=45),
            summary="Probe window open",
            description="Running while the probe starts up",
            location="HRI test bench",
            uid="probe-current",
        )
        self._upcoming = CalendarEvent(
            start=now + timedelta(hours=3),
            end=now + timedelta(hours=4),
            summary="Probe window next",
            location="HRI test bench",
            uid="probe-upcoming",
        )
        self._attr_extra_state_attributes.update(
            {
                "upcoming_summary": self._upcoming.summary,
                "upcoming_start": self._upcoming.start.isoformat(),
            }
        )

    @property
    def event(self) -> CalendarEvent | None:
        """The event HA turns into the state: the current one while it lasts."""
        now = dt_util.now()
        if self._current.end > now:
            return self._current
        return self._upcoming

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        return [
            event
            for event in (self._current, self._upcoming)
            if event.start < end_date and event.end > start_date
        ]
