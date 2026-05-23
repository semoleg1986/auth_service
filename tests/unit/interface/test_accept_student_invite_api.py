from __future__ import annotations

from fastapi.testclient import TestClient

from src.application.session.commands.dto import AcceptStudentInviteCommand
from src.interface.http.app import create_app
from src.interface.http.wiring import get_facade


class _FakeFacade:
    def execute(self, command: object) -> dict[str, object]:
        assert isinstance(command, AcceptStudentInviteCommand)
        assert command.token == "invite-token-123456"
        assert command.password == "student-pass-123"
        assert command.session_fingerprint == "invite-browser"
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "account_id": "account-1",
                "user_id": "student-user-1",
                "email": "student@example.com",
                "roles": ["student"],
                "status": "active",
            },
        }


def test_accept_student_invite_route_returns_created_account() -> None:
    app = create_app()
    app.dependency_overrides[get_facade] = lambda: _FakeFacade()
    client = TestClient(app)

    response = client.post(
        "/v1/auth/invites/accept",
        json={
            "token": "invite-token-123456",
            "password": "student-pass-123",
            "session_fingerprint": "invite-browser",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "access_token": "access",
        "refresh_token": "refresh",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "account_id": "account-1",
            "user_id": "student-user-1",
            "email": "student@example.com",
            "roles": ["student"],
            "status": "active",
        },
    }
