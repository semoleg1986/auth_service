from datetime import UTC, datetime

import pytest

from src.domain.errors import AccessDeniedError, InvariantViolationError, ValidationError
from src.domain.identity.account.entity import Account
from src.domain.identity.account.policies import AccountPolicy
from src.domain.identity.account.value_objects import UserAgent
from src.domain.shared.statuses import AccountStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role


def _now() -> datetime:
    return datetime(2026, 4, 9, tzinfo=UTC)


def _account() -> Account:
    return Account.register(
        account_id="acc-1",
        user_id="user-1",
        email=Email("user@example.com"),
        password_hash=PasswordHash("hash"),
        default_role=Role("parent"),
        now=_now(),
    )


def test_account_register_and_events() -> None:
    account = _account()
    events = account.pull_events()
    assert len(events) == 1
    assert events[0].account_id == "acc-1"


def test_assign_revoke_roles_and_last_role_guard() -> None:
    account = _account()
    now = _now()
    account.assign_role(role=Role("student"), now=now)
    assert {role.value for role in account.roles} == {"parent", "student"}

    account.revoke_role(role=Role("student"), now=now)
    assert {role.value for role in account.roles} == {"parent"}

    with pytest.raises(InvariantViolationError):
        account.revoke_role(role=Role("parent"), now=now)


def test_account_password_and_status_lifecycle() -> None:
    account = _account()
    now = _now()

    account.block(now=now)
    assert account.status == AccountStatus.BLOCKED

    account.unblock(now=now)
    assert account.status == AccountStatus.ACTIVE

    account.change_password(password_hash=PasswordHash("new-hash"), now=now)
    assert account.password_hash.value == "new-hash"

    account.archive(now=now)
    assert account.status == AccountStatus.ARCHIVED

    with pytest.raises(InvariantViolationError):
        account.change_password(password_hash=PasswordHash("x"), now=now)


def test_account_policies_and_user_agent_vo() -> None:
    AccountPolicy.ensure_admin({"admin"})
    with pytest.raises(AccessDeniedError):
        AccountPolicy.ensure_admin({"teacher"})

    AccountPolicy.ensure_self_or_admin("u-1", "u-1", {"parent"})
    AccountPolicy.ensure_self_or_admin("u-2", "u-1", {"admin"})
    with pytest.raises(AccessDeniedError):
        AccountPolicy.ensure_self_or_admin("u-2", "u-1", {"parent"})

    ua = UserAgent("Mozilla/5.0")
    assert ua.value == "Mozilla/5.0"
    with pytest.raises(ValidationError):
        UserAgent("   ")
