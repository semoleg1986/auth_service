"""Port for consuming onboarding invites from users_service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ConsumedStudentInvite:
    """Consumed invite data returned by users_service."""

    invite_id: str
    invite_type: str
    user_id: str
    email: str
    roles: list[str]
    consumed_at: datetime

    @property
    def student_user_id(self) -> str:
        """Backward-compatible alias for older student-invite tests."""

        return self.user_id


class StudentInviteConsumer(Protocol):
    """Consumes a single-use onboarding invite token."""

    def consume(self, *, token: str, consumer: str) -> ConsumedStudentInvite:
        """Consumes invite token and returns student identity data."""
