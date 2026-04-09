from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.application.ports.token_issuer import AccessTokenPayload
from src.domain.errors import AccessDeniedError
from src.infrastructure.crypto.jwt_token_issuer_eddsa import JwtEdDsaTokenIssuer
from src.infrastructure.crypto.password_hasher_argon2 import Argon2PasswordHasher


def test_password_hasher_verify_branches() -> None:
    hasher = Argon2PasswordHasher()
    password_hash = hasher.hash("pass-12345")

    assert hasher.verify("pass-12345", password_hash) is True
    assert hasher.verify("wrong", password_hash) is False
    assert hasher.verify("pass-12345", "not-a-valid-argon2-hash") is False


def test_jwt_issuer_loads_private_key_pem_branch() -> None:
    private = Ed25519PrivateKey.generate()
    private_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    issuer = JwtEdDsaTokenIssuer(private_key_pem=private_pem)
    now = datetime.now(UTC)
    pair = issuer.issue_pair(
        AccessTokenPayload(
            sub="acc-1",
            jti="jti-1",
            roles=["parent"],
            issued_at=now,
            expires_at=now + timedelta(minutes=10),
        ),
        refresh_claims={"token_id": "rt-1", "account_id": "acc-1", "session_id": "s-1"},
    )
    assert issuer.decode_access(pair.access_token)["sub"] == "acc-1"


def test_jwt_issuer_public_key_only_branch_and_empty_roles() -> None:
    private = Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    issuer = JwtEdDsaTokenIssuer(public_key_pem=public_pem)
    now = datetime.now(UTC)
    pair = issuer.issue_pair(
        AccessTokenPayload(
            sub="acc-2",
            jti="jti-2",
            roles=[],
            issued_at=now,
            expires_at=now + timedelta(minutes=10),
        ),
        refresh_claims={"token_id": "rt-2", "account_id": "acc-2", "session_id": "s-2"},
    )

    with pytest.raises(AccessDeniedError):
        issuer.decode_access(pair.access_token)
