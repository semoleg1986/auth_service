"""Настройка пути импорта для тестов."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from src.interface.http.common.rate_limit import reset_rate_limiter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def force_inmemory_for_non_integration(request: pytest.FixtureRequest) -> None:
    """Фиксирует in-memory режим для обычных тестов, не затрагивая integration."""

    if request.node.get_closest_marker("integration"):
        return

    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ.pop("AUTH_DATABASE_URL", None)
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    # Тесты не должны зависеть от внешних PEM ключей окружения.
    os.environ.pop("AUTH_JWT_PRIVATE_KEY_PEM", None)
    os.environ.pop("AUTH_JWT_PUBLIC_KEY_PEM", None)
    reset_rate_limiter()
