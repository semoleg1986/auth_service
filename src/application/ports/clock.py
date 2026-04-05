"""Порт системного времени."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Контракт источника текущего времени."""

    def now(self) -> datetime:
        """Возвращает текущее время в UTC."""
