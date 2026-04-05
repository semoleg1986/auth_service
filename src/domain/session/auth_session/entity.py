"""Агрегат сессии авторизации."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib

from src.domain.errors import InvariantViolationError
from src.domain.session.auth_session.events import SessionClosed, SessionStarted
from src.domain.shared.entity import AggregateRoot
from src.domain.shared.statuses import AuthMethod, DeviceType, RiskLevel, SessionStatus


@dataclass(slots=True)
class AuthSession(AggregateRoot):
    """Корневой агрегат сессии пользователя."""

    account_id: str
    user_id: str
    refresh_token_id: str | None
    status: SessionStatus
    ip_address: str | None = None
    user_agent_raw: str | None = None
    device_type: DeviceType = DeviceType.UNKNOWN
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None
    client_name: str | None = None
    country: str | None = None
    city: str | None = None
    auth_method: AuthMethod = AuthMethod.PASSWORD
    mfa_used: bool = False
    is_trusted: bool = False
    risk_level: RiskLevel = RiskLevel.MEDIUM
    session_fingerprint: str = ""
    request_count: int = 1
    last_path: str | None = None
    last_action: str | None = None
    last_seen_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    revoke_reason: str | None = None

    @classmethod
    def start(
        cls,
        *,
        session_id: str,
        account_id: str,
        user_id: str,
        now: datetime,
        refresh_token_id: str | None = None,
        ip_address: str | None = None,
        user_agent_raw: str | None = None,
        device_type: str | None = None,
        os_name: str | None = None,
        os_version: str | None = None,
        browser_name: str | None = None,
        browser_version: str | None = None,
        client_name: str | None = None,
        country: str | None = None,
        city: str | None = None,
        auth_method: str = "password",
        mfa_used: bool = False,
        is_trusted: bool = False,
        risk_level: str = "medium",
        session_fingerprint: str | None = None,
        last_path: str | None = None,
        last_action: str | None = None,
        expires_at: datetime | None = None,
    ) -> "AuthSession":
        """Создает новую активную сессию."""

        session = cls(
            aggregate_id=session_id,
            account_id=account_id,
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            status=SessionStatus.ACTIVE,
            ip_address=ip_address,
            user_agent_raw=user_agent_raw,
            device_type=DeviceType(device_type) if device_type else DeviceType.UNKNOWN,
            os_name=os_name,
            os_version=os_version,
            browser_name=browser_name,
            browser_version=browser_version,
            client_name=client_name or browser_name,
            country=country,
            city=city,
            auth_method=AuthMethod(auth_method),
            mfa_used=mfa_used,
            is_trusted=is_trusted,
            risk_level=RiskLevel(risk_level),
            session_fingerprint=session_fingerprint
            or cls._build_fingerprint(
                ip_address=ip_address,
                user_agent_raw=user_agent_raw,
                os_name=os_name,
                browser_name=browser_name,
            ),
            request_count=1,
            last_path=last_path,
            last_action=last_action,
            last_seen_at=now,
            expires_at=expires_at,
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

    def mark_seen(
        self,
        *,
        now: datetime,
        path: str | None = None,
        action: str | None = None,
        auth_method: str | None = None,
    ) -> None:
        """Обновляет активность сессии."""

        if self.status != SessionStatus.ACTIVE:
            raise InvariantViolationError("Нельзя обновить неактивную сессию.")
        self.request_count += 1
        self.last_seen_at = now
        self.last_path = path or self.last_path
        self.last_action = action or self.last_action
        if auth_method:
            self.auth_method = AuthMethod(auth_method)
        self.touch(now)

    def set_trusted(self, *, is_trusted: bool, now: datetime) -> None:
        """Изменяет признак доверенности устройства."""

        self.is_trusted = is_trusted
        self.touch(now)

    def set_risk_level(self, *, risk_level: str, now: datetime) -> None:
        """Изменяет уровень риска сессии."""

        self.risk_level = RiskLevel(risk_level)
        self.touch(now)

    def close(self, *, now: datetime) -> None:
        """Закрывает сессию пользователя."""

        if self.status == SessionStatus.CLOSED:
            return
        if self.status == SessionStatus.REVOKED:
            raise InvariantViolationError("Отозванную сессию нельзя закрыть повторно.")
        self.status = SessionStatus.CLOSED
        self.last_seen_at = now
        self.touch(now)
        self._raise_event(SessionClosed(session_id=self.aggregate_id, occurred_at=now))

    def revoke(self, *, now: datetime, reason: str | None = None) -> None:
        """Отзывает сессию администратором или системой."""

        if self.status == SessionStatus.REVOKED:
            return
        self.status = SessionStatus.REVOKED
        self.revoked_at = now
        self.revoke_reason = reason
        self.last_seen_at = now
        self.touch(now)

    @staticmethod
    def _build_fingerprint(
        *,
        ip_address: str | None,
        user_agent_raw: str | None,
        os_name: str | None,
        browser_name: str | None,
    ) -> str:
        """Строит стабильный хэш-отпечаток клиента."""

        raw = "|".join(
            [
                ip_address or "",
                user_agent_raw or "",
                os_name or "",
                browser_name or "",
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
