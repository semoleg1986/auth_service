from src.application.identity.commands.dto import (
    ChangePasswordCommand,
    RegisterAccountCommand,
)
from src.application.token.queries.dto import GetRefreshTokenByIdQuery


def test_identity_command_dto_instantiation() -> None:
    register = RegisterAccountCommand(
        email="user@example.com",
        password="pwd-12345",
        default_role="parent",
    )
    assert register.default_role == "parent"

    change = ChangePasswordCommand(account_id="acc-1", new_password="new-123")
    assert change.account_id == "acc-1"


def test_token_query_dto_instantiation() -> None:
    query = GetRefreshTokenByIdQuery(token_id="rt-1")
    assert query.token_id == "rt-1"
