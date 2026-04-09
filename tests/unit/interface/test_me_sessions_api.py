from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.wiring import get_runtime, get_token_issuer


def _client() -> TestClient:
    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    os.environ.pop("AUTH_DATABASE_URL", None)
    get_runtime.cache_clear()
    return TestClient(create_app())


def _auth_token(client: TestClient) -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "me1@example.com", "password": "pass-12345", "default_role": "parent"},
    )
    assert register.status_code == 200

    login = client.post(
        "/v1/auth/login",
        json={"email": "me1@example.com", "password": "pass-12345", "session_fingerprint": "fp-me"},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def test_me_and_sessions_success() -> None:
    client = _client()
    token = _auth_token(client)

    me = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "me1@example.com"

    sessions = client.get("/v1/auth/sessions", headers={"Authorization": f"Bearer {token}"})
    assert sessions.status_code == 200
    assert len(sessions.json()["items"]) >= 1


class _EmptySubTokenIssuer:
    def decode_access(self, _: str) -> dict[str, str]:
        return {"sub": ""}


def test_me_and_sessions_reject_empty_sub_claim() -> None:
    app = create_app()
    app.dependency_overrides[get_token_issuer] = lambda: _EmptySubTokenIssuer()
    client = TestClient(app)

    me = client.get("/v1/auth/me", headers={"Authorization": "Bearer any"})
    assert me.status_code == 401

    sessions = client.get("/v1/auth/sessions", headers={"Authorization": "Bearer any"})
    assert sessions.status_code == 401
