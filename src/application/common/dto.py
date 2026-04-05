"""Общие DTO application слоя."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TokenResult:
    """Результат выдачи токенов."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True, slots=True)
class MeResult:
    """Профиль текущего пользователя."""

    account_id: str
    user_id: str
    email: str
    roles: list[str]
    status: str


@dataclass(frozen=True, slots=True)
class SessionInfoResult:
    """Информация о пользовательской сессии."""

    session_id: str
    user_id: str
    account_id: str
    status: str
    auth_method: str
    mfa_used: bool
    is_trusted: bool
    risk_level: str
    session_fingerprint: str
    request_count: int
    created_at: datetime
    last_seen_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    revoke_reason: str | None
    ip_address: str | None
    user_agent_raw: str | None
    device_type: str | None
    os_name: str | None
    os_version: str | None
    browser_name: str | None
    browser_version: str | None
    client_name: str | None
    country: str | None
    city: str | None
    last_path: str | None
    last_action: str | None
