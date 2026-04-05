"""Доменные события агрегата Account."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AccountRegistered:
    """Событие регистрации учетной записи."""

    account_id: str
    user_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AccountRoleAssigned:
    """Событие назначения роли."""

    account_id: str
    role: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AccountBlocked:
    """Событие блокировки учетной записи."""

    account_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AccountPasswordChanged:
    """Событие смены пароля."""

    account_id: str
    occurred_at: datetime
