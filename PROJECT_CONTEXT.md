# Project Context

Дата обновления: 2026-08-21

Рабочее имя проекта: `Zakupich`.

## Что строим

Личный Telegram-бот для списка покупок.

Пользователь пишет товары обычным текстом:

- `молоко`
- `2 литра молока`
- `молоко, хлеб, яйца`

Бот сохраняет товары в текущий список, группирует по категориям, переводит список в checklist по кнопке `Начать покупки`, позволяет отмечать купленное, архивирует поход по кнопке `Завершить` и дает восстановить все или выбранные товары из архива.

## Текущий статус

MVP реализован до Telegram flows включительно. Tasks 01-20 из `.omx/plans/implementation-plan.md` выполнены.

Созданы и реализованы:

- `AGENTS.md` — правила для Codex и будущей разработки.
- `PLANS.md` — продуктово-технический план и стек.
- `DATABASE_SCHEMA.md` — зафиксированная MVP-схема БД.
- `.omx/plans/implementation-plan.md` — пошаговый backlog реализации.
- `.omx/specs/deep-interview-telegram-shopping-bot.md` — исходная спецификация после интервью.
- `pyproject.toml` и `poetry.lock` — Poetry-проект с MVP-зависимостями без OpenAI runtime dependency.
- `README.md` — базовые команды и текущая developer-документация.
- `.gitignore` — исключения для Python, локального окружения, IDE и OS-файлов.
- `.env.example` — безопасные placeholder-переменные окружения.
- `app/` — clean/onion структура пакетов: `core`, `domain`, `application`, `infrastructure`, `presentation`.
- `tests/` — unit и integration tests для реализованных слоев.
- `.pre-commit-config.yaml` — pre-commit hooks для hygiene-проверок и Ruff.
- `Makefile` — локальный command interface проекта.
- `docker-compose.yml` — локальная инфраструктура PostgreSQL с одной основной БД для dev и тестов.
- SQLAlchemy async models, Alembic setup и MVP initial migration.
- Idempotent seed начальных категорий с fallback-категорией `Прочие`.
- Repository ports, SQLAlchemy repositories и UnitOfWork.
- Локальный parser/splitter без AI: split по запятым, точкам с запятой и newline; неоднозначный ввод сохраняется как один item.
- Нормализация товара и мягкий parser количества/единиц с сохранением исходного `display_text`.
- Локальный categorizer без AI, fallback в `Прочие`.
- Use cases для добавления товаров, просмотра текущего списка, shopping lifecycle и archive/restore.
- aiogram bootstrap, `/start`, add/view handlers, shopping checklist handlers и archive/restore handlers.
- `app/application/errors.py` с `ApplicationError` и `ApplicationErrorCodeEnum` для expected use-case failures.

Выполненные шаги:

- Task 01: Scaffold Python project.
- Task 02: Add Makefile and local command interface.
- Task 03: Add Ruff and pre-commit.
- Task 04: Add Docker Compose for local database.
- Task 05: Add settings and logging.
- Task 06: Define domain enum-like classes and constants.
- Task 07: Add SQLAlchemy models and Alembic setup.
- Task 08: Seed categories.
- Task 09: Define repository ports, infrastructure repositories, and UnitOfWork.
- Task 10: Implement local message splitter.
- Task 11: Implement normalization and quantity parsing.
- Task 12: Implement local categorizer.
- Task 13: Implement add-items use case.
- Task 14: Implement list rendering service.
- Task 15: Implement shopping lifecycle use cases.
- Task 16: Implement archive use cases.
- Task 17: Add aiogram bot bootstrap and `/start`.
- Task 18: Implement bot handlers for add/view list.
- Task 19: Implement bot handlers for shopping checklist.
- Task 20: Implement bot handlers for finish/archive/restore.

Последние проверки после Task 20 и code-review fixes:

```bash
pytest --basetemp .pytest_tmp
ruff check .
ruff format --check .
```

Результат:

- `pytest --basetemp .pytest_tmp`: 139 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.

Если локальный `poetry` или `python` недоступны в PATH, используй bundled Python и пакеты из `.venv`; для pytest добавляй `--basetemp .pytest_tmp`.

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
- Telegram handlers должны оставаться тонкими: бизнес-логика живет в use cases.
- Не задавать пользователю уточняющих вопросов при неоднозначном вводе; лучше сохранить imperfect item.

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

Перед Task 21 выполнить mini-feature step: `TASK_20_5_MINI_FEATURES.md`.

Task 20.5 включает:

1. Добавить кнопку `Удалить` при просмотре текущего списка и flow выбора товаров для удаления.
2. Добавить pagination для inline checklist: shopping checklist, edit/delete checklist, restore selected checklist where applicable.
3. Расширить локальный categorizer/parser vocabulary для обычных товаров: `кола`, `чипсы`, `сливки`, `мясо`, `курица`, `свинина`, `бедра`, `голень`.

После Task 20.5 продолжить по `.omx/plans/implementation-plan.md` с Task 21: Add integration smoke tests for complete flows.

Task 21 должен добавить `tests/integration/test_full_mvp_flow.py` и покрыть use-case/repository сценарии без реального Telegram API:

1. User sends `молоко, хлеб, яйца`, starts shopping, toggles one item, finishes shopping, archive contains list.
2. User restores selected item from archive into new draft.
3. User starts shopping, sends `сыр` while shopping, item appears in active checklist.
4. Unknown item goes to `Прочие`, no AI call exists.

После Task 21 останется Task 22: обновить README как developer runbook.

Рекомендуемый prompt для следующего шага:

```text
Прочитай PROJECT_CONTEXT.md, AGENTS.md, DATABASE_SCHEMA.md и .omx/plans/implementation-plan.md.
Прочитай TASK_20_5_MINI_FEATURES.md.
Продолжи реализацию с Task 20.5: List edit mode, checklist pagination, and catalog expansion.
Следуй acceptance criteria, не добавляй OpenAI/AI runtime, shared lists, list_members или Redis.
После реализации запусти pytest и ruff.
```

## Low-priority watch items

- Malformed callbacks with known prefix currently may not reach invalid-action handlers because routing predicates require full parser success.
- Direct async handler tests are still missing for shopping/archive handlers.
- Inline keyboard labels use unbounded `display_text` and could be truncated presentation-only later.
- `ApplicationError` introduced, but broader typed-error cleanup can be continued if needed.

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
