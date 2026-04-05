"""Базовые сущности и агрегаты домена."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, kw_only=True)
class AggregateRoot:
    """Базовый агрегат с аудитом и версионированием.

    :param aggregate_id: Идентификатор агрегата.
    :type aggregate_id: str
    :param created_at: Дата и время создания.
    :type created_at: datetime
    :param updated_at: Дата и время последнего изменения.
    :type updated_at: datetime
    :param version: Версия агрегата для optimistic locking.
    :type version: int
    """

    aggregate_id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    _events: list[Any] = field(default_factory=list)

    def touch(self, happened_at: datetime) -> None:
        """Обновляет timestamp и версию агрегата.

        :param happened_at: Время изменения.
        :type happened_at: datetime
        """

        self.updated_at = happened_at
        self.version += 1

    def pull_events(self) -> list[Any]:
        """Возвращает и очищает накопленные доменные события.

        :return: Список событий.
        :rtype: list[Any]
        """

        events = list(self._events)
        self._events.clear()
        return events

    def _raise_event(self, event: Any) -> None:
        """Добавляет событие в outbox агрегата.

        :param event: Экземпляр доменного события.
        :type event: Any
        """

        self._events.append(event)
