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
