"""Handler accepting a student invite and creating auth account."""

from __future__ import annotations

from datetime import timedelta

from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.student_invite_consumer import StudentInviteConsumer
from src.application.ports.token_issuer import AccessTokenPayload, TokenIssuer
from src.application.ports.unit_of_work import UnitOfWorkFactory
from src.application.session.commands.dto import AcceptStudentInviteCommand
from src.domain.errors import InvariantViolationError
from src.domain.identity.account.entity import Account
from src.domain.session.auth_session.entity import AuthSession
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.domain.token.refresh_token.entity import RefreshToken


class AcceptStudentInviteHandler:
    """Creates a student auth account for an existing users_service profile."""

    def __init__(
        self,
        *,
        uow_factory: UnitOfWorkFactory,
        clock: Clock,
        id_generator: IdGenerator,
        password_hasher: PasswordHasher,
        invite_consumer: StudentInviteConsumer,
        token_issuer: TokenIssuer,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._id_generator = id_generator
        self._password_hasher = password_hasher
        self._invite_consumer = invite_consumer
        self._token_issuer = token_issuer
        self._access_ttl_seconds = access_ttl_seconds
        self._refresh_ttl_seconds = refresh_ttl_seconds

    def __call__(self, command: AcceptStudentInviteCommand) -> dict[str, object]:
        invite = self._invite_consumer.consume(
            token=command.token,
            consumer="auth_service",
        )
        email = Email(invite.email)

        uow = self._uow_factory()
        try:
            existing_by_user = uow.repositories.accounts.get_by_user_id(
                invite.student_user_id
            )
            if existing_by_user is not None:
                raise InvariantViolationError(
                    "Аккаунт для этого student уже существует."
                )

            existing_by_email = uow.repositories.accounts.get_by_email(email.value)
            if existing_by_email is not None:
                raise InvariantViolationError("Аккаунт с таким email уже существует.")

            now = self._clock.now()
            account = Account.register(
                account_id=self._id_generator.new(),
                user_id=invite.student_user_id,
                email=email,
                password_hash=PasswordHash(
                    self._password_hasher.hash(command.password)
                ),
                default_role=Role("student"),
                now=now,
            )
            uow.repositories.accounts.add(account)
            session_id = self._id_generator.new()
            refresh_token_id = self._id_generator.new()
            access_jti = self._id_generator.new()

            session = AuthSession.start(
                session_id=session_id,
                account_id=account.aggregate_id,
                user_id=account.user_id,
                now=now,
                refresh_token_id=refresh_token_id,
                ip_address=command.ip_address,
                user_agent_raw=command.user_agent_raw,
                device_type=command.device_type,
                os_name=command.os_name,
                os_version=command.os_version,
                browser_name=command.browser_name,
                browser_version=command.browser_version,
                client_name=command.client_name,
                country=command.country,
                city=command.city,
                auth_method="password",
                mfa_used=False,
                is_trusted=False,
                risk_level="medium",
                session_fingerprint=command.session_fingerprint,
                last_path="/v1/auth/invites/accept",
                last_action="accept_student_invite",
                expires_at=now + timedelta(seconds=self._refresh_ttl_seconds),
            )
            refresh = RefreshToken.issue(
                token_id=refresh_token_id,
                account_id=account.aggregate_id,
                session_id=session_id,
                expires_at=now + timedelta(seconds=self._refresh_ttl_seconds),
                now=now,
            )
            token_pair = self._token_issuer.issue_pair(
                AccessTokenPayload(
                    sub=account.aggregate_id,
                    jti=access_jti,
                    roles=sorted(role.value for role in account.roles),
                    issued_at=now,
                    expires_at=now + timedelta(seconds=self._access_ttl_seconds),
                    user_id=account.user_id,
                ),
                refresh_claims={
                    "token_id": refresh_token_id,
                    "account_id": account.aggregate_id,
                    "session_id": session_id,
                },
            )

            uow.repositories.sessions.add(session)
            uow.repositories.refresh_tokens.add(refresh)
            uow.commit()

            return {
                "access_token": token_pair.access_token,
                "refresh_token": token_pair.refresh_token,
                "token_type": "Bearer",
                "expires_in": self._access_ttl_seconds,
                "user": {
                    "account_id": account.aggregate_id,
                    "user_id": account.user_id,
                    "email": account.email.value,
                    "roles": sorted(role.value for role in account.roles),
                    "status": account.status.value,
                },
            }
        except Exception:
            uow.rollback()
            raise
        finally:
            close = getattr(uow, "close", None)
            if callable(close):
                close()
