# Error Format

`auth_service` returns HTTP errors as RFC7807 `application/problem+json`.

## Fields

- `type`
- `title`
- `status`
- `detail`
- `instance`
- `request_id`
- `correlation_id`

`X-Request-ID` and `X-Correlation-ID` are also returned as response headers when
available.

## Common Types

- `/problems/validation` -> `422`
- `/problems/unauthorized` -> `401`
- `/problems/access-denied` -> `403`
- `/problems/not-found` -> `404`
- `/problems/conflict` -> `409`

## Example

```json
{
  "type": "https://api.example.com/problems/unauthorized",
  "title": "Не авторизован",
  "status": 401,
  "detail": "Требуется Bearer токен.",
  "instance": "/v1/auth/me",
  "request_id": "req-123",
  "correlation_id": "corr-123"
}
```
