"""HTTP client for users_service onboarding invite internal API."""

from __future__ import annotations

import json
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.application.ports.student_invite_consumer import ConsumedStudentInvite
from src.domain.errors import InvariantViolationError


class UsersServiceStudentInviteClient:
    """Consumes onboarding invite tokens through users_service."""

    def __init__(
        self, *, base_url: str, service_token: str, timeout_seconds: float
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_token = service_token
        self._timeout_seconds = timeout_seconds

    def consume(self, *, token: str, consumer: str) -> ConsumedStudentInvite:
        body = json.dumps({"token": token, "consumer": consumer}).encode("utf-8")
        request = Request(
            f"{self._base_url}/internal/v1/invites/consume",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Service-Token": self._service_token,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = self._extract_error_detail(exc)
            raise InvariantViolationError(detail) from exc
        except (TimeoutError, URLError) as exc:
            raise InvariantViolationError("users_service недоступен.") from exc

        return ConsumedStudentInvite(
            invite_id=str(payload["invite_id"]),
            invite_type=str(payload["invite_type"]),
            user_id=str(payload["user_id"]),
            email=str(payload["email"]),
            roles=[str(role) for role in payload["roles"]],
            consumed_at=datetime.fromisoformat(
                str(payload["consumed_at"]).replace("Z", "+00:00")
            ),
        )

    @staticmethod
    def _extract_error_detail(exc: HTTPError) -> str:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return "student invite не может быть принят."
        detail = payload.get("detail") or payload.get("title") or payload.get("message")
        return str(detail or "student invite не может быть принят.")
