from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from src.application.ports.token_issuer import AccessTokenPayload
from src.domain.errors import AccessDeniedError
from src.infrastructure.crypto.jwt_token_issuer_eddsa import JwtEdDsaTokenIssuer


def test_access_and_refresh_tokens_follow_contract() -> None:
    issuer = JwtEdDsaTokenIssuer(
        issuer="auth_service",
        audience="platform_clients",
    )
    now = datetime.now(UTC)

    tokens = issuer.issue_pair(
        AccessTokenPayload(
            sub="acc-1",
            jti="jti-1",
            roles=["student"],
            issued_at=now,
            expires_at=now + timedelta(minutes=10),
            user_id="user-1",
        ),
        refresh_claims={
            "token_id": "rt-1",
            "account_id": "acc-1",
            "session_id": "sess-1",
        },
    )

    access_claims = issuer.decode_access(tokens.access_token)
    assert access_claims["sub"] == "acc-1"
    assert access_claims["user_id"] == "user-1"
    assert access_claims["jti"] == "jti-1"
    assert access_claims["roles"] == ["student"]

    refresh_claims = issuer.decode_refresh(tokens.refresh_token)
    assert refresh_claims["token_id"] == "rt-1"
    assert refresh_claims["account_id"] == "acc-1"
    assert refresh_claims["session_id"] == "sess-1"


def test_refresh_decode_rejects_access_token() -> None:
    issuer = JwtEdDsaTokenIssuer(
        issuer="auth_service",
        audience="platform_clients",
    )
    now = datetime.now(UTC)
    tokens = issuer.issue_pair(
        AccessTokenPayload(
            sub="acc-2",
            jti="jti-2",
            roles=["teacher"],
            issued_at=now,
            expires_at=now + timedelta(minutes=10),
        ),
        refresh_claims={
            "token_id": "rt-2",
            "account_id": "acc-2",
            "session_id": "sess-2",
        },
    )

    with pytest.raises(AccessDeniedError):
        issuer.decode_refresh(tokens.access_token)


def test_access_decode_rejects_refresh_token() -> None:
    issuer = JwtEdDsaTokenIssuer(
        issuer="auth_service",
        audience="platform_clients",
    )
    now = datetime.now(UTC)
    tokens = issuer.issue_pair(
        AccessTokenPayload(
            sub="acc-3",
            jti="jti-3",
            roles=["admin"],
            issued_at=now,
            expires_at=now + timedelta(minutes=10),
        ),
        refresh_claims={
            "token_id": "rt-3",
            "account_id": "acc-3",
            "session_id": "sess-3",
        },
    )

    with pytest.raises(AccessDeniedError):
        issuer.decode_access(tokens.refresh_token)
