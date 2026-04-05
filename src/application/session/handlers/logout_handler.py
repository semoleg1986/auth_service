"""Handler завершения сессии."""

from __future__ import annotations

from src.application.ports.clock import Clock
from src.application.ports.unit_of_work import UnitOfWork
from src.application.session.commands.dto import LogoutCommand
from src.domain.errors import NotFoundError


class LogoutHandler:
    """Закрывает пользовательскую сессию и отзывает refresh token."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, command: LogoutCommand) -> None:
        session = self._uow.repositories.sessions.get_by_id(command.session_id)
        if session is None:
            raise NotFoundError("Сессия не найдена.")

        now = self._clock.now()
        session.close(now=now)
        self._uow.repositories.sessions.save(session)

        if session.refresh_token_id:
            token = self._uow.repositories.refresh_tokens.get_by_id(session.refresh_token_id)
            if token is not None:
                token.revoke(now=now)
                self._uow.repositories.refresh_tokens.save(token)

        self._uow.commit()
