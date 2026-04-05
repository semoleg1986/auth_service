"""In-memory репозитории auth_service."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.identity.account.entity import Account
from src.domain.session.auth_session.entity import AuthSession
from src.domain.token.refresh_token.entity import RefreshToken


@dataclass(slots=True)
class InMemoryAccountRepository:
    """In-memory репозиторий аккаунтов."""

    by_id: dict[str, Account] = field(default_factory=dict)
    by_email: dict[str, str] = field(default_factory=dict)

    def add(self, account: Account) -> None:
        self.by_id[account.aggregate_id] = account
        self.by_email[account.email.value] = account.aggregate_id

    def save(self, account: Account) -> None:
        self.add(account)

    def get_by_id(self, account_id: str) -> Account | None:
        return self.by_id.get(account_id)

    def get_by_email(self, email: str) -> Account | None:
        account_id = self.by_email.get(email.strip().lower())
        return self.by_id.get(account_id) if account_id else None


@dataclass(slots=True)
class InMemorySessionRepository:
    """In-memory репозиторий сессий."""

    by_id: dict[str, AuthSession] = field(default_factory=dict)

    def add(self, session: AuthSession) -> None:
        self.by_id[session.aggregate_id] = session

    def save(self, session: AuthSession) -> None:
        self.by_id[session.aggregate_id] = session

    def get_by_id(self, session_id: str) -> AuthSession | None:
        return self.by_id.get(session_id)


@dataclass(slots=True)
class InMemoryRefreshTokenRepository:
    """In-memory репозиторий refresh token."""

    by_id: dict[str, RefreshToken] = field(default_factory=dict)

    def add(self, token: RefreshToken) -> None:
        self.by_id[token.aggregate_id] = token

    def save(self, token: RefreshToken) -> None:
        self.by_id[token.aggregate_id] = token

    def get_by_id(self, token_id: str) -> RefreshToken | None:
        return self.by_id.get(token_id)
