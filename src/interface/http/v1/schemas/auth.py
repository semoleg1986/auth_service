"""Pydantic-схемы auth API."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Тело запроса на вход."""

    email: EmailStr
    password: str = Field(min_length=8)
    ip_address: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None
    client_name: str | None = None
    country: str | None = None
    city: str | None = None
    auth_method: str = "password"
    mfa_used: bool = False
    is_trusted: bool = False
    risk_level: str = "medium"
    session_fingerprint: str | None = None
    last_path: str | None = "/v1/auth/login"
    last_action: str | None = "login"


class RefreshRequest(BaseModel):
    """Тело запроса на обновление токенов."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Тело запроса на выход."""

    session_id: str


class RegisterRequest(BaseModel):
    """Тело запроса регистрации."""

    email: EmailStr
    password: str = Field(min_length=8)
    default_role: str = "student"


class TokenPairResponse(BaseModel):
    """Ответ с парой токенов."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class MeResponse(BaseModel):
    """Профиль текущего пользователя."""

    account_id: str
    user_id: str
    email: EmailStr
    roles: list[str]
    status: str


class JwksResponse(BaseModel):
    """Публичный JWKS документ."""

    keys: list[dict]


class SessionItemResponse(BaseModel):
    """Элемент списка сессий пользователя."""

    session_id: str
    user_id: str
    account_id: str
    status: str
    auth_method: str
    mfa_used: bool
    is_trusted: bool
    risk_level: str
    session_fingerprint: str
    request_count: int
    created_at: datetime
    last_seen_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    revoke_reason: str | None = None
    ip_address: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None
    client_name: str | None = None
    country: str | None = None
    city: str | None = None
    last_path: str | None = None
    last_action: str | None = None


class SessionListResponse(BaseModel):
    """Список сессий пользователя."""

    items: list[SessionItemResponse]
