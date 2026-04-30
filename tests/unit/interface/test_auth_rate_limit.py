from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.common.rate_limit import RateLimitRule
from src.interface.http.v1.auth import router as auth_router
from src.interface.http.wiring import get_runtime


def _client() -> TestClient:
    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    os.environ.pop("AUTH_DATABASE_URL", None)
    get_runtime.cache_clear()
    return TestClient(create_app())


def test_login_rate_limit_returns_429(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_router, "LOGIN_RATE_RULE", RateLimitRule(max_requests=1, window_seconds=60)
    )
    client = _client()

    payload = {
        "email": "admin@example.com",
        "password": "admin12345",
        "session_fingerprint": "limit-login",
    }
    first = client.post("/v1/auth/login", json=payload)
    assert first.status_code == 200, first.text

    second = client.post("/v1/auth/login", json=payload)
    assert second.status_code == 429
    assert "Слишком много запросов" in second.text


def test_refresh_rate_limit_returns_429(monkeypatch) -> None:
    monkeypatch.setattr(
        auth_router,
        "REFRESH_RATE_RULE",
        RateLimitRule(max_requests=1, window_seconds=60),
    )
    client = _client()

    login = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin12345",
            "session_fingerprint": "limit-refresh",
        },
    )
    assert login.status_code == 200, login.text
    refresh_token = login.json()["refresh_token"]

    first = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert first.status_code == 200, first.text

    second = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert second.status_code == 429
    assert "Слишком много запросов" in second.text
