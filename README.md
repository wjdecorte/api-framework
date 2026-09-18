# API Framework

A reusable Python API framework built on established libraries and conventions. It provides a layered FastAPI application with database migrations, structured logging, centralized error handling, and a reference `user` domain module that demonstrates how to extend the framework for new services.

Managed with [uv](https://docs.astral.sh/uv/), formatted and linted with [ruff](https://docs.astral.sh/ruff/).

## Tech Stack

| Layer | Library |
|-------|---------|
| Web framework | FastAPI |
| Validation & settings | Pydantic, Pydantic Settings |
| ORM & models | SQLModel (SQLAlchemy + Pydantic) |
| Migrations | Alembic |
| Database driver | psycopg2 (PostgreSQL) |
| ASGI server | Uvicorn (via Gunicorn + uvicorn-worker) |
| HTTP client (tests) | httpx |
| Logging | Python `logging` with dictionary config and optional JSON output |
| Testing | pytest, pytest-asyncio, testcontainers |

Requires **Python 3.13+**.

## Architecture

The application follows a **modular, layered architecture**. Each domain (e.g. `user`) is a self-contained package with its own routers, services, models, schemas, and exceptions. Shared infrastructure lives under `common/`.

```mermaid
flowchart TB
    subgraph Client
        HTTP[HTTP Client]
    end

    subgraph FastAPI["FastAPI Application (app.py)"]
        MW[LogRoute Middleware]
        EH[Global Exception Handler]
        CR[Common Router]
        UR[User Router]
    end

    subgraph Domain["Domain Layer (e.g. user/)"]
        R[Routers]
        S[Services]
        SCH[Schemas]
        M[Models]
        EX[Exceptions]
    end

    subgraph Infra["Infrastructure"]
        DEP[Dependencies / Session]
        CFG[Settings]
        MIG[Alembic Migrations]
        LOG[Logger Config]
    end

    DB[(PostgreSQL)]

    HTTP --> MW
    MW --> CR & UR
    CR & UR --> R
    R --> S
    S --> M
    R --> SCH
    S --> EX
    R --> DEP
    DEP --> DB
    MIG --> DB
    EH --> HTTP
    CFG --> FastAPI
    LOG --> FastAPI
```

### Request lifecycle

1. **Router** — Receives the HTTP request, validates input via Pydantic schemas, and injects dependencies (`Session`, `CommonHeaders`).
2. **Service** — Contains business logic and database operations. Routers stay thin; services own queries and transactions.
3. **Model** — SQLModel table definitions backed by PostgreSQL. Models inherit from `AppBaseModel` for shared columns and naming conventions.
4. **Schema** — API request/response DTOs with camelCase serialization for external clients and snake_case internally.
5. **Exception** — Domain-specific errors subclass `AppBaseError` or `CommonBaseError` and are converted to a consistent JSON error envelope by the global handler.

### Cross-cutting concerns

- **Logging** — `LogRoute` middleware logs request/response metadata (method, path, status, `x-*` headers, bodies) as a background task. Log format is configurable as standard text or JSON via `API_LOG_TYPE`.
- **Error handling** — All known exceptions are registered in `ALL_EXCEPTIONS` and return `{ "errors": [{ "type", "code", "message", "http_code" }] }`. Unknown exceptions return a 500 with a traceback in debug scenarios.
- **Migrations** — Alembic runs automatically on application startup (`lifespan` in `app.py`). Schema versioning is stored in the `common` schema.
- **Naming** — API payloads use camelCase (`alias_generator=to_camel`); database tables use snake_case derived from class names.

## Project Structure

```
api_framework/
├── app.py                  # FastAPI app, router registration, exception handler, lifespan
├── __init__.py             # Pydantic Settings (app_settings)
├── exceptions.py           # Base exception hierarchy and registry
├── logger_conf.py          # Dictionary logging configuration
├── gunicorn_config.py      # Gunicorn worker settings
├── common/
│   ├── dependencies.py     # DB engine, session factory, CommonHeaders
│   ├── middleware.py       # LogRoute request/response logging
│   ├── models.py           # AppBaseModel (id, timestamps, table naming)
│   ├── routers.py          # Healthcheck and info endpoints
│   ├── schemas.py          # AppBaseSchema, ValidationErrorSchema
│   └── exceptions.py         # CommonBaseError
├── user/                   # Reference domain module
│   ├── routers.py          # CRUD endpoints for users
│   ├── services.py         # UserService business logic
│   ├── models.py           # User, UserAddress tables (user_example schema)
│   ├── schemas.py          # UserSchema, UserAddressSchema
│   └── exceptions.py       # UserDoesNotExistError, UserAlreadyExistError
├── block/
│   └── models.py           # Document/block models (not yet wired to routers)
├── migrations/
│   ├── alembic.ini
│   ├── env.py              # Alembic environment; imports models for autogenerate
│   ├── alembic_runner.py   # upgrade / downgrade / generate_revision helpers
│   └── versions/           # Migration scripts
└── interfaces/             # Extension point for external integrations

tests/
├── conftest.py             # Fixtures (TestClient, Postgres testcontainer)
├── common/                 # Common router tests
├── users/                  # User service and router tests
└── http-client/            # Sample .http requests for manual testing
```

## API Endpoints

All routes are prefixed with `/framework/api/v1` (configurable via `BASE_URL_PREFIX`).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/common/healthcheck` | Liveness probe |
| GET | `/common/info` | Non-sensitive application settings |
| GET | `/user/healthcheck` | User module healthcheck |
| POST | `/user/create` | Create a user with addresses |
| PUT | `/user/update` | Update an existing user |
| GET | `/user/` | List users (optional `?search=` filter) |
| GET | `/user/{username}` | Get a single user |
| DELETE | `/user/delete/{username}` | Delete a user |

Interactive docs are available at `/framework/api/v1/docs` (Swagger) and `/framework/api/v1/redoc`.

## Configuration

Settings are loaded from environment variables via Pydantic Settings (`api_framework/__init__.py`). Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `test` | SQLAlchemy connection URL; use `{pswd}` placeholder for password |
| `DATABASE_PASSWORD` | `<PASSWORD>` | Substituted into `DATABASE_URL` |
| `DATABASE_DEFAULT_SCHEMA` | `common` | Schema for Alembic version table |
| `BASE_URL_PREFIX` | `/framework/api/v1` | API route prefix |
| `DEBUG_MODE` | `false` | Enables DEBUG log level when true |
| `API_LOG_TYPE` | `json` | Log format: `json` or `standard` |
| `LOG_LEVEL` | `INFO` | Root log level |
| `LOGGER_NAME` | `api-logger` | Application logger name |
| `WORKERS` | `1` | Gunicorn worker count |

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL (or use Docker Compose below)

### Install dependencies

```bash
uv sync
```

### Run locally with Docker Compose

Starts PostgreSQL and the API service:

```bash
docker compose up
```

The API is available at `http://localhost:8282`. PostgreSQL is exposed on port `5440`.

### Run locally without Docker

```bash
export DATABASE_URL="postgresql+psycopg2://api:{pswd}@localhost:5440/api"
export DATABASE_PASSWORD="api"

uv run gunicorn --config api_framework/gunicorn_config.py 'api_framework.app:app' --reload
```

Or with uvicorn directly for development:

```bash
uv run uvicorn api_framework.app:app --reload --port 9000
```

### Run tests

```bash
uv run pytest
```

Tests use [testcontainers](https://testcontainers.com/) to spin up a disposable PostgreSQL instance. Coverage omits boilerplate files (migrations, app entrypoint, middleware).

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

Hooks run ruff (lint + format), file hygiene checks, and commitizen for conventional commits.

## Database Migrations

Migrations run automatically on app startup. To create a new revision manually:

```bash
DATABASE_URL="postgresql+psycopg2://api:api@0.0.0.0:5440/api" \
  alembic --config api_framework/migrations/alembic.ini revision --autogenerate -m "your message"
```

Ensure new SQLModel tables are imported in `api_framework/migrations/env.py` so Alembic can detect them.

## Adding a New Domain Module

1. Create a package under `api_framework/` (e.g. `orders/`).
2. Define models inheriting from `AppBaseModel` with an appropriate `__table_args__` schema.
3. Add Pydantic schemas inheriting from `AppBaseSchema`.
4. Implement a service class that accepts a `Session` and contains business logic.
5. Create an `APIRouter` with `route_class=LogRoute` and register it in `app.py`.
6. Add domain exceptions subclassing `AppBaseError` or `CommonBaseError`.
7. Import models in `migrations/env.py` and generate an Alembic revision.

## Production Deployment

The `Dockerfile` builds a slim Python 3.13 image using uv for dependency installation. Gunicorn serves the app with `uvicorn_worker.UvicornWorker`. Sample GitHub Actions workflows for testing and deployment are in `github_workflow_samples/`.
