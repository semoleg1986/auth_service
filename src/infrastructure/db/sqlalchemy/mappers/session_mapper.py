"""Мапперы AuthSession <-> AuthSessionModel."""

from __future__ import annotations

from src.domain.session.auth_session.entity import AuthSession
from src.domain.shared.statuses import SessionStatus
from src.infrastructure.db.sqlalchemy.models import AuthSessionModel


def to_model(session: AuthSession) -> AuthSessionModel:
    """Преобразует доменную сессию в ORM-модель."""

    model = AuthSessionModel(id=session.aggregate_id, account_id=session.account_id)
    copy_to_model(session, model)
    return model


def copy_to_model(session: AuthSession, model: AuthSessionModel) -> None:
    """Копирует поля доменной сессии в ORM-модель."""

    model.account_id = session.account_id
    model.user_id = session.user_id
    model.refresh_token_id = session.refresh_token_id
    model.status = session.status.value
    model.ip_address = session.ip_address
    model.user_agent_raw = session.user_agent_raw
    model.device_type = session.device_type.value
    model.os_name = session.os_name
    model.os_version = session.os_version
    model.browser_name = session.browser_name
    model.browser_version = session.browser_version
    model.client_name = session.client_name
    model.country = session.country
    model.city = session.city
    model.auth_method = session.auth_method.value
    model.mfa_used = session.mfa_used
    model.is_trusted = session.is_trusted
    model.risk_level = session.risk_level.value
    model.session_fingerprint = session.session_fingerprint
    model.request_count = session.request_count
    model.last_path = session.last_path
    model.last_action = session.last_action
    model.created_at = session.created_at
    model.updated_at = session.updated_at
    model.last_seen_at = session.last_seen_at
    model.expires_at = session.expires_at
    model.revoked_at = session.revoked_at
    model.revoke_reason = session.revoke_reason
    model.version = session.version


def to_entity(model: AuthSessionModel) -> AuthSession:
    """Преобразует ORM-модель в доменную сессию."""

    return AuthSession(
        aggregate_id=model.id,
        account_id=model.account_id,
        user_id=model.user_id,
        refresh_token_id=model.refresh_token_id,
        status=SessionStatus(model.status),
        ip_address=model.ip_address,
        user_agent_raw=model.user_agent_raw,
        device_type=model.device_type,
        os_name=model.os_name,
        os_version=model.os_version,
        browser_name=model.browser_name,
        browser_version=model.browser_version,
        client_name=model.client_name,
        country=model.country,
        city=model.city,
        auth_method=model.auth_method,
        mfa_used=model.mfa_used,
        is_trusted=model.is_trusted,
        risk_level=model.risk_level,
        session_fingerprint=model.session_fingerprint,
        request_count=model.request_count,
        last_path=model.last_path,
        last_action=model.last_action,
        created_at=model.created_at,
        updated_at=model.updated_at,
        last_seen_at=model.last_seen_at,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        revoke_reason=model.revoke_reason,
        version=model.version,
    )
