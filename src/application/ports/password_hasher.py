"""Порт хэширования и проверки пароля."""

from typing import Protocol


class PasswordHasher(Protocol):
    """Контракт крипто-адаптера для паролей."""

    def hash(self, raw_password: str) -> str:
        """Возвращает криптостойкий хэш пароля."""

    def verify(self, raw_password: str, password_hash: str) -> bool:
        """Проверяет соответствие пароля его хэшу."""
