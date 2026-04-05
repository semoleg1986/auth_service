"""SQLAlchemy-репозиторий refresh token."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.token.refresh_token.entity import RefreshToken
from src.infrastructure.db.sqlalchemy.mappers import refresh_token_mapper
from src.infrastructure.db.sqlalchemy.models import RefreshTokenModel


class SqlalchemyRefreshTokenRepository:
    """Репозиторий `RefreshToken` на SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, token: RefreshToken) -> None:
        self._db.add(refresh_token_mapper.to_model(token))

    def save(self, token: RefreshToken) -> None:
        model = self._db.get(RefreshTokenModel, token.aggregate_id)
        if model is None:
            self._db.add(refresh_token_mapper.to_model(token))
            return
        refresh_token_mapper.copy_to_model(token, model)

    def get_by_id(self, token_id: str) -> RefreshToken | None:
        model = self._db.get(RefreshTokenModel, token_id)
        return refresh_token_mapper.to_entity(model) if model else None
