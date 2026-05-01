"""Handler аутентификации пользователя."""

from __future__ import annotations

from datetime import timedelta

from src.application.common.dto import TokenResult
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.token_issuer import AccessTokenPayload, TokenIssuer
from src.application.ports.unit_of_work import UnitOfWork
from src.application.session.commands.dto import LoginCommand
from src.domain.errors import AccessDeniedError
from src.domain.session.auth_session.entity import AuthSession
from src.domain.shared.statuses import AccountStatus
from src.domain.token.refresh_token.entity import RefreshToken


class LoginHandler:
    """Выполняет вход пользователя и выдает токены."""

    def __init__(
        self,
        *,
        uow: UnitOfWork,
        clock: Clock,
        id_generator: IdGenerator,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator
        self._password_hasher = password_hasher
        self._token_issuer = token_issuer
        self._access_ttl_seconds = access_ttl_seconds
        self._refresh_ttl_seconds = refresh_ttl_seconds

    def __call__(self, command: LoginCommand) -> TokenResult:
        account = self._uow.repositories.accounts.get_by_email(
            command.email.strip().lower()
        )
        if account is None:
            raise AccessDeniedError("Неверный email или пароль.")
        if account.status != AccountStatus.ACTIVE:
            raise AccessDeniedError("Аккаунт недоступен для входа.")
        if not self._password_hasher.verify(
            command.password, account.password_hash.value
        ):
            raise AccessDeniedError("Неверный email или пароль.")

        now = self._clock.now()
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
            auth_method=command.auth_method,
            mfa_used=command.mfa_used,
            is_trusted=command.is_trusted,
            risk_level=command.risk_level,
            session_fingerprint=command.session_fingerprint,
            last_path=command.last_path,
            last_action=command.last_action,
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

        self._uow.repositories.sessions.add(session)
        self._uow.repositories.refresh_tokens.add(refresh)
        self._uow.commit()

        return TokenResult(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type="Bearer",
            expires_in=self._access_ttl_seconds,
        )
