"""Запросы identity use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GetAccountByIdQuery:
    """Запрос аккаунта по идентификатору."""

    account_id: str


@dataclass(frozen=True, slots=True)
class GetMeQuery:
    """Запрос профиля текущего пользователя."""

    account_id: str
