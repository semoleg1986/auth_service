"""Агрегат сессии авторизации."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.errors import InvariantViolationError
from src.domain.session.auth_session.events import SessionClosed, SessionStarted
from src.domain.shared.entity import AggregateRoot
from src.domain.shared.statuses import SessionStatus


@dataclass(slots=True)
class AuthSession(AggregateRoot):
    """Корневой агрегат сессии пользователя."""

    account_id: str
    refresh_token_id: str | None
    status: SessionStatus
    ip: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None

    @classmethod
    def start(
        cls,
        *,
        session_id: str,
        account_id: str,
        now: datetime,
        refresh_token_id: str | None = None,
        ip: str | None = None,
        user_agent_raw: str | None = None,
        device_type: str | None = None,
        os_name: str | None = None,
        os_version: str | None = None,
        browser_name: str | None = None,
        browser_version: str | None = None,
    ) -> "AuthSession":
        """Создает новую активную сессию."""

        session = cls(
            aggregate_id=session_id,
            account_id=account_id,
            refresh_token_id=refresh_token_id,
            status=SessionStatus.ACTIVE,
            ip=ip,
            user_agent_raw=user_agent_raw,
            device_type=device_type,
            os_name=os_name,
            os_version=os_version,
            browser_name=browser_name,
            browser_version=browser_version,
            created_at=now,
            updated_at=now,
        )
        session._raise_event(
            SessionStarted(session_id=session_id, account_id=account_id, occurred_at=now)
        )
        return session

    def attach_refresh_token(self, *, refresh_token_id: str, now: datetime) -> None:
        """Привязывает refresh token к активной сессии."""

        if self.status != SessionStatus.ACTIVE:
            raise InvariantViolationError("Нельзя обновить неактивную сессию.")
        self.refresh_token_id = refresh_token_id
        self.touch(now)

    def close(self, *, now: datetime) -> None:
        """Закрывает сессию пользователя."""

        if self.status == SessionStatus.CLOSED:
            return
        if self.status == SessionStatus.REVOKED:
            raise InvariantViolationError("Отозванную сессию нельзя закрыть повторно.")
        self.status = SessionStatus.CLOSED
        self.touch(now)
        self._raise_event(SessionClosed(session_id=self.aggregate_id, occurred_at=now))

    def revoke(self, *, now: datetime) -> None:
        """Отзывает сессию администратором или системой."""

        if self.status == SessionStatus.REVOKED:
            return
        self.status = SessionStatus.REVOKED
        self.touch(now)
