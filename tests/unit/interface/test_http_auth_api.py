from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.common.rate_limit import reset_rate_limiter
from src.interface.http.observability import reset_metrics
from src.interface.http.wiring import get_runtime


def test_login_returns_token_pair_for_demo_admin() -> None:
    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    os.environ.pop("AUTH_DATABASE_URL", None)
    reset_metrics()
    reset_rate_limiter()
    get_runtime.cache_clear()

    client = TestClient(create_app())
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin12345",
            "session_fingerprint": "http-test",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert (
        response.headers.get("Permissions-Policy")
        == "camera=(), microphone=(), geolocation=()"
    )

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text
    assert "http_request_duration_seconds" in metrics.text
    assert "http_errors_total" in metrics.text
    assert 'auth_login_success_total{auth_method="password"} 1' in metrics.text


def test_metrics_requires_token_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_METRICS_TOKEN", "metrics-secret")
    os.environ["AUTH_USE_INMEMORY"] = "1"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    os.environ.pop("AUTH_DATABASE_URL", None)
    reset_metrics()
    reset_rate_limiter()
    get_runtime.cache_clear()

    client = TestClient(create_app())
    denied = client.get("/metrics")
    assert denied.status_code == 401

    allowed = client.get(
        "/metrics",
        headers={"Authorization": "Bearer metrics-secret"},
    )
    assert allowed.status_code == 200
