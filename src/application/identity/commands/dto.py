"""Команды identity use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterAccountCommand:
    """Команда регистрации учетной записи."""

    email: str
    password: str
    default_role: str


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    """Команда смены пароля."""

    account_id: str
    new_password: str
