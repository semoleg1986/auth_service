"""Handler регистрации учетной записи."""

from __future__ import annotations

from src.application.session.commands.dto import RegisterCommand
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.unit_of_work import UnitOfWork
from src.domain.errors import InvariantViolationError
from src.domain.identity.account.entity import Account
from src.domain.shared.value_objects import Email, PasswordHash, Role


class RegisterHandler:
    """Регистрирует новый аккаунт пользователя."""

    def __init__(
        self,
        *,
        uow: UnitOfWork,
        clock: Clock,
        id_generator: IdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator
        self._password_hasher = password_hasher

    def __call__(self, command: RegisterCommand) -> dict[str, str]:
        email = Email(command.email)
        existing = self._uow.repositories.accounts.get_by_email(email.value)
        if existing is not None:
            raise InvariantViolationError("Аккаунт с таким email уже существует.")

        now = self._clock.now()
        account = Account.register(
            account_id=self._id_generator.new(),
            user_id=self._id_generator.new(),
            email=email,
            password_hash=PasswordHash(self._password_hasher.hash(command.password)),
            default_role=Role(command.default_role),
            now=now,
        )
        self._uow.repositories.accounts.add(account)
        self._uow.commit()
        return {"account_id": account.aggregate_id, "user_id": account.user_id}
