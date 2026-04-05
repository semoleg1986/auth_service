"""Агрегат учетной записи пользователя."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.errors import InvariantViolationError
from src.domain.identity.account.events import (
    AccountBlocked,
    AccountPasswordChanged,
    AccountRegistered,
    AccountRoleAssigned,
)
from src.domain.shared.entity import AggregateRoot
from src.domain.shared.statuses import AccountStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role


@dataclass(slots=True)
class Account(AggregateRoot):
    """Корневой агрегат identity контекста.

    :param aggregate_id: Идентификатор аккаунта.
    :type aggregate_id: str
    :param user_id: Внешний идентификатор пользователя.
    :type user_id: str
    :param email: Email value object.
    :type email: Email
    :param password_hash: Хэш пароля.
    :type password_hash: PasswordHash
    :param roles: Набор назначенных ролей.
    :type roles: set[Role]
    :param status: Статус аккаунта.
    :type status: AccountStatus
    """

    user_id: str
    email: Email
    password_hash: PasswordHash
    roles: set[Role] = field(default_factory=set)
    status: AccountStatus = AccountStatus.ACTIVE

    @classmethod
    def register(
        cls,
        *,
        account_id: str,
        user_id: str,
        email: Email,
        password_hash: PasswordHash,
        default_role: Role,
        now: datetime,
    ) -> "Account":
        """Создает новый аккаунт и поднимает событие регистрации."""

        account = cls(
            aggregate_id=account_id,
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            roles={default_role},
            status=AccountStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        account._raise_event(
            AccountRegistered(account_id=account_id, user_id=user_id, occurred_at=now)
        )
        return account

    def assign_role(self, *, role: Role, now: datetime) -> None:
        """Назначает роль аккаунту."""

        if self.status == AccountStatus.ARCHIVED:
            raise InvariantViolationError("Нельзя назначить роль архивному аккаунту.")
        if role in self.roles:
            return
        self.roles.add(role)
        self.touch(now)
        self._raise_event(
            AccountRoleAssigned(account_id=self.aggregate_id, role=role.value, occurred_at=now)
        )

    def revoke_role(self, *, role: Role, now: datetime) -> None:
        """Снимает роль с аккаунта."""

        if role not in self.roles:
            return
        if len(self.roles) == 1:
            raise InvariantViolationError("Нельзя удалить последнюю роль аккаунта.")
        self.roles.remove(role)
        self.touch(now)

    def change_password(self, *, password_hash: PasswordHash, now: datetime) -> None:
        """Обновляет хэш пароля."""

        if self.status == AccountStatus.ARCHIVED:
            raise InvariantViolationError("Нельзя изменить пароль архивного аккаунта.")
        self.password_hash = password_hash
        self.touch(now)
        self._raise_event(
            AccountPasswordChanged(account_id=self.aggregate_id, occurred_at=now)
        )

    def block(self, *, now: datetime) -> None:
        """Блокирует аккаунт."""

        if self.status == AccountStatus.ARCHIVED:
            raise InvariantViolationError("Нельзя блокировать архивный аккаунт.")
        if self.status == AccountStatus.BLOCKED:
            return
        self.status = AccountStatus.BLOCKED
        self.touch(now)
        self._raise_event(AccountBlocked(account_id=self.aggregate_id, occurred_at=now))

    def unblock(self, *, now: datetime) -> None:
        """Разблокирует аккаунт."""

        if self.status == AccountStatus.ARCHIVED:
            raise InvariantViolationError("Нельзя разблокировать архивный аккаунт.")
        if self.status == AccountStatus.ACTIVE:
            return
        self.status = AccountStatus.ACTIVE
        self.touch(now)

    def archive(self, *, now: datetime) -> None:
        """Архивирует аккаунт."""

        if self.status == AccountStatus.ARCHIVED:
            return
        self.status = AccountStatus.ARCHIVED
        self.touch(now)
