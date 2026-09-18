# Digital Waitlist — Backend

FastAPI backend for the Digital Waitlist pilot: guests join a restaurant's
waitlist and track their position; hosts manage the queue from a shared
tablet. See `../specs/001-digital-waitlist/` for the spec, plan, and tasks.

This is a **local-only demo** — no Docker, no cloud. SQLite is the database,
managed through Alembic migrations and a repository/service layer.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the Python version, virtualenv,
  and dependencies; nothing else needs to be installed separately.
- `make` — optional. It's just a thin wrapper around `uv run ...` commands;
  every target has a raw equivalent below if you don't have it (or are on
  Windows without it installed).

## Quick start

```
cp .env.example .env      # defaults are already fine for local dev
make migrate               # create waitlist.db and apply the schema
make seed                  # seed the single pilot restaurant
make dev                    # start the API with hot reload
```

No `make`? Run the same three steps directly:

```
cp .env.example .env
uv run alembic upgrade head
uv run python -m app.seed
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The app is served at http://localhost:8000. Edit any file under `app/` and
uvicorn's `--reload` picks it up automatically — no restart needed.

## Common commands

| `make` target | Without `make` | What it does |
| --- | --- | --- |
| `make dev` | `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | Run the API locally with hot reload |
| `make seed` | `uv run python -m app.seed` | Insert the single pilot restaurant |
| `make migrate` | `uv run alembic upgrade head` | Apply database migrations |
| `make makemigrations m="message"` | `uv run alembic revision --autogenerate -m "message"` | Generate a new migration from model changes |
| `make test` | `uv run pytest` | Run the test suite (`pytest`) |
| `make lint` | `uv run ruff check . && uv run ruff format --check . && uv run mypy .` | Run ruff + mypy checks |
| `make fmt` | `uv run ruff check --fix . && uv run ruff format .` | Auto-fix lint/format issues |
| `make precommit` | `uv run pre-commit run --all-files` | Run all pre-commit hooks against the whole repo |

(No Makefile target replaces `git commit` — pre-commit hooks run
automatically on commit once `uv run pre-commit install` has been run
against the project's git repo.)

## Environment variables

See `.env.example` for the full list. `.env` itself is gitignored and holds
local config — for this project that's just the SQLite path and a debug
flag, no real secrets.

## Migrations

Schema changes are always an explicit developer action, never automatic on
startup: after changing `app/models.py`, run `make makemigrations
m="describe the change"`, review the generated file under
`alembic/versions/`, then `make migrate`.

## Health checks

- `GET /health` — liveness only, no I/O.
- `GET /ready` — checks the database connection.

## Project structure

```
app/
  main.py            # app factory, health/ready endpoints
  config.py           # Settings (pydantic-settings)
  db.py                # async SQLAlchemy engine/session, SQLite pragmas
  models.py            # Restaurant, WaitlistEntry
  repositories/         # the only layer that touches SQLAlchemy directly
  services/              # business logic, orchestrates repositories
  api/routes/             # FastAPI routers — HTTP only, no business logic
  seed.py                  # one-time seed of the pilot restaurant
alembic/                    # migrations (source of truth for schema)
tests/                        # pytest suite
```
