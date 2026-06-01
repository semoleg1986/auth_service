# auth_service

Identity and authentication service for the platform.

## Responsibility

`auth_service` owns:
- account registration
- login and logout
- access and refresh tokens
- JWKS publication
- auth session lifecycle

It does not own parent/student domain profiles or relationships.

## Local run

### Install
```bash
make install
```

### Run with uvicorn
```bash
uvicorn src.interface.http.main:app --host 0.0.0.0 --port 8000 --reload
```

### Health
```bash
curl -fsS http://127.0.0.1:8000/healthz
```

## Environment

Base variables live in:
- [auth_service/.env.example](/Users/olegsemenov/Programming/curs/auth_service/.env.example)
- [auth_service/.env.local.example](/Users/olegsemenov/Programming/curs/auth_service/.env.local.example)

Key variables:
- `AUTH_DATABASE_URL`
- `AUTH_USE_INMEMORY`
- `AUTH_JWT_ISSUER`
- `AUTH_JWT_AUDIENCE`
- `AUTH_JWT_PRIVATE_KEY_PEM`
- `AUTH_JWT_PUBLIC_KEY_PEM`

## Tests and quality

```bash
make test
make test-integration
make lint
make format
```

## Migrations

```bash
make migrate-up
make migrate-down-1
```

## Documentation

- [ERROR_FORMAT.md](/Users/olegsemenov/Programming/curs/auth_service/docs/ERROR_FORMAT.md)
- [JWT_CONTRACT.md](/Users/olegsemenov/Programming/curs/auth_service/docs/JWT_CONTRACT.md)
- [postgres.md](/Users/olegsemenov/Programming/curs/auth_service/docs/postgres.md)
