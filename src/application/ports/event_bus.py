"""Порт публикации доменных событий."""

from typing import Any, Protocol


class EventBus(Protocol):
    """Контракт event bus для integration events."""

    def publish(self, events: list[Any]) -> None:
        """Публикует пачку событий."""
