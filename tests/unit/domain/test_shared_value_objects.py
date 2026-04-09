from __future__ import annotations

import pytest

from src.domain.errors import ValidationError
from src.domain.shared.value_objects import Email, PasswordHash, Role


def test_email_password_hash_and_role_validation() -> None:
    assert Email("  USER@EXAMPLE.COM ").value == "user@example.com"

    with pytest.raises(ValidationError):
        Email("bad-email")

    with pytest.raises(ValidationError):
        PasswordHash("   ")

    assert Role(" Teacher ").value == "teacher"
    with pytest.raises(ValidationError):
        Role("unknown")
