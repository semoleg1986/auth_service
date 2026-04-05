"""Value objects identity/account."""

from dataclasses import dataclass

from src.domain.errors import ValidationError


@dataclass(frozen=True, slots=True)
class UserAgent:
    """User-Agent клиента."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValidationError("User-Agent не может быть пустым.")
