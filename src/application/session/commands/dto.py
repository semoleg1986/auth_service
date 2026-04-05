"""Команды session use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Команда входа пользователя."""

    email: str
    password: str
    ip: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None


@dataclass(frozen=True, slots=True)
class LogoutCommand:
    """Команда выхода пользователя."""

    session_id: str


@dataclass(frozen=True, slots=True)
class RegisterCommand:
    """Команда регистрации учетной записи."""

    email: str
    password: str
    default_role: str
