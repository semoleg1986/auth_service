"""Handler обновления токенов."""

from __future__ import annotations

from datetime import timedelta

from src.application.common.dto import TokenResult
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.token_issuer import AccessTokenPayload, TokenIssuer
from src.application.ports.unit_of_work import UnitOfWork
from src.application.token.commands.dto import RefreshCommand
from src.domain.errors import AccessDeniedError, NotFoundError
from src.domain.shared.statuses import AccountStatus
from src.domain.token.refresh_token.entity import RefreshToken


class RefreshHandler:
    """Ротирует refresh token и выдает новую пару токенов."""

    def __init__(
        self,
        *,
        uow: UnitOfWork,
        clock: Clock,
        id_generator: IdGenerator,
        token_issuer: TokenIssuer,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator
        self._token_issuer = token_issuer
        self._access_ttl_seconds = access_ttl_seconds
        self._refresh_ttl_seconds = refresh_ttl_seconds

    def __call__(self, command: RefreshCommand) -> TokenResult:
        now = self._clock.now()
        claims = self._token_issuer.decode_refresh(command.refresh_token)
        token_id = claims.get("token_id")
        if not token_id:
            raise AccessDeniedError("Некорректный refresh token.")

        old_token = self._uow.repositories.refresh_tokens.get_by_id(token_id)
        if old_token is None:
            raise NotFoundError("Refresh token не найден.")
        old_token.ensure_usable(now=now)

        account = self._uow.repositories.accounts.get_by_id(old_token.account_id)
        if account is None:
            raise NotFoundError("Аккаунт не найден.")
        if account.status != AccountStatus.ACTIVE:
            raise AccessDeniedError("Аккаунт недоступен.")

        session = self._uow.repositories.sessions.get_by_id(old_token.session_id)
        if session is None:
            raise NotFoundError("Сессия не найдена.")

        new_token_id = self._id_generator.new()
        access_jti = self._id_generator.new()

        old_token.rotate(new_token_id=new_token_id, now=now)
        new_token = RefreshToken.issue(
            token_id=new_token_id,
            account_id=account.aggregate_id,
            session_id=session.aggregate_id,
            expires_at=now + timedelta(seconds=self._refresh_ttl_seconds),
            now=now,
        )
        session.attach_refresh_token(refresh_token_id=new_token_id, now=now)

        pair = self._token_issuer.issue_pair(
            AccessTokenPayload(
                sub=account.aggregate_id,
                jti=access_jti,
                roles=sorted(role.value for role in account.roles),
                issued_at=now,
                expires_at=now + timedelta(seconds=self._access_ttl_seconds),
            ),
            refresh_claims={
                "token_id": new_token_id,
                "account_id": account.aggregate_id,
                "session_id": session.aggregate_id,
            },
        )

        self._uow.repositories.refresh_tokens.save(old_token)
        self._uow.repositories.refresh_tokens.add(new_token)
        self._uow.repositories.sessions.save(session)
        self._uow.commit()

        return TokenResult(
            access_token=pair.access_token,
            refresh_token=pair.refresh_token,
            token_type="Bearer",
            expires_in=self._access_ttl_seconds,
        )
