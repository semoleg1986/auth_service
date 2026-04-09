"""Конфигурация infrastructure слоя."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    """Параметры запуска auth_service."""

    database_url: str
    use_inmemory: bool
    auto_create_schema: bool
    jwt_issuer: str
    jwt_audience: str
    jwt_private_key_pem: str | None
    jwt_public_key_pem: str | None
    jwt_access_ttl_seconds: int
    jwt_refresh_ttl_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        """Собирает настройки из переменных окружения."""

        return cls(
            database_url=os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth_service.db"),
            use_inmemory=os.getenv("AUTH_USE_INMEMORY", "0") == "1",
            auto_create_schema=os.getenv("AUTH_AUTO_CREATE_SCHEMA", "0") == "1",
            jwt_issuer=os.getenv("AUTH_JWT_ISSUER", "auth_service"),
            jwt_audience=os.getenv("AUTH_JWT_AUDIENCE", "platform_clients"),
            jwt_private_key_pem=os.getenv("AUTH_JWT_PRIVATE_KEY_PEM"),
            jwt_public_key_pem=os.getenv("AUTH_JWT_PUBLIC_KEY_PEM"),
            jwt_access_ttl_seconds=int(os.getenv("AUTH_JWT_ACCESS_TTL_SECONDS", "3600")),
            jwt_refresh_ttl_seconds=int(
                os.getenv("AUTH_JWT_REFRESH_TTL_SECONDS", str(60 * 60 * 24 * 30))
            ),
        )
