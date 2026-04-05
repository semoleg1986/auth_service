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


    @classmethod
    def from_env(cls) -> "Settings":
        """Собирает настройки из переменных окружения."""

        return cls(
            database_url=os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth_service.db"),
            use_inmemory=os.getenv("AUTH_USE_INMEMORY", "0") == "1",
            auto_create_schema=os.getenv("AUTH_AUTO_CREATE_SCHEMA", "0") == "1",
        )
