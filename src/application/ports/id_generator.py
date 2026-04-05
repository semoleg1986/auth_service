"""Порт генерации идентификаторов."""

from typing import Protocol


class IdGenerator(Protocol):
    """Контракт генератора идентификаторов."""

    def new(self) -> str:
        """Возвращает новый уникальный идентификатор."""
