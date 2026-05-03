"""Handler завершения сессии."""

from __future__ import annotations

from src.application.ports.clock import Clock
from src.application.ports.unit_of_work import UnitOfWorkFactory
from src.application.session.commands.dto import LogoutCommand
from src.domain.errors import NotFoundError


class LogoutHandler:
    """Закрывает пользовательскую сессию и отзывает refresh token."""

    def __init__(self, *, uow_factory: UnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def __call__(self, command: LogoutCommand) -> None:
        uow = self._uow_factory()
        try:
            session = uow.repositories.sessions.get_by_id(command.session_id)
            if session is None:
                raise NotFoundError("Сессия не найдена.")

            now = self._clock.now()
            session.close(now=now)
            uow.repositories.sessions.save(session)

            if session.refresh_token_id:
                token = uow.repositories.refresh_tokens.get_by_id(
                    session.refresh_token_id
                )
                if token is not None:
                    token.revoke(now=now)
                    uow.repositories.refresh_tokens.save(token)

            uow.commit()
        except Exception:
            uow.rollback()
            raise
        finally:
            close = getattr(uow, "close", None)
            if callable(close):
                close()
