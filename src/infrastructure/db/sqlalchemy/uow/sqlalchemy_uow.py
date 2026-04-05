"""SQLAlchemy UnitOfWork для auth_service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from src.application.ports.repositories import RepositoryProvider
from src.infrastructure.db.sqlalchemy.repositories.account_repository_sqlalchemy import (
    SqlalchemyAccountRepository,
)
from src.infrastructure.db.sqlalchemy.repositories.refresh_token_repository_sqlalchemy import (
    SqlalchemyRefreshTokenRepository,
)
from src.infrastructure.db.sqlalchemy.repositories.session_repository_sqlalchemy import (
    SqlalchemySessionRepository,
)


@dataclass(slots=True)
class SqlalchemyRepositoryProvider(RepositoryProvider):
    """Провайдер SQLAlchemy-репозиториев."""

    accounts: SqlalchemyAccountRepository
    sessions: SqlalchemySessionRepository
    refresh_tokens: SqlalchemyRefreshTokenRepository


class SqlalchemyUnitOfWork:
    """Транзакционная обертка SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session = session_factory()
        self._repositories = SqlalchemyRepositoryProvider(
            accounts=SqlalchemyAccountRepository(self._session),
            sessions=SqlalchemySessionRepository(self._session),
            refresh_tokens=SqlalchemyRefreshTokenRepository(self._session),
        )

    @property
    def repositories(self) -> SqlalchemyRepositoryProvider:
        return self._repositories

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()
