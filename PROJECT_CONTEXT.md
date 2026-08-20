# Project Context

Дата обновления: 2026-08-08

Рабочее имя проекта: `Zakupich`.

## Что строим

Личный Telegram-бот для списка покупок.

Пользователь пишет товары обычным текстом:

- `молоко`
- `2 литра молока`
- `молоко, хлеб, яйца`

Бот сохраняет товары в текущий список, группирует по категориям, переводит список в checklist по кнопке `Начать покупки`, позволяет отмечать купленное, архивирует поход по кнопке `Завершить` и дает восстановить все или выбранные товары из архива.

## Текущий статус

Проект пока на стадии проектирования и подготовки реализации.

Созданы:

- `AGENTS.md` — правила для Codex и будущей разработки.
- `PLANS.md` — продуктово-технический план и стек.
- `DATABASE_SCHEMA.md` — зафиксированная MVP-схема БД.
- `.omx/plans/implementation-plan.md` — пошаговый backlog реализации.
- `.omx/specs/deep-interview-telegram-shopping-bot.md` — исходная спецификация после интервью.
- `pyproject.toml` и `poetry.lock` — Poetry-проект с MVP-зависимостями без OpenAI runtime dependency.
- `README.md` — базовые команды scaffold-этапа.
- `.gitignore` — исключения для Python, локального окружения, IDE и OS-файлов.
- `.env.example` — безопасные placeholder-переменные окружения.
- `app/` — базовая clean/onion структура пакетов: `core`, `domain`, `application`, `infrastructure`, `presentation`.
- `tests/` — базовый test package.
- `.pre-commit-config.yaml` — pre-commit hooks для hygiene-проверок и Ruff.
- `Makefile` — локальный command interface проекта.
- `docker-compose.yml` — локальная инфраструктура PostgreSQL с одной основной БД для dev и тестов.
- `tests/test_scaffold.py` — smoke-test на импорт scaffold-пакета.

Task 01: Scaffold Python project выполнен и проверен.
Task 03: Add Ruff and pre-commit выполнен и проверен.
Task 02: Add Makefile and local command interface выполнен и проверен.
Task 04: Add Docker Compose for local database выполнен и проверен.
Task 05: Add settings and logging выполнен и проверен; добавлены typed settings, безопасное
маскирование секретов, базовый console logging и unit-тесты.

Проверки Task 01:

```bash
poetry install
poetry run python -c "import app"
```

Проверки Task 03:

```bash
poetry run pre-commit run --all-files
poetry run ruff check .
poetry run ruff format --check .
```

Проверки Task 02:

```bash
make lint
make format-check
make test
```

Проверки Task 04:

```bash
make db-up
make db-down
```

Проверки прошли. На текущей машине команда `poetry` не была в PATH в части окружений, поэтому часть проверок выполнялась через системный Poetry: `python -m poetry ...`. Также установленный GnuWin32 `make` 3.81 не подхватывает `Makefile` автоматически из текущего кириллического пути; targets проверены через `make -f Makefile ...`.

Проект переименован в `Zakupich`; рекомендуется использовать путь без кириллицы:

```text
C:\Users\sqd12\Documents\ChatGPT\Zakupich
```

## Главные решения

- MVP работает без AI/OpenAI в runtime.
- Если локальная категоризация не распознала товар, товар сохраняется в категорию `Прочие`.
- OpenAI SDK, Responses API и Structured Outputs остаются future extension.
- Shared/family lists не входят в MVP.
- Таблицу `list_members` не создавать в MVP migrations; future-схема сохранена отдельно в `DATABASE_SCHEMA.md`.
- Redis не добавлять, пока явно не понадобится.
- Основная БД: PostgreSQL.
- Docker Compose используется только для локальной инфраструктуры: одна основная PostgreSQL DB для dev и тестов.
- Тесты не используют отдельную test DB и `TEST_DATABASE_URL`; интеграционные фикстуры должны очищать данные после каждого теста.
- Архитектура: clean/onion layers.
- Все constant string и enum-like значения собираются в классы с суффиксом `Enum`.
- Избегаем magic values.

## Реализуемая MVP-схема БД

Текущие таблицы:

- `users`
- `shopping_lists`
- `categories`
- `input_messages`
- `shopping_items`

PostgreSQL enum types:

- `shopping_list_status_enum`: `draft`, `shopping`, `archived`
- `shopping_item_status_enum`: `pending`, `bought`

Не реализуется в MVP:

- `list_members`
- `product_classification_cache`
- AI parser/classifier tables

## Стек

- Python 3.12+
- aiogram 3.x
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- pydantic-settings with `.env`
- Poetry
- Ruff
- pre-commit
- pytest + pytest-asyncio
- Docker Compose for local DB
- Makefile

## Архитектурные слои

```text
presentation/bot
  aiogram handlers, keyboards, callback parsing

application/services
  use cases, orchestration, repository ports

domain
  entities, value objects, enum-like classes, domain rules

infrastructure
  SQLAlchemy models, DB sessions, repository implementations, migrations

core/bootstrap
  settings, logging, app startup, dependency wiring
```

Domain не должен импортировать Telegram, SQLAlchemy sessions, OpenAI SDK или framework-specific объекты.

## Следующий шаг

Продолжить по `.omx/plans/implementation-plan.md` с Task 06: Define domain enum-like classes and constants.

Рекомендуемый prompt для следующего шага:

```text
Прочитай PROJECT_CONTEXT.md, AGENTS.md, DATABASE_SCHEMA.md и .omx/plans/implementation-plan.md.
Продолжи реализацию с Task 06: Define domain enum-like classes and constants.
Следуй acceptance criteria и не переходи к следующим task без проверки.
```

## Стоп-правила

Не добавлять без отдельного решения пользователя:

- AI/OpenAI runtime calls;
- Redis;
- shared/family lists;
- `list_members` migrations/table;
- voice messages;
- reminders;
- prices/budget;
- recipes.
