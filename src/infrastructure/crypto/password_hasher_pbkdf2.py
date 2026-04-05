"""PBKDF2-реализация password hasher."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os


class Pbkdf2PasswordHasher:
    """Хэширует пароль через PBKDF2-HMAC-SHA256."""

    def __init__(self, iterations: int = 120_000) -> None:
        self._iterations = iterations

    def hash(self, raw_password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", raw_password.encode("utf-8"), salt, self._iterations
        )
        return (
            f"pbkdf2_sha256${self._iterations}$"
            f"{base64.urlsafe_b64encode(salt).decode()}$"
            f"{base64.urlsafe_b64encode(digest).decode()}"
        )

    def verify(self, raw_password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            salt = base64.urlsafe_b64decode(salt_b64.encode())
            expected = base64.urlsafe_b64decode(digest_b64.encode())
            actual = hashlib.pbkdf2_hmac(
                "sha256", raw_password.encode("utf-8"), salt, int(iterations)
            )
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False
