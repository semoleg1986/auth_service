"""Handler запроса списка сессий пользователя."""

from __future__ import annotations

from src.application.common.dto import SessionInfoResult
from src.application.ports.unit_of_work import UnitOfWork
from src.application.session.queries.dto import ListSessionsQuery


class ListSessionsHandler:
    """Возвращает список сессий аккаунта."""

    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def __call__(self, query: ListSessionsQuery) -> list[SessionInfoResult]:
        sessions = self._uow.repositories.sessions.list_by_account_id(query.account_id)
        sessions = sorted(sessions, key=lambda item: item.created_at, reverse=True)
        return [
            SessionInfoResult(
                session_id=item.aggregate_id,
                status=item.status.value,
                created_at=item.created_at,
                updated_at=item.updated_at,
                ip=item.ip,
                user_agent_raw=item.user_agent_raw,
                device_type=item.device_type,
                os_name=item.os_name,
                os_version=item.os_version,
                browser_name=item.browser_name,
                browser_version=item.browser_version,
            )
            for item in sessions
        ]
