"""Команды token use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RefreshCommand:
    """Команда обновления access token по refresh token."""

    refresh_token: str


@dataclass(frozen=True, slots=True)
class RevokeRefreshTokenCommand:
    """Команда отзыва refresh token."""

    token_id: str
