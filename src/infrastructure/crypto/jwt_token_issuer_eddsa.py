"""EdDSA-реализация token issuer (Ed25519 + JWKS)."""

from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from src.application.ports.token_issuer import AccessTokenPayload, TokenPair
from src.domain.errors import AccessDeniedError


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class JwtEdDsaTokenIssuer:
    """Выпускает и проверяет JWT на алгоритме EdDSA (Ed25519)."""

    def __init__(
        self,
        *,
        issuer: str = "auth_service",
        audience: str = "platform_clients",
        private_key_pem: str | None = None,
        public_key_pem: str | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._private_key, self._public_key = self._load_or_generate_keys(
            private_key_pem=private_key_pem,
            public_key_pem=public_key_pem,
        )
        self._kid = self._build_kid()

    def issue_pair(
        self,
        payload: AccessTokenPayload,
        refresh_claims: dict[str, str],
    ) -> TokenPair:
        now_ts = int(payload.issued_at.timestamp())
        access_claims = {
            "iss": self._issuer,
            "aud": self._audience,
            "typ": "access",
            "sub": payload.sub,
            "jti": payload.jti,
            "roles": payload.roles,
            "iat": now_ts,
            "exp": int(payload.expires_at.timestamp()),
        }
        if payload.user_id:
            access_claims["user_id"] = payload.user_id
        refresh_claims_payload = {
            "iss": self._issuer,
            "aud": self._audience,
            "typ": "refresh",
            **refresh_claims,
            "iat": now_ts,
            "exp": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
        }
        return TokenPair(
            access_token=self._encode(access_claims),
            refresh_token=self._encode(refresh_claims_payload),
        )

    def decode_refresh(self, refresh_token: str) -> dict[str, str]:
        claims = self._decode(refresh_token)
        if claims.get("typ") != "refresh":
            raise AccessDeniedError("Некорректный тип токена для refresh операции.")

        token_id = str(claims.get("token_id", ""))
        account_id = str(claims.get("account_id", ""))
        session_id = str(claims.get("session_id", ""))
        if not token_id or not account_id or not session_id:
            raise AccessDeniedError("В refresh token отсутствуют обязательные claims.")

        return {
            "token_id": token_id,
            "account_id": account_id,
            "session_id": session_id,
        }

    def decode_access(self, access_token: str) -> dict[str, str | list[str]]:
        claims = self._decode(access_token)
        if claims.get("typ") != "access":
            raise AccessDeniedError("Некорректный тип токена для access операции.")

        subject = str(claims.get("sub", ""))
        token_id = str(claims.get("jti", ""))
        roles = list(claims.get("roles", []))
        if not subject or not token_id or not roles:
            raise AccessDeniedError("В access token отсутствуют обязательные claims.")

        return {
            "sub": subject,
            "jti": token_id,
            "roles": roles,
            "user_id": str(claims.get("user_id", "")).strip(),
        }

    def jwks(self) -> dict:
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": _b64url(public_bytes),
                    "alg": "EdDSA",
                    "use": "sig",
                    "kid": self._kid,
                }
            ]
        }

    def _encode(self, claims: dict) -> str:
        try:
            return jwt.encode(
                claims,
                self._private_key,
                algorithm="EdDSA",
                headers={"kid": self._kid, "typ": "JWT"},
            )
        except Exception as exc:
            raise AccessDeniedError("Не удалось выпустить токен.") from exc

    def _decode(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self._public_key,
                algorithms=["EdDSA"],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["iss", "aud", "iat", "exp", "typ"]},
            )
        except Exception as exc:
            raise AccessDeniedError("Некорректный токен.") from exc

    def _build_kid(self) -> str:
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        digest = hashlib.sha256(public_bytes).digest()[:8]
        return f"ed25519-{_b64url(digest)}"

    @staticmethod
    def _load_or_generate_keys(
        *,
        private_key_pem: str | None,
        public_key_pem: str | None,
    ) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        if private_key_pem:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=None,
            )
            if not isinstance(private_key, Ed25519PrivateKey):
                raise ValueError("Ожидался Ed25519 private key.")
            return private_key, private_key.public_key()

        if public_key_pem:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8")
            )
            if not isinstance(public_key, Ed25519PublicKey):
                raise ValueError("Ожидался Ed25519 public key.")
            # Только с public key нельзя подписывать access/refresh, поэтому генерируем runtime pair.
            # Public key из параметра используется для валидации в других адаптерах.
            private_key = Ed25519PrivateKey.generate()
            return private_key, public_key

        private_key = Ed25519PrivateKey.generate()
        return private_key, private_key.public_key()
