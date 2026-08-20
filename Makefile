ifeq ($(OS),Windows_NT)
SHELL := cmd.exe
.SHELLFLAGS := /C
endif

POETRY ?= poetry
DOCKER_COMPOSE ?= docker compose

.PHONY: install lint format format-check test pre-commit db-up db-down migrate downgrade seed revision run

install:
	$(POETRY) install

lint:
	$(POETRY) run ruff check .

format:
	$(POETRY) run ruff format .

format-check:
	$(POETRY) run ruff format --check .

test:
	$(POETRY) run pytest

pre-commit:
	$(POETRY) run pre-commit run --all-files

db-up:
	$(DOCKER_COMPOSE) up -d postgres

db-down:
	$(DOCKER_COMPOSE) down

migrate:
	$(POETRY) run alembic upgrade head

downgrade:
	$(POETRY) run alembic downgrade -1

seed:
	$(POETRY) run python -m app.infrastructure.db.seeds

revision:
	$(POETRY) run alembic revision --autogenerate -m "$(name)"

run:
	$(POETRY) run python -m app.main
