from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def _database_url() -> str:
    return os.getenv(
        "AUTH_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/auth_service_test",
    )


@pytest.fixture(scope="session", autouse=True)
def prepare_postgres_schema() -> None:
    os.environ["AUTH_USE_INMEMORY"] = "0"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "0"
    database_url = _database_url()
    os.environ["AUTH_DATABASE_URL"] = database_url

    try:
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"Postgres недоступен для integration tests: {exc}")

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    database_url = _database_url()
    engine = create_engine(database_url, future=True, pool_pre_ping=True)
    with engine.begin() as conn:
        try:
            conn.execute(text("TRUNCATE TABLE refresh_tokens RESTART IDENTITY CASCADE"))
            conn.execute(text("TRUNCATE TABLE auth_sessions RESTART IDENTITY CASCADE"))
            conn.execute(text("TRUNCATE TABLE accounts RESTART IDENTITY CASCADE"))
        except SQLAlchemyError:
            conn.execute(text("DELETE FROM refresh_tokens"))
            conn.execute(text("DELETE FROM auth_sessions"))
            conn.execute(text("DELETE FROM accounts"))
