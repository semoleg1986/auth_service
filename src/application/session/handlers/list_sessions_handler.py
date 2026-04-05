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
                user_id=item.user_id,
                account_id=item.account_id,
                status=item.status.value,
                auth_method=item.auth_method.value,
                mfa_used=item.mfa_used,
                is_trusted=item.is_trusted,
                risk_level=item.risk_level.value,
                session_fingerprint=item.session_fingerprint,
                request_count=item.request_count,
                created_at=item.created_at,
                last_seen_at=item.last_seen_at,
                expires_at=item.expires_at,
                revoked_at=item.revoked_at,
                revoke_reason=item.revoke_reason,
                ip_address=item.ip_address,
                user_agent_raw=item.user_agent_raw,
                device_type=item.device_type.value if item.device_type else None,
                os_name=item.os_name,
                os_version=item.os_version,
                browser_name=item.browser_name,
                browser_version=item.browser_version,
                client_name=item.client_name,
                country=item.country,
                city=item.city,
                last_path=item.last_path,
                last_action=item.last_action,
            )
            for item in sessions
        ]
