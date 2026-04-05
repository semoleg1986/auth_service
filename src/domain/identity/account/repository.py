"""Контракт репозитория агрегата Account."""

from __future__ import annotations

from typing import Protocol

from src.domain.identity.account.entity import Account


class AccountRepository(Protocol):
    """Порт репозитория для хранения и загрузки Account."""

    def add(self, account: Account) -> None:
        """Сохраняет новый аккаунт."""

    def save(self, account: Account) -> None:
        """Обновляет существующий аккаунт."""

    def get_by_id(self, account_id: str) -> Account | None:
        """Возвращает аккаунт по идентификатору."""

    def get_by_email(self, email: str) -> Account | None:
        """Возвращает аккаунт по email."""
