# Zakupich

Personal Telegram bot for a low-friction shopping list.

The MVP keeps one current list per user, accepts plain text items, categorizes locally, and does not call OpenAI or any AI service at runtime.

## Current Stage

Tasks completed:

- Task 01: Python project scaffold
- Task 03: Ruff and pre-commit configuration
- Task 02: Makefile command interface
- Task 04: Docker Compose local database
- Task 05: Typed settings and logging

Domain constants, business logic, database models, migrations, and bot handlers are intentionally left for later tasks in `.omx/plans/implementation-plan.md`.

## Requirements

- Python 3.12+
- Poetry
- Docker with Docker Compose

## Setup

```bash
poetry install
```

## Verify Scaffold

```bash
poetry run python -c "import app"
```

## Local Commands

```bash
make install
make lint
make format
make format-check
make test
make db-up
make db-down
```

Planned migration and runtime commands are already reserved for later tasks:

```bash
make migrate
make revision name="describe_change"
make run
```

On older GnuWin32 `make` builds in Unicode paths, automatic Makefile discovery may fail. In that case, use a modern `make` or pass the file explicitly:

```bash
make -f Makefile lint
```

## Environment

Copy `.env.example` to `.env` for local development and fill in real values locally. Do not commit `.env`.

Local PostgreSQL uses this default URL:

```text
DATABASE_URL=postgresql+asyncpg://shopping_user:shopping_password@localhost:5432/shopping_bot
```

Tests use the same local Docker database and must clean up their data after each test via the repository/session test fixtures.

OpenAI configuration is not required for the MVP scaffold.
