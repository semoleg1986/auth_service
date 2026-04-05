"""Совместимые экспорты DI-провайдеров.

Основной composition root находится в `src.infrastructure.di.composition`.
"""

from src.infrastructure.di.composition import (  # noqa: F401
    RuntimeContainer,
    build_application_facade,
    build_runtime,
)
