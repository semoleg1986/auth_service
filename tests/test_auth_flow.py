from src.application.session.commands.dto import LoginCommand, LogoutCommand, RegisterCommand
from src.application.session.handlers.login_handler import LoginHandler
from src.application.session.handlers.logout_handler import LogoutHandler
from src.application.session.handlers.register_handler import RegisterHandler
from src.application.token.commands.dto import RefreshCommand
from src.application.token.handlers.refresh_handler import RefreshHandler
from src.domain.identity.account.entity import Account
from src.domain.shared.statuses import SessionStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role
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


def test_register_and_login_and_me_flow() -> None:
    ctx = _Ctx()
    register = RegisterHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        password_hasher=ctx.password_hasher,
    )
    login = LoginHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        password_hasher=ctx.password_hasher,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=60 * 60 * 24,
    )

    created = register(
        RegisterCommand(
            email="parent@example.com",
            password="strong-pass-123",
            default_role="parent",
        )
    )
    tokens = login(
        LoginCommand(email="parent@example.com", password="strong-pass-123")
    )

    claims = ctx.token_issuer.decode_access(tokens.access_token)
    assert claims["sub"] == created["account_id"]


def test_refresh_rotates_token_and_logout_closes_session() -> None:
    ctx = _Ctx()
    now = ctx.clock.now()
    account = Account.register(
        account_id=ctx.id_generator.new(),
        user_id=ctx.id_generator.new(),
        email=Email("admin@example.com"),
        password_hash=PasswordHash(ctx.password_hasher.hash("admin12345")),
        default_role=Role("admin"),
        now=now,
    )
    ctx.uow.repositories.accounts.add(account)

    login = LoginHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        password_hasher=ctx.password_hasher,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=60 * 60 * 24,
    )
    refresh = RefreshHandler(
        uow=ctx.uow,
        clock=ctx.clock,
        id_generator=ctx.id_generator,
        token_issuer=ctx.token_issuer,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=60 * 60 * 24,
    )
    logout = LogoutHandler(uow=ctx.uow, clock=ctx.clock)

    first = login(LoginCommand(email="admin@example.com", password="admin12345"))
    first_refresh_claims = ctx.token_issuer.decode_refresh(first.refresh_token)

    second = refresh(RefreshCommand(refresh_token=first.refresh_token))
    second_refresh_claims = ctx.token_issuer.decode_refresh(second.refresh_token)

    assert second.refresh_token != first.refresh_token
    assert second_refresh_claims["token_id"] != first_refresh_claims["token_id"]

    logout(LogoutCommand(session_id=second_refresh_claims["session_id"]))
    session = ctx.uow.repositories.sessions.get_by_id(second_refresh_claims["session_id"])
    assert session is not None
    assert session.status == SessionStatus.CLOSED
