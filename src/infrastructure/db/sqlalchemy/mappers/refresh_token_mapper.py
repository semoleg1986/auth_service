"""Мапперы RefreshToken <-> RefreshTokenModel."""

from __future__ import annotations

from src.domain.shared.statuses import RefreshTokenStatus
from src.domain.token.refresh_token.entity import RefreshToken
from src.infrastructure.db.sqlalchemy.models import RefreshTokenModel


def to_model(token: RefreshToken) -> RefreshTokenModel:
    """Преобразует доменный токен в ORM-модель."""

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


def copy_to_model(token: RefreshToken, model: RefreshTokenModel) -> None:
    """Копирует поля доменного токена в ORM-модель."""

    model.account_id = token.account_id
    model.session_id = token.session_id
    model.expires_at = token.expires_at
    model.status = token.status.value
    model.replaced_by_token_id = token.replaced_by_token_id
    model.created_at = token.created_at
    model.updated_at = token.updated_at
    model.version = token.version


def to_entity(model: RefreshTokenModel) -> RefreshToken:
    """Преобразует ORM-модель в доменный токен."""

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
