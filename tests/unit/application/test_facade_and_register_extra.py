from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.facade.application_facade import ApplicationFacade
from src.application.session.commands.dto import RegisterCommand
from src.application.session.handlers.register_handler import RegisterHandler
from src.domain.errors import InvariantViolationError
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.crypto.password_hasher_argon2 import Argon2PasswordHasher
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAccountRepository,
    InMemoryRefreshTokenRepository,
    InMemorySessionRepository,
)
from src.infrastructure.db.inmemory.uow import InMemoryRepositoryProvider, InMemoryUnitOfWork
from src.infrastructure.id.uuid_generator import UuidGenerator


def _register_handler() -> RegisterHandler:
    repos = InMemoryRepositoryProvider(
        accounts=InMemoryAccountRepository(),
        sessions=InMemorySessionRepository(),
        refresh_tokens=InMemoryRefreshTokenRepository(),
    )
    return RegisterHandler(
        uow=InMemoryUnitOfWork(repos),
        clock=SystemClock(),
        id_generator=UuidGenerator(),
        password_hasher=Argon2PasswordHasher(),
    )


def test_register_rejects_duplicate_email() -> None:
    handler = _register_handler()
    cmd = RegisterCommand(email="dup@example.com", password="pass-12345", default_role="parent")

    handler(cmd)
    with pytest.raises(InvariantViolationError):
        handler(cmd)


def test_application_facade_query_and_missing_query_handler() -> None:
    facade = ApplicationFacade()

    class Ping:
        def __init__(self, value: str) -> None:
            self.value = value

    facade.register_query_handler(Ping, lambda q: {"ok": q.value})
    assert facade.query(Ping("pong")) == {"ok": "pong"}

    class Unknown:
        pass

    with pytest.raises(KeyError):
        facade.query(Unknown())
