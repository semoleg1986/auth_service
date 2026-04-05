"""Доменные события агрегата RefreshToken."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RefreshTokenIssued:
    """Событие выдачи refresh token."""

    token_id: str
    account_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshTokenRotated:
    """Событие ротации refresh token."""

    old_token_id: str
    new_token_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshTokenRevoked:
    """Событие отзыва refresh token."""

    token_id: str
    occurred_at: datetime
