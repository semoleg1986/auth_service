"""Мапперы Account <-> AccountModel."""

from __future__ import annotations

from src.domain.identity.account.entity import Account
from src.domain.shared.statuses import AccountStatus
from src.domain.shared.value_objects import Email, PasswordHash, Role
from src.infrastructure.db.sqlalchemy.models import AccountModel


def serialize_roles(roles: set[Role]) -> str:
    """Сериализует роли в строку для хранения."""

    return ",".join(sorted(role.value for role in roles))


def deserialize_roles(value: str) -> set[Role]:
    """Десериализует роли из строки хранения."""

    if not value.strip():
        return set()
    return {Role(item.strip()) for item in value.split(",") if item.strip()}


def to_model(account: Account) -> AccountModel:
    """Преобразует доменную сущность в ORM-модель."""

    return AccountModel(
        id=account.aggregate_id,
        user_id=account.user_id,
        email=account.email.value,
        password_hash=account.password_hash.value,
        roles=serialize_roles(account.roles),
        status=account.status.value,
        created_at=account.created_at,
        updated_at=account.updated_at,
        version=account.version,
    )


def to_entity(model: AccountModel) -> Account:
    """Преобразует ORM-модель в доменную сущность."""

    return Account(
        aggregate_id=model.id,
        user_id=model.user_id,
        email=Email(model.email),
        password_hash=PasswordHash(model.password_hash),
        roles=deserialize_roles(model.roles),
        status=AccountStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
        version=model.version,
    )


def copy_to_model(account: Account, model: AccountModel) -> None:
    """Копирует поля доменной сущности в ORM-модель."""

    model.user_id = account.user_id
    model.email = account.email.value
    model.password_hash = account.password_hash.value
    model.roles = serialize_roles(account.roles)
    model.status = account.status.value
    model.created_at = account.created_at
    model.updated_at = account.updated_at
    model.version = account.version
