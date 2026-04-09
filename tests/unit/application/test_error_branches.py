from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.identity.handlers.get_me_handler import GetMeHandler
from src.application.identity.queries.dto import GetMeQuery
from src.application.ports.token_issuer import AccessTokenPayload
from src.application.session.commands.dto import LoginCommand
from src.application.session.handlers.login_handler import LoginHandler
from src.application.token.commands.dto import RefreshCommand
from src.application.token.handlers.refresh_handler import RefreshHandler
from src.domain.errors import AccessDeniedError, NotFoundError
from src.domain.identity.account.entity import Account
from src.domain.session.auth_session.entity import AuthSession
from src.domain.shared.statuses import AccountStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.domain.token.refresh_token.entity import RefreshToken
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.crypto.jwt_token_issuer_eddsa import JwtEdDsaTokenIssuer
from src.infrastructure.crypto.password_hasher_argon2 import Argon2PasswordHasher
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from src.infrastructure.db.inmemory.uow import InMemoryRepositoryProvider, InMemoryUnitOfWork
from src.infrastructure.id.uuid_generator import UuidGenerator


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


def _create_account(ctx: _Ctx, *, status: AccountStatus = AccountStatus.ACTIVE) -> Account:
    now = datetime(2026, 4, 9, tzinfo=UTC)
    account = Account.register(
        account_id=ctx.id_generator.new(),
        user_id=ctx.id_generator.new(),
        email=Email("user@example.com"),
        password_hash=PasswordHash(ctx.password_hasher.hash("pass-12345")),
        default_role=Role("parent"),
        now=now,
    )
    if status == AccountStatus.BLOCKED:
        account.block(now=now)
    ctx.uow.repositories.accounts.add(account)
    return account


def test_get_me_raises_not_found_for_unknown_account() -> None:
    ctx = _Ctx()
    handler = GetMeHandler(uow=ctx.uow)

    with pytest.raises(NotFoundError):
        handler(GetMeQuery(account_id="missing"))


def test_login_rejects_missing_account_or_wrong_password_or_blocked() -> None:
    ctx = _Ctx()
    handler = LoginHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        password_hasher=ctx.password_hasher,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )

    with pytest.raises(AccessDeniedError):
        handler(LoginCommand(email="none@example.com", password="x"))

    _create_account(ctx)
    with pytest.raises(AccessDeniedError):
        handler(LoginCommand(email="user@example.com", password="wrong"))

    ctx_blocked = _Ctx()
    _create_account(ctx_blocked, status=AccountStatus.BLOCKED)
    blocked_handler = LoginHandler(
        uow=ctx_blocked.uow,
        clock=ctx_blocked.clock,
        id_generator=ctx_blocked.id_generator,
        password_hasher=ctx_blocked.password_hasher,
        token_issuer=ctx_blocked.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )
    with pytest.raises(AccessDeniedError):
        blocked_handler(LoginCommand(email="user@example.com", password="pass-12345"))


def test_refresh_rejects_missing_claims_and_missing_entities() -> None:
    ctx = _Ctx()
    refresh = RefreshHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )

    bogus = ctx.token_issuer.issue_pair(
        payload=type("P", (), {
            "sub": "acc",
            "jti": "jti",
            "roles": ["parent"],
            "issued_at": datetime.now(UTC),
            "expires_at": datetime.now(UTC),
        })(),
        refresh_claims={"account_id": "acc", "session_id": "sess"},
    )
    with pytest.raises(AccessDeniedError):
        refresh(RefreshCommand(refresh_token=bogus.refresh_token))

    proper = ctx.token_issuer.issue_pair(
        payload=type("P", (), {
            "sub": "acc",
            "jti": "jti2",
            "roles": ["parent"],
            "issued_at": datetime.now(UTC),
            "expires_at": datetime.now(UTC),
        })(),
        refresh_claims={"token_id": "missing-rt", "account_id": "acc", "session_id": "sess"},
    )
    with pytest.raises(NotFoundError):
        refresh(RefreshCommand(refresh_token=proper.refresh_token))


def test_refresh_rejects_when_account_missing_or_blocked_or_session_missing() -> None:
    ctx = _Ctx()
    now = datetime.now(UTC)
    refresh = RefreshHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )

    payload = AccessTokenPayload(
        sub="acc-x",
        jti="jti-x",
        roles=["parent"],
        issued_at=now,
        expires_at=now,
    )

    # account missing
    missing_acc_rt = RefreshToken.issue(
        token_id="rt-missing-acc",
        account_id="acc-missing",
        session_id="sess-1",
        expires_at=now.replace(year=2027),
        now=now,
    )
    ctx.uow.repositories.refresh_tokens.add(missing_acc_rt)
    token_missing_acc = ctx.token_issuer.issue_pair(
        payload=payload,
        refresh_claims={
            "token_id": "rt-missing-acc",
            "account_id": "acc-missing",
            "session_id": "sess-1",
        },
    )
    with pytest.raises(NotFoundError):
        refresh(RefreshCommand(refresh_token=token_missing_acc.refresh_token))

    # blocked account
    blocked = _create_account(ctx, status=AccountStatus.BLOCKED)
    sess_blocked = AuthSession.start(
        session_id="sess-blocked",
        account_id=blocked.aggregate_id,
        user_id=blocked.user_id,
        now=now,
    )
    ctx.uow.repositories.sessions.add(sess_blocked)
    rt_blocked = RefreshToken.issue(
        token_id="rt-blocked",
        account_id=blocked.aggregate_id,
        session_id=sess_blocked.aggregate_id,
        expires_at=now.replace(year=2027),
        now=now,
    )
    ctx.uow.repositories.refresh_tokens.add(rt_blocked)
    token_blocked = ctx.token_issuer.issue_pair(
        payload=payload,
        refresh_claims={
            "token_id": "rt-blocked",
            "account_id": blocked.aggregate_id,
            "session_id": sess_blocked.aggregate_id,
        },
    )
    with pytest.raises(AccessDeniedError):
        refresh(RefreshCommand(refresh_token=token_blocked.refresh_token))

    # session missing
    active = _create_account(ctx, status=AccountStatus.ACTIVE)
    rt_missing_session = RefreshToken.issue(
        token_id="rt-no-session",
        account_id=active.aggregate_id,
        session_id="sess-missing",
        expires_at=now.replace(year=2027),
        now=now,
    )
    ctx.uow.repositories.refresh_tokens.add(rt_missing_session)
    token_missing_session = ctx.token_issuer.issue_pair(
        payload=payload,
        refresh_claims={
            "token_id": "rt-no-session",
            "account_id": active.aggregate_id,
            "session_id": "sess-missing",
        },
    )
    with pytest.raises(NotFoundError):
        refresh(RefreshCommand(refresh_token=token_missing_session.refresh_token))
