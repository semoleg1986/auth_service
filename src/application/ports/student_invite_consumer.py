"""Port for consuming student invites from users_service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ConsumedStudentInvite:
    """Consumed invite data returned by users_service."""

    invite_id: str
    parent_user_id: str
    student_user_id: str
    email: str
    consumed_at: datetime


class StudentInviteConsumer(Protocol):
    """Consumes a single-use student invite token."""

    def consume(self, *, token: str, consumer: str) -> ConsumedStudentInvite:
        """Consumes invite token and returns student identity data."""
