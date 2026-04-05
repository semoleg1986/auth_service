"""DI-провайдеры auth_service."""

from __future__ import annotations

from src.application.facade.application_facade import ApplicationFacade
from src.application.identity.handlers.get_me_handler import GetMeHandler
from src.application.identity.queries.dto import GetMeQuery
from src.application.session.commands.dto import LoginCommand, LogoutCommand, RegisterCommand
from src.application.session.handlers.login_handler import LoginHandler
from src.application.session.handlers.logout_handler import LogoutHandler
from src.application.session.handlers.register_handler import RegisterHandler
from src.application.token.commands.dto import RefreshCommand
from src.application.token.handlers.refresh_handler import RefreshHandler
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.crypto.jwt_token_issuer_hs256 import JwtHs256TokenIssuer
from src.infrastructure.crypto.password_hasher_pbkdf2 import Pbkdf2PasswordHasher
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from src.infrastructure.db.inmemory.uow import InMemoryRepositoryProvider, InMemoryUnitOfWork
from src.infrastructure.id.uuid_generator import UuidGenerator
from src.domain.identity.account.entity import Account
from src.domain.shared.value_objects import Email, PasswordHash, Role


def build_application_facade() -> ApplicationFacade:
    """Собирает фасад приложения с in-memory адаптерами."""

    clock = SystemClock()
    id_generator = UuidGenerator()
    password_hasher = Pbkdf2PasswordHasher()
    token_issuer = JwtHs256TokenIssuer(secret="dev-auth-secret")

    repositories = InMemoryRepositoryProvider(
        accounts=InMemoryAccountRepository(),
        sessions=InMemorySessionRepository(),
        refresh_tokens=InMemoryRefreshTokenRepository(),
    )
    uow = InMemoryUnitOfWork(repositories)

    # Seed demo account for local development.
    now = clock.now()
    demo = Account.register(
        account_id=id_generator.new(),
        user_id=id_generator.new(),
        email=Email("admin@example.com"),
        password_hash=PasswordHash(password_hasher.hash("admin12345")),
        default_role=Role("admin"),
        now=now,
    )
    repositories.accounts.add(demo)

    facade = ApplicationFacade()
    facade.register_command_handler(
        RegisterCommand,
        RegisterHandler(
            uow=uow,
            clock=clock,
            id_generator=id_generator,
            password_hasher=password_hasher,
        ),
    )
    facade.register_command_handler(
        LoginCommand,
        LoginHandler(
            uow=uow,
            clock=clock,
            id_generator=id_generator,
            password_hasher=password_hasher,
            token_issuer=token_issuer,
            access_ttl_seconds=3600,
            refresh_ttl_seconds=60 * 60 * 24 * 30,
        ),
    )
    facade.register_command_handler(
        RefreshCommand,
        RefreshHandler(
            uow=uow,
            clock=clock,
            id_generator=id_generator,
            token_issuer=token_issuer,
            access_ttl_seconds=3600,
            refresh_ttl_seconds=60 * 60 * 24 * 30,
        ),
    )
    facade.register_command_handler(LogoutCommand, LogoutHandler(uow=uow, clock=clock))
    facade.register_query_handler(GetMeQuery, GetMeHandler(uow=uow))

    return facade
