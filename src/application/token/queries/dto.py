"""Запросы token use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GetRefreshTokenByIdQuery:
    """Запрос refresh token по идентификатору."""

    token_id: str
