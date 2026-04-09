from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain.errors import AccessDeniedError, InvariantViolationError
from src.domain.session.auth_session.entity import AuthSession
from src.domain.session.auth_session.policies import SessionPolicy
from src.domain.token.refresh_token.entity import RefreshToken
from src.domain.token.refresh_token.policies import RefreshTokenPolicy


def _now() -> datetime:
    return datetime(2026, 4, 9, tzinfo=UTC)


def test_session_policy_owner_or_admin() -> None:
    SessionPolicy.ensure_owner_or_admin("acc-1", "acc-1", {"parent"})
    SessionPolicy.ensure_owner_or_admin("admin-1", "acc-1", {"admin"})

    with pytest.raises(AccessDeniedError):
        SessionPolicy.ensure_owner_or_admin("u-2", "u-1", {"teacher"})


def test_refresh_policy_owner_or_admin() -> None:
    RefreshTokenPolicy.ensure_owner_or_admin("acc-1", "acc-1", {"student"})
    RefreshTokenPolicy.ensure_owner_or_admin("admin-1", "acc-1", {"admin"})

    with pytest.raises(AccessDeniedError):
        RefreshTokenPolicy.ensure_owner_or_admin("u-2", "u-1", {"parent"})


def test_auth_session_lifecycle_and_guards() -> None:
    now = _now()
    session = AuthSession.start(
        session_id="s-1",
        account_id="acc-1",
        user_id="user-1",
        now=now,
        ip_address="127.0.0.1",
        user_agent_raw="Mozilla",
    )

    session.attach_refresh_token(refresh_token_id="rt-1", now=now)
    session.mark_seen(now=now, path="/v1/me", action="view", auth_method="refresh")
    session.set_trusted(is_trusted=True, now=now)
    session.set_risk_level(risk_level="high", now=now)
    assert session.is_trusted is True
    assert session.risk_level.value == "high"

    session.revoke(now=now, reason="security")
    assert session.status.value == "revoked"

    with pytest.raises(InvariantViolationError):
        session.close(now=now)

    with pytest.raises(InvariantViolationError):
        session.attach_refresh_token(refresh_token_id="rt-2", now=now)

    with pytest.raises(InvariantViolationError):
        session.mark_seen(now=now)


def test_refresh_token_revoke_idempotent() -> None:
    now = _now()
    token = RefreshToken.issue(
        token_id="rt-1",
        account_id="acc-1",
        session_id="s-1",
        expires_at=now.replace(year=2027),
        now=now,
    )

    token.revoke(now=now)
    assert token.status.value == "revoked"

    # Повторный revoke допустим и не падает.
    token.revoke(now=now)
    assert token.status.value == "revoked"
