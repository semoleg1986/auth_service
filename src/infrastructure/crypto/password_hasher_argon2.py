"""Argon2-реализация password hasher."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Argon2PasswordHasher:
    """Хэширует пароль через Argon2id."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, raw_password: str) -> str:
        return self._hasher.hash(raw_password)

    def verify(self, raw_password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, raw_password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False

