"""Маппинг HTTP/domain ошибок в RFC7807."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.errors import (
    AccessDeniedError,
    DomainError,
    InvariantViolationError,
    NotFoundError,
    ValidationError,
)
from src.interface.http import problem_types


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or request.headers.get(
        "X-Request-ID"
    )


def _correlation_id(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None) or request.headers.get(
        "X-Correlation-ID"
    )


def _headers(request: Request, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = dict(extra or {})
    request_id = _request_id(request)
    correlation_id = _correlation_id(request)
    if request_id is not None:
        headers["X-Request-ID"] = request_id
    if correlation_id is not None:
        headers["X-Correlation-ID"] = correlation_id
    return headers


def _problem(
    request: Request,
    *,
    status: int,
    title: str,
    problem_type: str,
    detail: object,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": str(request.url.path),
            "request_id": _request_id(request),
            "correlation_id": _correlation_id(request),
        },
        headers=_headers(request, headers),
        media_type="application/problem+json",
    )


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Конвертирует доменное исключение в `application/problem+json`."""

    mapping: dict[type[Exception], tuple[int, str, str]] = {
        ValidationError: (422, "Ошибка валидации", problem_types.VALIDATION),
        NotFoundError: (404, "Не найдено", problem_types.NOT_FOUND),
        AccessDeniedError: (403, "Доступ запрещен", problem_types.ACCESS_DENIED),
        InvariantViolationError: (409, "Нарушение инварианта", problem_types.CONFLICT),
    }
    status, title, problem_type = mapping.get(
        type(exc),
        (500, "Внутренняя ошибка", "about:blank"),
    )
    return _problem(
        request,
        status=status,
        title=title,
        problem_type=problem_type,
        detail=str(exc),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Конвертирует ошибки валидации FastAPI в RFC7807."""

    return _problem(
        request,
        status=422,
        title="Ошибка валидации",
        problem_type=problem_types.VALIDATION,
        detail=str(exc),
    )


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Конвертирует HTTPException в RFC7807."""

    mapping = {
        401: ("Не авторизован", problem_types.UNAUTHORIZED),
        403: ("Доступ запрещен", problem_types.ACCESS_DENIED),
        404: ("Не найдено", problem_types.NOT_FOUND),
        409: ("Конфликт", problem_types.CONFLICT),
        422: ("Ошибка валидации", problem_types.VALIDATION),
    }
    title, problem_type = mapping.get(exc.status_code, (str(exc.detail), "about:blank"))
    return _problem(
        request,
        status=exc.status_code,
        title=title,
        problem_type=problem_type,
        detail=exc.detail,
        headers=exc.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует единый problem+json контракт ошибок."""

    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
