"""Публичные auth роуты."""

from fastapi import APIRouter, Depends

from src.application.ports.token_issuer import TokenIssuer
from src.interface.http.v1.schemas.auth import JwksResponse
from src.interface.http.wiring import get_token_issuer

router = APIRouter(tags=["public"])


@router.get("/.well-known/jwks.json", response_model=JwksResponse)
def jwks(token_issuer: TokenIssuer = Depends(get_token_issuer)) -> JwksResponse:
    """Публикует JWKS документ."""

    return JwksResponse(**token_issuer.jwks())
