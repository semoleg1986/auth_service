"""Публичные auth роуты."""

from fastapi import APIRouter

from src.infrastructure.crypto.jwt_token_issuer_hs256 import JwtHs256TokenIssuer
from src.interface.http.v1.schemas.auth import JwksResponse

router = APIRouter(tags=["public"])


@router.get("/.well-known/jwks.json", response_model=JwksResponse)
def jwks() -> JwksResponse:
    """Публикует JWKS документ."""

    issuer = JwtHs256TokenIssuer(secret="dev-auth-secret")
    return JwksResponse(**issuer.jwks())
