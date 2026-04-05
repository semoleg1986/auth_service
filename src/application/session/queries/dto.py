"""Запросы session use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GetSessionByIdQuery:
    """Запрос сессии по идентификатору."""

    session_id: str
