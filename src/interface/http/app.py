"""Инициализация FastAPI приложения."""

from fastapi import FastAPI

from src.domain.errors import DomainError
from src.interface.http.errors import domain_error_handler
from src.interface.http.health import router as health_router
from src.interface.http.v1.auth.router import router as auth_router
from src.interface.http.v1.public.router import router as public_router


def create_app() -> FastAPI:
    """Создает и настраивает HTTP приложение."""

    app = FastAPI(title="auth_service")
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(public_router)
    app.add_exception_handler(DomainError, domain_error_handler)
    return app
