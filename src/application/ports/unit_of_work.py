"""Порт транзакционного Unit of Work."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from src.application.ports.repositories import RepositoryProvider


class UnitOfWork(Protocol):
    """Контракт транзакции для use case обработчиков."""

    @property
    def repositories(self) -> RepositoryProvider:
        """Возвращает набор репозиториев текущей транзакции."""

    def commit(self) -> None:
        """Фиксирует транзакцию."""

    def rollback(self) -> None:
        """Откатывает транзакцию."""


UnitOfWorkFactory = Callable[[], UnitOfWork]
