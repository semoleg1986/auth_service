"""Маппинг доменных ошибок в RFC7807."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
    ValidationError,
)
from src.interface.http import problem_types


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
    return JSONResponse(
        status_code=status,
        content={
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": str(exc),
            "instance": str(request.url.path),
        },
        media_type="application/problem+json",
    )
