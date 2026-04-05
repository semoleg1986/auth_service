"""Агрегат refresh token."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.errors import InvariantViolationError
from src.domain.shared.entity import AggregateRoot
from src.domain.shared.statuses import RefreshTokenStatus
from src.domain.token.refresh_token.events import (
    RefreshTokenIssued,
    RefreshTokenRevoked,
    RefreshTokenRotated,
)


@dataclass(slots=True)
class RefreshToken(AggregateRoot):
    """Корневой агрегат refresh token."""

    account_id: str
    session_id: str
    expires_at: datetime
    status: RefreshTokenStatus
    replaced_by_token_id: str | None = None

    @classmethod
    def issue(
        cls,
        *,
        token_id: str,
        account_id: str,
        session_id: str,
        expires_at: datetime,
        now: datetime,
    ) -> "RefreshToken":
        """Выпускает новый refresh token."""

        token = cls(
            aggregate_id=token_id,
            account_id=account_id,
            session_id=session_id,
            expires_at=expires_at,
            status=RefreshTokenStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        token._raise_event(
            RefreshTokenIssued(token_id=token_id, account_id=account_id, occurred_at=now)
        )
        return token

    def ensure_usable(self, *, now: datetime) -> None:
        """Проверяет, что токен активен и не истек."""

        if self.status != RefreshTokenStatus.ACTIVE:
            raise InvariantViolationError("Refresh token не активен.")
        if now >= self.expires_at:
            raise InvariantViolationError("Refresh token истек.")

    def rotate(self, *, new_token_id: str, now: datetime) -> None:
        """Переводит токен в состояние rotated."""

        self.ensure_usable(now=now)
        self.status = RefreshTokenStatus.ROTATED
        self.replaced_by_token_id = new_token_id
        self.touch(now)
        self._raise_event(
            RefreshTokenRotated(
                old_token_id=self.aggregate_id,
                new_token_id=new_token_id,
                occurred_at=now,
            )
        )

    def revoke(self, *, now: datetime) -> None:
        """Отзывает refresh token."""

        if self.status == RefreshTokenStatus.REVOKED:
            return
        self.status = RefreshTokenStatus.REVOKED
        self.touch(now)
        self._raise_event(RefreshTokenRevoked(token_id=self.aggregate_id, occurred_at=now))
