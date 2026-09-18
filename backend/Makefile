.PHONY: dev seed migrate makemigrations test lint fmt precommit

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	uv run python -m app.seed

migrate:
	uv run alembic upgrade head

makemigrations:
	uv run alembic revision --autogenerate -m "$(m)"

test:
	uv run pytest

lint:
	uv run ruff check . && uv run ruff format --check . && uv run mypy .

fmt:
	uv run ruff check --fix . && uv run ruff format .

precommit:
	uv run pre-commit run --all-files
