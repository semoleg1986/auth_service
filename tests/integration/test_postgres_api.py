from __future__ import annotations

import os

import pytest

from src.application.identity.queries.dto import GetMeQuery
from src.application.session.commands.dto import LoginCommand, LogoutCommand, RegisterCommand
from src.application.session.queries.dto import ListSessionsQuery
from src.application.token.commands.dto import RefreshCommand
from src.infrastructure.di.composition import build_runtime

pytestmark = pytest.mark.integration


def _runtime():
    os.environ["AUTH_USE_INMEMORY"] = "0"
    return build_runtime()


def test_postgres_auth_flow() -> None:
    runtime = _runtime()
    facade = runtime.facade

    registered = facade.execute(
        RegisterCommand(
            email="parent-it@example.com",
            password="strong-pass-123",
            default_role="parent",
        )
    )
    assert registered["account_id"]
    assert registered["user_id"]

    login = facade.execute(
        LoginCommand(
            email="parent-it@example.com",
            password="strong-pass-123",
            ip_address="127.0.0.1",
            user_agent_raw=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            device_type="desktop",
            browser_name="chrome",
            session_fingerprint="itest-fingerprint",
        )
    )
    assert login.token_type == "Bearer"
    assert login.access_token
    assert login.refresh_token

    access_claims = runtime.token_issuer.decode_access(login.access_token)
    me = facade.query(GetMeQuery(account_id=str(access_claims["sub"])))
    assert me.email == "parent-it@example.com"
    assert "parent" in me.roles

    sessions = facade.query(ListSessionsQuery(account_id=str(access_claims["sub"])))
    assert len(sessions) == 1
    assert sessions[0].browser_name == "chrome"
    assert sessions[0].device_type == "desktop"
    assert sessions[0].status == "active"

    refreshed = facade.execute(RefreshCommand(refresh_token=login.refresh_token))
    assert refreshed.refresh_token != login.refresh_token

    refresh_claims = runtime.token_issuer.decode_refresh(refreshed.refresh_token)
    facade.execute(
        LogoutCommand(session_id=str(refresh_claims["session_id"]))
    )

    sessions_after = facade.query(ListSessionsQuery(account_id=str(access_claims["sub"])))
    assert len(sessions_after) == 1
    assert sessions_after[0].status == "closed"
