"""SQLAlchemy-репозиторий refresh token."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.shared.statuses import RefreshTokenStatus
from src.domain.token.refresh_token.entity import RefreshToken
from src.infrastructure.db.sqlalchemy.models import RefreshTokenModel


class SqlalchemyRefreshTokenRepository:
    """Репозиторий `RefreshToken` на SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, token: RefreshToken) -> None:
        self._db.add(self._to_model(token))

    def save(self, token: RefreshToken) -> None:
        model = self._db.get(RefreshTokenModel, token.aggregate_id)
        if model is None:
            self._db.add(self._to_model(token))
            return
        model.account_id = token.account_id
        model.session_id = token.session_id
        model.expires_at = token.expires_at
        model.status = token.status.value
        model.replaced_by_token_id = token.replaced_by_token_id
        model.created_at = token.created_at
        model.updated_at = token.updated_at
        model.version = token.version

    def get_by_id(self, token_id: str) -> RefreshToken | None:
        model = self._db.get(RefreshTokenModel, token_id)
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_model(token: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=token.aggregate_id,
            account_id=token.account_id,
            session_id=token.session_id,
            expires_at=token.expires_at,
            status=token.status.value,
            replaced_by_token_id=token.replaced_by_token_id,
            created_at=token.created_at,
            updated_at=token.updated_at,
            version=token.version,
        )

    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            aggregate_id=model.id,
            account_id=model.account_id,
            session_id=model.session_id,
            expires_at=model.expires_at,
            status=RefreshTokenStatus(model.status),
            replaced_by_token_id=model.replaced_by_token_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )
