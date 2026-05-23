from __future__ import annotations

from fastapi.testclient import TestClient

from src.application.session.commands.dto import AcceptStudentInviteCommand
from src.interface.http.app import create_app
from src.interface.http.wiring import get_facade


class _FakeFacade:
    def execute(self, command: object) -> dict[str, str]:
        assert isinstance(command, AcceptStudentInviteCommand)
        assert command.token == "invite-token-123456"
        assert command.password == "student-pass-123"
        return {
            "account_id": "account-1",
            "user_id": "student-user-1",
            "email": "student@example.com",
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
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "account_id": "account-1",
        "user_id": "student-user-1",
        "email": "student@example.com",
    }
