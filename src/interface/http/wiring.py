"""Wiring зависимостей HTTP слоя."""

from functools import lru_cache

from src.application.facade.application_facade import ApplicationFacade
from src.infrastructure.di.providers import build_application_facade


@lru_cache(maxsize=1)
def get_facade() -> ApplicationFacade:
    """Возвращает singleton фасада приложения."""

    return build_application_facade()
