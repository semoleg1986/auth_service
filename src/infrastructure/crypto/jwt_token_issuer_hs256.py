"""HS256-реализация token issuer для локальной разработки."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime

from src.application.ports.token_issuer import AccessTokenPayload, TokenPair
from src.domain.errors import AccessDeniedError


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


class JwtHs256TokenIssuer:
    """Выпускает и проверяет JWT на HS256.

    Для production рекомендуется заменить на асимметричную схему с ротацией ключей.
    """

    def __init__(self, secret: str, issuer: str = "auth_service") -> None:
        self._secret = secret.encode("utf-8")
        self._issuer = issuer

    def issue_pair(self, payload: AccessTokenPayload, refresh_claims: dict[str, str]) -> TokenPair:
        now_ts = int(payload.issued_at.timestamp())
        access_claims = {
            "iss": self._issuer,
            "sub": payload.sub,
            "jti": payload.jti,
            "roles": payload.roles,
            "iat": now_ts,
            "exp": int(payload.expires_at.timestamp()),
        }
        refresh_claims_payload = {
            "iss": self._issuer,
            **refresh_claims,
            "iat": now_ts,
            "exp": int(datetime.now(UTC).timestamp()) + 60 * 60 * 24 * 30,
        }
        return TokenPair(
            access_token=self._encode(access_claims),
            refresh_token=self._encode(refresh_claims_payload),
        )

    def decode_refresh(self, refresh_token: str) -> dict[str, str]:
        claims = self._decode(refresh_token)
        return {
            "token_id": str(claims.get("token_id", "")),
            "account_id": str(claims.get("account_id", "")),
            "session_id": str(claims.get("session_id", "")),
        }

    def decode_access(self, access_token: str) -> dict[str, str | list[str]]:
        claims = self._decode(access_token)
        return {
            "sub": str(claims.get("sub", "")),
            "jti": str(claims.get("jti", "")),
            "roles": list(claims.get("roles", [])),
        }

    def jwks(self) -> dict:
        return {
            "keys": [
                {
                    "kty": "oct",
                    "alg": "HS256",
                    "use": "sig",
                    "kid": "local-hs256",
                }
            ]
        }

    def _encode(self, claims: dict) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = _b64url_encode(json.dumps(claims, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        signature = hmac.new(self._secret, signing_input, hashlib.sha256).digest()
        return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"

    def _decode(self, token: str) -> dict:
        try:
            header_b64, payload_b64, sig_b64 = token.split(".", 2)
            signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
            expected_sig = hmac.new(self._secret, signing_input, hashlib.sha256).digest()
            actual_sig = _b64url_decode(sig_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                raise AccessDeniedError("Некорректная подпись токена.")
            claims = json.loads(_b64url_decode(payload_b64))
            exp = int(claims.get("exp", 0))
            if exp and int(datetime.now(UTC).timestamp()) >= exp:
                raise AccessDeniedError("Токен истек.")
            return claims
        except AccessDeniedError:
            raise
        except Exception as exc:
            raise AccessDeniedError("Некорректный токен.") from exc
