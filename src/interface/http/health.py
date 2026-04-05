"""Health endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health() -> dict[str, str]:
    """Проверка доступности сервиса."""

    return {"status": "ok"}
