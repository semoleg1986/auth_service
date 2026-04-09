# JWT Contract (`auth_service`)

## Access token
- `alg`: `EdDSA` (Ed25519)
- `iss`: значение `AUTH_JWT_ISSUER`
- `aud`: значение `AUTH_JWT_AUDIENCE`
- `typ`: `access`
- Обязательные claims:
  - `sub` (account_id)
  - `jti` (token id)
  - `roles` (непустой массив ролей)
  - `iat`
  - `exp`

## Refresh token
- `alg`: `EdDSA` (Ed25519)
- `iss`: значение `AUTH_JWT_ISSUER`
- `aud`: значение `AUTH_JWT_AUDIENCE`
- `typ`: `refresh`
- Обязательные claims:
  - `token_id`
  - `account_id`
  - `session_id`
  - `iat`
  - `exp`

## JWKS
- Публичный ключ публикуется на:
  - `GET /.well-known/jwks.json`
- Формат ключа:
  - `kty=OKP`
  - `crv=Ed25519`
  - `alg=EdDSA`
  - `use=sig`
  - `kid=<stable key id>`

## Env
- `AUTH_JWT_ISSUER`
- `AUTH_JWT_AUDIENCE`
- `AUTH_JWT_PRIVATE_KEY_PEM`
- `AUTH_JWT_PUBLIC_KEY_PEM`
- `AUTH_JWT_ACCESS_TTL_SECONDS`
- `AUTH_JWT_REFRESH_TTL_SECONDS`
