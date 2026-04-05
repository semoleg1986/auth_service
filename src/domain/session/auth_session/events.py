"""Доменные события агрегата AuthSession."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SessionStarted:
    """Событие начала сессии."""

    session_id: str
    account_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SessionClosed:
    """Событие закрытия сессии."""

    session_id: str
    occurred_at: datetime
