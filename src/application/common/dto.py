"""Общие DTO application слоя."""

from dataclasses import dataclass


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
