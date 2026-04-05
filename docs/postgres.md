# PostgreSQL: запуск auth_service

## 1. URL подключения

Используйте переменную окружения `AUTH_DATABASE_URL`:

```bash
export AUTH_DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/auth_service'
```

`auth_service` и Alembic читают этот URL из окружения.

## 2. Миграции

Применить миграции:

```bash
make migrate-up
```

Откатить последнюю миграцию:

```bash
make migrate-down-1
```

## 3. Локальный запуск API

```bash
export AUTH_USE_INMEMORY=0
uvicorn src.interface.http.main:app --reload
```

Опционально для dev можно включить автосоздание схемы (в дополнение к миграциям):

```bash
export AUTH_AUTO_CREATE_SCHEMA=1
```

## 4. Проверка готовности

- Драйвер PostgreSQL: `psycopg[binary]`
- ORM и миграции: `SQLAlchemy + Alembic`
- Источник URL: `AUTH_DATABASE_URL` (fallback: `DATABASE_URL`, затем `alembic.ini`)

## 4.1 JWT конфигурация (контракт env)

`auth_service` читает JWT параметры из окружения:

- `AUTH_JWT_ISSUER` (по умолчанию `auth_service`)
- `AUTH_JWT_ACCESS_TTL_SECONDS` (по умолчанию `3600`)
- `AUTH_JWT_REFRESH_TTL_SECONDS` (по умолчанию `2592000`)
- `AUTH_JWT_PRIVATE_KEY_PEM` (опционально)
- `AUTH_JWT_PUBLIC_KEY_PEM` (опционально)

Если `AUTH_JWT_PRIVATE_KEY_PEM` не задан, сервис сгенерирует runtime-ключи.  
Для production рекомендуется всегда задавать стабильную пару ключей через env.

## 5. Интеграционные тесты (Postgres)

Перед запуском создайте тестовую БД:

```bash
docker exec curs_postgres psql -U postgres -d postgres -c "CREATE DATABASE auth_service_test;"
```

Запуск интеграционных тестов:

```bash
AUTH_DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/auth_service_test' make test-integration
```

Если Postgres недоступен, integration tests будут помечены как `skipped`.
