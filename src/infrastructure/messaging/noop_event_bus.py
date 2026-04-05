"""Заглушка event bus для локального запуска."""

from typing import Any


class NoopEventBus:
    """Не выполняет отправку событий."""

    def publish(self, events: list[Any]) -> None:
        _ = events
