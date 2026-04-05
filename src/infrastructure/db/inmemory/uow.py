"""In-memory UnitOfWork auth_service."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.ports.repositories import RepositoryProvider
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)


@dataclass(slots=True)
class InMemoryRepositoryProvider(RepositoryProvider):
    """Провайдер in-memory репозиториев."""

    accounts: InMemoryAccountRepository
    sessions: InMemorySessionRepository
    refresh_tokens: InMemoryRefreshTokenRepository


class InMemoryUnitOfWork:
    """Простейшая транзакционная оболочка для локальной разработки."""

    def __init__(self, repositories: InMemoryRepositoryProvider) -> None:
        self._repositories = repositories

    @property
    def repositories(self) -> InMemoryRepositoryProvider:
        return self._repositories

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None
