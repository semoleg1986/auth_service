"""Перечисления статусов домена auth_service."""

from enum import StrEnum


class AccountStatus(StrEnum):
    """Статус учетной записи."""

    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class SessionStatus(StrEnum):
    """Статус сессии авторизации."""

    ACTIVE = "active"
    CLOSED = "closed"
    REVOKED = "revoked"


class RefreshTokenStatus(StrEnum):
    """Статус refresh token."""

    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"
    EXPIRED = "expired"


class DeviceType(StrEnum):
    """Тип клиентского устройства."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    BOT = "bot"
    UNKNOWN = "unknown"


class AuthMethod(StrEnum):
    """Метод аутентификации/подтверждения сессии."""

    PASSWORD = "password"
    REFRESH = "refresh"
    OAUTH = "oauth"
    MAGIC_LINK = "magic_link"


class RiskLevel(StrEnum):
    """Уровень риска сессии."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
