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
    status: str
    created_at: datetime
    updated_at: datetime
    ip: str | None
    user_agent_raw: str | None
    device_type: str | None
    os_name: str | None
    os_version: str | None
    browser_name: str | None
    browser_version: str | None
