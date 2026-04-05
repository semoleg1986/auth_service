"""Команды session use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Команда входа пользователя."""

    email: str
    password: str
    ip_address: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None
    client_name: str | None = None
    country: str | None = None
    city: str | None = None
    auth_method: str = "password"
    mfa_used: bool = False
    is_trusted: bool = False
    risk_level: str = "medium"
    session_fingerprint: str | None = None
    last_path: str | None = "/v1/auth/login"
    last_action: str | None = "login"


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
