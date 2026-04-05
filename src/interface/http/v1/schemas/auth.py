"""Pydantic-схемы auth API."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Тело запроса на вход."""

    email: EmailStr
    password: str = Field(min_length=8)
    ip: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None


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
    status: str
    created_at: datetime
    updated_at: datetime
    ip: str | None = None
    user_agent_raw: str | None = None
    device_type: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    browser_name: str | None = None
    browser_version: str | None = None


class SessionListResponse(BaseModel):
    """Список сессий пользователя."""

    items: list[SessionItemResponse]
