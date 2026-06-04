# auth_service

Identity and authentication service for the platform.

## Responsibility

`auth_service` owns:
- account registration
- invite acceptance for existing users_service profiles
- login and logout
- access and refresh tokens
- JWKS publication
- auth session lifecycle

It does not own parent/student domain profiles or relationships.

## Invite acceptance

`POST /v1/auth/invites/accept` accepts a one-time onboarding token and creates
an auth account linked to an existing `users_service.user_id`.

Supported invite types are resolved by `users_service` through the internal
endpoint `POST /internal/v1/invites/consume`:

- `student` -> roles `student`
- `staff` -> roles from the invite, for example `teacher` or `content_manager`

Invariant: `auth_service` must not generate a new domain `user_id` during invite
acceptance. The account `user_id` is always the `user_id` returned by
`users_service`.

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
