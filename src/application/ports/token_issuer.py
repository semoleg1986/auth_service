"""Порт выпуска и проверки токенов."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AccessTokenPayload:
    """Полезная нагрузка access token."""

    sub: str
    jti: str
    roles: list[str]
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class TokenPair:
    """Пара access/refresh токенов."""

    access_token: str
    refresh_token: str


class TokenIssuer(Protocol):
    """Контракт токен-провайдера."""

    def issue_pair(self, payload: AccessTokenPayload, refresh_claims: dict[str, str]) -> TokenPair:
        """Выпускает пару access/refresh токенов."""

    def decode_refresh(self, refresh_token: str) -> dict[str, str]:
        """Декодирует refresh token до набора claims."""

    def decode_access(self, access_token: str) -> dict[str, str | list[str]]:
        """Декодирует access token до набора claims."""

    def jwks(self) -> dict:
        """Возвращает публичный JWKS документ."""
