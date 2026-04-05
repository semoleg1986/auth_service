"""Контракт репозитория агрегата RefreshToken."""

from __future__ import annotations

from typing import Protocol

from src.domain.token.refresh_token.entity import RefreshToken


class RefreshTokenRepository(Protocol):
    """Порт репозитория refresh token."""

    def add(self, token: RefreshToken) -> None:
        """Сохраняет новый токен."""

    def save(self, token: RefreshToken) -> None:
        """Обновляет существующий токен."""

    def get_by_id(self, token_id: str) -> RefreshToken | None:
        """Возвращает токен по идентификатору."""
