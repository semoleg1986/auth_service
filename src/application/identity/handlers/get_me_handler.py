"""Handler запроса профиля текущего пользователя."""

from __future__ import annotations

from src.application.common.dto import MeResult
from src.application.identity.queries.dto import GetMeQuery
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.errors import NotFoundError


class GetMeHandler:
    """Возвращает профиль текущего аккаунта."""

    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def __call__(self, query: GetMeQuery) -> MeResult:
        account = self._uow.repositories.accounts.get_by_id(query.account_id)
        if account is None:
            raise NotFoundError("Аккаунт не найден.")
        return MeResult(
            account_id=account.aggregate_id,
            user_id=account.user_id,
            email=account.email.value,
            roles=sorted(role.value for role in account.roles),
            status=account.status.value,
        )
