"""SQLAlchemy-репозиторий сессий."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.session.auth_session.entity import AuthSession
from src.infrastructure.db.sqlalchemy.mappers import session_mapper
from src.infrastructure.db.sqlalchemy.models import AuthSessionModel


class SqlalchemySessionRepository:
    """Репозиторий `AuthSession` на SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, session: AuthSession) -> None:
        self._db.add(session_mapper.to_model(session))

    def save(self, session: AuthSession) -> None:
        model = self._db.get(AuthSessionModel, session.aggregate_id)
        if model is None:
            self._db.add(session_mapper.to_model(session))
            return
        session_mapper.copy_to_model(session, model)

    def get_by_id(self, session_id: str) -> AuthSession | None:
        model = self._db.get(AuthSessionModel, session_id)
        return session_mapper.to_entity(model) if model else None

    def list_by_account_id(self, account_id: str) -> list[AuthSession]:
        stmt = select(AuthSessionModel).where(AuthSessionModel.account_id == account_id)
        return [session_mapper.to_entity(item) for item in self._db.execute(stmt).scalars().all()]
