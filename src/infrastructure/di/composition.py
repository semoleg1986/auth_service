"""Composition root auth_service."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.facade.application_facade import ApplicationFacade
from src.application.identity.handlers.get_me_handler import GetMeHandler
from src.application.identity.queries.dto import GetMeQuery
from src.application.ports.token_issuer import TokenIssuer
from src.application.session.commands.dto import LoginCommand, LogoutCommand, RegisterCommand
from src.application.session.handlers.list_sessions_handler import ListSessionsHandler
from src.application.session.handlers.login_handler import LoginHandler
from src.application.session.handlers.logout_handler import LogoutHandler
from src.application.session.handlers.register_handler import RegisterHandler
from src.application.session.queries.dto import ListSessionsQuery
from src.application.token.commands.dto import RefreshCommand
from src.application.token.handlers.refresh_handler import RefreshHandler
from src.domain.identity.account.entity import Account
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.config.settings import Settings
from src.infrastructure.crypto.jwt_token_issuer_eddsa import JwtEdDsaTokenIssuer
from src.infrastructure.crypto.password_hasher_argon2 import Argon2PasswordHasher
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from src.infrastructure.db.inmemory.uow import InMemoryRepositoryProvider, InMemoryUnitOfWork
from src.infrastructure.db.sqlalchemy.base import Base
from src.infrastructure.db.sqlalchemy.session import build_engine, build_session_factory
from src.infrastructure.db.sqlalchemy.uow.sqlalchemy_uow import SqlalchemyUnitOfWork
from src.infrastructure.id.uuid_generator import UuidGenerator


@dataclass(frozen=True, slots=True)
class RuntimeContainer:
    """Контейнер runtime-зависимостей."""

    facade: ApplicationFacade
    token_issuer: TokenIssuer


def build_runtime() -> RuntimeContainer:
    """Собирает runtime и DI-граф приложения."""

    settings = Settings.from_env()
    clock = SystemClock()
    id_generator = UuidGenerator()
    password_hasher = Argon2PasswordHasher()
    token_issuer = JwtEdDsaTokenIssuer()

    repositories = None
    if settings.use_inmemory:
        repositories = InMemoryRepositoryProvider(
            accounts=InMemoryAccountRepository(),
            sessions=InMemorySessionRepository(),
            refresh_tokens=InMemoryRefreshTokenRepository(),
        )
        uow = InMemoryUnitOfWork(repositories)
    else:
        engine = build_engine(settings.database_url)
        if settings.auto_create_schema:
            Base.metadata.create_all(bind=engine)
        session_factory = build_session_factory(engine)
        uow = SqlalchemyUnitOfWork(session_factory)

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
    if settings.use_inmemory:
        assert repositories is not None
        if repositories.accounts.get_by_email("admin@example.com") is None:
            repositories.accounts.add(demo)
    else:
        existing = uow.repositories.accounts.get_by_email("admin@example.com")
        if existing is None:
            uow.repositories.accounts.add(demo)
            uow.commit()

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
    facade.register_query_handler(ListSessionsQuery, ListSessionsHandler(uow=uow))

    return RuntimeContainer(facade=facade, token_issuer=token_issuer)


def build_application_facade() -> ApplicationFacade:
    """Совместимый конструктор фасада приложения."""

    return build_runtime().facade
