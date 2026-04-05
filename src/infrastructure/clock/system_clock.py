"""Системные часы infrastructure слоя."""

from datetime import UTC, datetime


class SystemClock:
    """Возвращает текущее UTC-время."""

    def now(self) -> datetime:
        return datetime.now(UTC)
