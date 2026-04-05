"""SQLAlchemy-репозиторий аккаунтов."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.identity.account.entity import Account
from src.domain.shared.statuses import AccountStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.infrastructure.db.sqlalchemy.models import AccountModel


def _serialize_roles(roles: set[Role]) -> str:
    return ",".join(sorted(role.value for role in roles))


def _deserialize_roles(value: str) -> set[Role]:
    if not value.strip():
        return set()
    return {Role(item.strip()) for item in value.split(",") if item.strip()}


class SqlalchemyAccountRepository:
    """Репозиторий `Account` на SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, account: Account) -> None:
        self._db.add(self._to_model(account))

    def save(self, account: Account) -> None:
        model = self._db.get(AccountModel, account.aggregate_id)
        if model is None:
            self._db.add(self._to_model(account))
            return
        model.user_id = account.user_id
        model.email = account.email.value
        model.password_hash = account.password_hash.value
        model.roles = _serialize_roles(account.roles)
        model.status = account.status.value
        model.created_at = account.created_at
        model.updated_at = account.updated_at
        model.version = account.version

    def get_by_id(self, account_id: str) -> Account | None:
        model = self._db.get(AccountModel, account_id)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.strip().lower())
        model = self._db.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_model(account: Account) -> AccountModel:
        return AccountModel(
            id=account.aggregate_id,
            user_id=account.user_id,
            email=account.email.value,
            password_hash=account.password_hash.value,
            roles=_serialize_roles(account.roles),
            status=account.status.value,
            created_at=account.created_at,
            updated_at=account.updated_at,
            version=account.version,
        )

    @staticmethod
    def _to_entity(model: AccountModel) -> Account:
        return Account(
            aggregate_id=model.id,
            user_id=model.user_id,
            email=Email(model.email),
            password_hash=PasswordHash(model.password_hash),
            roles=_deserialize_roles(model.roles),
            status=AccountStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )
