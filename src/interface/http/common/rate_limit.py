"""Простой in-memory rate limiter для HTTP endpoints."""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass

from fastapi import HTTPException


@dataclass(frozen=True, slots=True)
class RateLimitRule:
    """Правило rate-limit: не больше `max_requests` за `window_seconds`."""

    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    """Потокобезопасный sliding-window limiter."""

    def __init__(self, now: Callable[[], float] | None = None) -> None:
        self._now = now or time.monotonic
        self._events: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, scope: str, key: str, rule: RateLimitRule) -> bool:
        """Проверяет и учитывает запрос."""

        now = self._now()
        boundary = now - float(rule.window_seconds)
        token = (scope, key)

        with self._lock:
            bucket = self._events[token]
            while bucket and bucket[0] <= boundary:
                bucket.popleft()
            if len(bucket) >= rule.max_requests:
                return False
            bucket.append(now)
            return True

    def reset(self) -> None:
        """Очищает состояние limiter (для тестов)."""

        with self._lock:
            self._events.clear()


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


LOGIN_RATE_RULE = RateLimitRule(
    max_requests=_int_env("AUTH_RATE_LIMIT_LOGIN_MAX", 10),
    window_seconds=_int_env("AUTH_RATE_LIMIT_LOGIN_WINDOW_SECONDS", 60),
)
REFRESH_RATE_RULE = RateLimitRule(
    max_requests=_int_env("AUTH_RATE_LIMIT_REFRESH_MAX", 20),
    window_seconds=_int_env("AUTH_RATE_LIMIT_REFRESH_WINDOW_SECONDS", 60),
)

_limiter = InMemoryRateLimiter()


def enforce_rate_limit(*, scope: str, key: str, rule: RateLimitRule) -> None:
    """Бросает 429, если лимит превышен."""

    if _limiter.allow(scope=scope, key=key, rule=rule):
        return
    raise HTTPException(
        status_code=429, detail="Слишком много запросов, попробуйте позже."
    )


def reset_rate_limiter() -> None:
    """Сбрасывает глобальный limiter."""

    _limiter.reset()
