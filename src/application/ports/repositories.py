"""Порты репозиториев application слоя."""

from __future__ import annotations

from typing import Protocol

from src.domain.identity.account.repository import AccountRepository
from src.domain.session.auth_session.repository import AuthSessionRepository
from src.domain.token.refresh_token.repository import RefreshTokenRepository


class RepositoryProvider(Protocol):
    """Контейнер доступа к репозиториям внутри транзакции."""

    @property
    def accounts(self) -> AccountRepository:
        """Репозиторий аккаунтов."""

    @property
    def sessions(self) -> AuthSessionRepository:
        """Репозиторий сессий."""

    @property
    def refresh_tokens(self) -> RefreshTokenRepository:
        """Репозиторий refresh token."""
