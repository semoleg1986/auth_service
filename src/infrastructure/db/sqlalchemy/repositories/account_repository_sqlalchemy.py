"""SQLAlchemy-репозиторий аккаунтов."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.identity.account.entity import Account
from src.infrastructure.db.sqlalchemy.mappers import account_mapper
from src.infrastructure.db.sqlalchemy.models import AccountModel


class SqlalchemyAccountRepository:
    """Репозиторий `Account` на SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, account: Account) -> None:
        self._db.add(account_mapper.to_model(account))

    def save(self, account: Account) -> None:
        model = self._db.get(AccountModel, account.aggregate_id)
        if model is None:
            self._db.add(account_mapper.to_model(account))
            return
        account_mapper.copy_to_model(account, model)

    def get_by_id(self, account_id: str) -> Account | None:
        model = self._db.get(AccountModel, account_id)
        return account_mapper.to_entity(model) if model else None

    def get_by_email(self, email: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.strip().lower())
        model = self._db.execute(stmt).scalar_one_or_none()
        return account_mapper.to_entity(model) if model else None
