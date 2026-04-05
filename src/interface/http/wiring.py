"""Wiring зависимостей HTTP слоя."""

from functools import lru_cache

from src.application.facade.application_facade import ApplicationFacade
from src.application.ports.token_issuer import TokenIssuer
from src.infrastructure.di.providers import RuntimeContainer, build_runtime


@lru_cache(maxsize=1)
def get_runtime() -> RuntimeContainer:
    """Возвращает singleton runtime-контейнера."""

    return build_runtime()


def get_facade() -> ApplicationFacade:
    """Возвращает singleton фасада приложения."""

    return get_runtime().facade


def get_token_issuer() -> TokenIssuer:
    """Возвращает singleton token issuer."""

    return get_runtime().token_issuer
