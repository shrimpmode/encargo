# Digital Waitlist — Backend

FastAPI backend for the Digital Waitlist pilot: guests join a restaurant's
waitlist and track their position; hosts manage the queue from a shared
tablet. See `../specs/001-digital-waitlist/` for the spec, plan, and tasks.

This is a **local-only demo** — no Docker, no cloud. SQLite is the database,
managed through Alembic migrations and a repository/service layer.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the Python version, virtualenv,
  and dependencies; nothing else needs to be installed separately.

## Quick start

```
cp .env.example .env      # defaults are already fine for local dev
make migrate               # create waitlist.db and apply the schema
make seed                  # seed the single pilot restaurant
make dev                    # start the API with hot reload
```

The app is served at http://localhost:8000. Edit any file under `app/` and
uvicorn's `--reload` picks it up automatically — no restart needed.

## Common commands

| Command              | What it does                                      |
| --------------------- | -------------------------------------------------- |
| `make dev`            | Run the API locally with hot reload                 |
| `make seed`           | Insert the single pilot restaurant                  |
| `make migrate`        | Apply database migrations                            |
| `make makemigrations m="message"` | Generate a new migration from model changes |
| `make test`           | Run the test suite (`pytest`)                       |
| `make lint`           | Run ruff + mypy checks                              |
| `make fmt`            | Auto-fix lint/format issues                          |
| `make precommit`      | Run all pre-commit hooks against the whole repo      |

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
