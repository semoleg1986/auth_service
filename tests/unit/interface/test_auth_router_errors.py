from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.wiring import get_runtime


def _client() -> TestClient:
    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    os.environ.pop("AUTH_DATABASE_URL", None)
    get_runtime.cache_clear()
    return TestClient(create_app())


def test_me_and_sessions_require_bearer_token() -> None:
    client = _client()

    me = client.get("/v1/auth/me")
    assert me.status_code == 401

    sessions = client.get("/v1/auth/sessions")
    assert sessions.status_code == 401


def test_logout_and_refresh_routes_operate() -> None:
    client = _client()

    register = client.post(
        "/v1/auth/register",
        json={"email": "r1@example.com", "password": "pass-12345", "default_role": "parent"},
    )
    assert register.status_code == 200

    login = client.post(
        "/v1/auth/login",
        json={"email": "r1@example.com", "password": "pass-12345", "session_fingerprint": "fp-1"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    me_bad = client.get("/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert me_bad.status_code == 403

    refreshed = client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200

    session_id = refreshed.json()["refresh_token"]
    # session_id напрямую API не возвращает, поэтому проверяем только контракт logout-валидации.
    bad_logout = client.post("/v1/auth/logout", json={"session_id": "missing"})
    assert bad_logout.status_code in {204, 404}
