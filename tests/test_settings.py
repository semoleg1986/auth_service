from __future__ import annotations

import os

from src.infrastructure.config.settings import Settings


def test_settings_read_jwt_contract_from_env() -> None:
    os.environ["AUTH_DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/auth_service"
    os.environ["AUTH_USE_INMEMORY"] = "0"
    os.environ["AUTH_AUTO_CREATE_SCHEMA"] = "1"
    os.environ["AUTH_JWT_ISSUER"] = "auth_service_prod"
    os.environ["AUTH_JWT_PRIVATE_KEY_PEM"] = "PRIVATE_KEY_PEM"
    os.environ["AUTH_JWT_PUBLIC_KEY_PEM"] = "PUBLIC_KEY_PEM"
    os.environ["AUTH_JWT_ACCESS_TTL_SECONDS"] = "900"
    os.environ["AUTH_JWT_REFRESH_TTL_SECONDS"] = "1209600"

    settings = Settings.from_env()

    assert settings.database_url.endswith("/auth_service")
    assert settings.use_inmemory is False
    assert settings.auto_create_schema is True
    assert settings.jwt_issuer == "auth_service_prod"
    assert settings.jwt_private_key_pem == "PRIVATE_KEY_PEM"
    assert settings.jwt_public_key_pem == "PUBLIC_KEY_PEM"
    assert settings.jwt_access_ttl_seconds == 900
    assert settings.jwt_refresh_ttl_seconds == 1209600
