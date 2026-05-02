"""HTTP роуты auth v1."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from src.application.identity.queries.dto import GetMeQuery
from src.application.ports.token_issuer import TokenIssuer
from src.application.session.commands.dto import (
    LoginCommand,
    LogoutCommand,
    RegisterCommand,
)
from src.application.session.queries.dto import ListSessionsQuery
from src.application.token.commands.dto import RefreshCommand
from src.domain.errors import AccessDeniedError
from src.interface.http.common.rate_limit import (
    LOGIN_RATE_RULE,
    REFRESH_RATE_RULE,
    enforce_rate_limit,
)
from src.interface.http.common.user_agent_parser import parse_user_agent
from src.interface.http.observability import increment_counter
from src.interface.http.v1.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    SessionItemResponse,
    SessionListResponse,
    TokenPairResponse,
)
from src.interface.http.wiring import get_facade, get_token_issuer

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(payload: RegisterRequest, facade=Depends(get_facade)) -> dict:
    """Регистрирует учетную запись."""

    return facade.execute(
        RegisterCommand(
            email=str(payload.email),
            password=payload.password,
            default_role=payload.default_role,
        )
    )


@router.post("/login", response_model=TokenPairResponse)
def login(
    payload: LoginRequest,
    request: Request,
    facade=Depends(get_facade),
    user_agent_header: str | None = Header(default=None, alias="User-Agent"),
) -> TokenPairResponse:
    """Выполняет login и выдает пару токенов."""

    client_host = request.client.host if request.client else "unknown"
    enforce_rate_limit(
        scope="auth_login",
        key=f"{client_host}:{str(payload.email).lower()}",
        rule=LOGIN_RATE_RULE,
    )

    parsed = parse_user_agent(payload.user_agent_raw or user_agent_header)
    try:
        result = facade.execute(
            LoginCommand(
                email=str(payload.email),
                password=payload.password,
                ip_address=payload.ip_address,
                user_agent_raw=parsed.user_agent_raw,
                device_type=payload.device_type or parsed.device_type,
                os_name=payload.os_name or parsed.os_name,
                os_version=payload.os_version or parsed.os_version,
                browser_name=payload.browser_name or parsed.browser_name,
                browser_version=payload.browser_version or parsed.browser_version,
                client_name=payload.client_name or parsed.client_name,
                country=payload.country,
                city=payload.city,
                auth_method=payload.auth_method,
                mfa_used=payload.mfa_used,
                is_trusted=payload.is_trusted,
                risk_level=payload.risk_level or parsed.risk_level,
                session_fingerprint=payload.session_fingerprint,
                last_path=payload.last_path,
                last_action=payload.last_action,
            )
        )
    except AccessDeniedError:
        increment_counter(
            "auth_login_fail_total",
            "Total failed auth login attempts.",
            reason="access_denied",
        )
        raise
    increment_counter(
        "auth_login_success_total",
        "Total successful auth logins.",
        auth_method=payload.auth_method,
    )
    return TokenPairResponse(**asdict(result))


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    payload: RefreshRequest,
    request: Request,
    facade=Depends(get_facade),
) -> TokenPairResponse:
    """Ротирует refresh token и выдает новую пару токенов."""

    client_host = request.client.host if request.client else "unknown"
    enforce_rate_limit(
        scope="auth_refresh",
        key=client_host,
        rule=REFRESH_RATE_RULE,
    )

    result = facade.execute(RefreshCommand(refresh_token=payload.refresh_token))
    return TokenPairResponse(**asdict(result))


@router.post("/logout", status_code=204)
def logout(payload: LogoutRequest, facade=Depends(get_facade)) -> None:
    """Завершает пользовательскую сессию."""

    facade.execute(LogoutCommand(session_id=payload.session_id))
    return None


@router.get("/me", response_model=MeResponse)
def me(
    authorization: str | None = Header(default=None),
    facade=Depends(get_facade),
    token_issuer: TokenIssuer = Depends(get_token_issuer),
) -> MeResponse:
    """Возвращает профиль текущего пользователя по access token."""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется Bearer токен.")
    access = authorization.removeprefix("Bearer ").strip()
    claims = token_issuer.decode_access(access)
    account_id = str(claims.get("sub", ""))
    if not account_id:
        raise HTTPException(status_code=401, detail="Некорректный access token.")
    result = facade.query(GetMeQuery(account_id=account_id))
    return MeResponse(**asdict(result))


@router.get("/sessions", response_model=SessionListResponse)
def sessions(
    authorization: str | None = Header(default=None),
    facade=Depends(get_facade),
    token_issuer: TokenIssuer = Depends(get_token_issuer),
) -> SessionListResponse:
    """Возвращает список сессий текущего пользователя."""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется Bearer токен.")
    access = authorization.removeprefix("Bearer ").strip()
    claims = token_issuer.decode_access(access)
    account_id = str(claims.get("sub", ""))
    if not account_id:
        raise HTTPException(status_code=401, detail="Некорректный access token.")

    results = facade.query(ListSessionsQuery(account_id=account_id))
    return SessionListResponse(
        items=[SessionItemResponse(**asdict(item)) for item in results]
    )
