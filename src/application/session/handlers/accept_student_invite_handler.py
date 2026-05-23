"""Handler accepting a student invite and creating auth account."""

from __future__ import annotations

from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.student_invite_consumer import StudentInviteConsumer
from src.application.ports.unit_of_work import UnitOfWorkFactory
from src.application.session.commands.dto import AcceptStudentInviteCommand
from src.domain.errors import InvariantViolationError
from src.domain.identity.account.entity import Account
from src.domain.shared.value_objects import Email, PasswordHash, Role


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
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._id_generator = id_generator
        self._password_hasher = password_hasher
        self._invite_consumer = invite_consumer

    def __call__(self, command: AcceptStudentInviteCommand) -> dict[str, str]:
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
            uow.commit()
            return {
                "account_id": account.aggregate_id,
                "user_id": account.user_id,
                "email": account.email.value,
            }
        except Exception:
            uow.rollback()
            raise
        finally:
            close = getattr(uow, "close", None)
            if callable(close):
                close()
