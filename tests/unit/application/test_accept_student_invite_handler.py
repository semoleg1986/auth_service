from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from src.application.ports.student_invite_consumer import ConsumedStudentInvite
from src.application.session.commands.dto import AcceptStudentInviteCommand
from src.application.session.handlers.accept_student_invite_handler import (
    AcceptStudentInviteHandler,
)
from src.domain.errors import InvariantViolationError
from src.domain.identity.account.entity import Account
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.crypto.jwt_token_issuer_eddsa import JwtEdDsaTokenIssuer
from src.infrastructure.crypto.password_hasher_argon2 import Argon2PasswordHasher
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from src.infrastructure.db.inmemory.uow import (
    InMemoryRepositoryProvider,
    InMemoryUnitOfWork,
)
from src.infrastructure.id.uuid_generator import UuidGenerator


@dataclass(slots=True)
class _FakeInviteConsumer:
    invite: ConsumedStudentInvite

    def consume(self, *, token: str, consumer: str) -> ConsumedStudentInvite:
        assert token == "invite-token-123456"
        assert consumer == "auth_service"
        return self.invite


class _Ctx:
    def __init__(self) -> None:
        self.clock = SystemClock()
        self.id_generator = UuidGenerator()
        self.password_hasher = Argon2PasswordHasher()
        self.token_issuer = JwtEdDsaTokenIssuer(issuer="auth_service_test")
        repos = InMemoryRepositoryProvider(
            accounts=InMemoryAccountRepository(),
            sessions=InMemorySessionRepository(),
            refresh_tokens=InMemoryRefreshTokenRepository(),
        )
        self.uow = InMemoryUnitOfWork(repos)
        self.invite = ConsumedStudentInvite(
            invite_id="invite-1",
            parent_user_id="parent-user-1",
            student_user_id="student-user-1",
            email="student@example.com",
            consumed_at=datetime.now(timezone.utc),
        )

    def handler(self) -> AcceptStudentInviteHandler:
        return AcceptStudentInviteHandler(
            uow_factory=lambda: self.uow,
            clock=self.clock,
            id_generator=self.id_generator,
            password_hasher=self.password_hasher,
            invite_consumer=_FakeInviteConsumer(self.invite),
            token_issuer=self.token_issuer,
            access_ttl_seconds=3600,
            refresh_ttl_seconds=60 * 60 * 24,
        )


def test_accept_student_invite_creates_account_with_existing_student_user_id() -> None:
    ctx = _Ctx()

    result = ctx.handler()(
        AcceptStudentInviteCommand(
            token="invite-token-123456",
            password="student-pass-123",
        )
    )

    user = result["user"]
    assert isinstance(user, dict)
    account = ctx.uow.repositories.accounts.get_by_id(str(user["account_id"]))
    assert account is not None
    assert account.user_id == "student-user-1"
    assert account.email.value == "student@example.com"
    assert {role.value for role in account.roles} == {"student"}
    assert ctx.password_hasher.verify("student-pass-123", account.password_hash.value)
    assert result["token_type"] == "Bearer"
    assert result["access_token"]
    assert result["refresh_token"]
    claims = ctx.token_issuer.decode_access(str(result["access_token"]))
    assert claims["sub"] == account.aggregate_id
    assert claims["user_id"] == "student-user-1"
    assert claims["roles"] == ["student"]
    refresh_claims = ctx.token_issuer.decode_refresh(str(result["refresh_token"]))
    session = ctx.uow.repositories.sessions.get_by_id(refresh_claims["session_id"])
    refresh = ctx.uow.repositories.refresh_tokens.get_by_id(refresh_claims["token_id"])
    assert session is not None
    assert refresh is not None


def test_accept_student_invite_rejects_existing_student_user_id() -> None:
    ctx = _Ctx()
    now = ctx.clock.now()
    existing = Account.register(
        account_id="account-1",
        user_id="student-user-1",
        email=Email("other@example.com"),
        password_hash=PasswordHash(ctx.password_hasher.hash("student-pass-123")),
        default_role=Role("student"),
        now=now,
    )
    ctx.uow.repositories.accounts.add(existing)

    with pytest.raises(InvariantViolationError, match="student уже существует"):
        ctx.handler()(
            AcceptStudentInviteCommand(
                token="invite-token-123456",
                password="student-pass-123",
            )
        )
