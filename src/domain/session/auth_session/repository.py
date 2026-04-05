"""Контракт репозитория агрегата AuthSession."""

from __future__ import annotations

from typing import Protocol

from src.domain.session.auth_session.entity import AuthSession


class AuthSessionRepository(Protocol):
    """Порт репозитория сессий."""

    def add(self, session: AuthSession) -> None:
        """Сохраняет новую сессию."""

    def save(self, session: AuthSession) -> None:
        """Обновляет существующую сессию."""

    def get_by_id(self, session_id: str) -> AuthSession | None:
        """Возвращает сессию по идентификатору."""
