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
