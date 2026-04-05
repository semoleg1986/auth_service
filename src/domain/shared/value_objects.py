"""Общие value objects домена."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.errors import ValidationError


@dataclass(frozen=True, slots=True)
class Email:
    """Email пользователя.

    :param value: Адрес электронной почты.
    :type value: str
    :raises ValidationError: Если email пустой или не содержит '@'.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized or "@" not in normalized:
            raise ValidationError("Некорректный email адрес.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class PasswordHash:
    """Хэш пароля."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValidationError("Хэш пароля не может быть пустым.")


@dataclass(frozen=True, slots=True)
class Role:
    """Роль пользователя в платформе."""

    value: str

    def __post_init__(self) -> None:
        allowed = {"admin", "teacher", "parent", "student"}
        role_value = self.value.strip().lower()
        if role_value not in allowed:
            raise ValidationError("Недопустимая роль пользователя.")
        object.__setattr__(self, "value", role_value)
