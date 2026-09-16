"""Probe to-do list: three seeded items and the full to-do item API (create/update/delete/move)."""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
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
    async_add_entities([ProbeTodoList(entry)])


class ProbeTodoList(ProbeEntity, TodoListEntity):
    """The state is the number of items still needing action, counted by HA itself."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.MOVE_TODO_ITEM
        | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
    )

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "todo_list", "list", FAMILY_MEDIA)
        today = dt_util.now().date()
        self._attr_todo_items = [
            TodoItem(
                summary="Check the MQTT bridge",
                uid=uuid4().hex,
                status=TodoItemStatus.NEEDS_ACTION,
                due=today + timedelta(days=1),
                description="Seeded by hri_probe",
            ),
            TodoItem(
                summary="Publish the mirrors",
                uid=uuid4().hex,
                status=TodoItemStatus.NEEDS_ACTION,
            ),
            TodoItem(
                summary="Read the probe device page",
                uid=uuid4().hex,
                status=TodoItemStatus.COMPLETED,
            ),
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        item.uid = uuid4().hex  # HA leaves uid assignment to the integration
        self._items().append(item)
        self.async_write_ha_state()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        items = self._items()
        for index, existing in enumerate(items):
            if existing.uid == item.uid:
                items[index] = item
                break
        self.async_write_ha_state()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        self._attr_todo_items = [i for i in self._items() if i.uid not in uids]
        self.async_write_ha_state()

    async def async_move_todo_item(self, uid: str, previous_uid: str | None = None) -> None:
        items = self._items()
        moved = next(i for i in items if i.uid == uid)
        items.remove(moved)
        target = 0
        if previous_uid is not None:
            target = next(i for i, item in enumerate(items) if item.uid == previous_uid) + 1
        items.insert(target, moved)
        self.async_write_ha_state()

    def _items(self) -> list[TodoItem]:
        assert self._attr_todo_items is not None
        return self._attr_todo_items
