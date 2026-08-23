# Zakupich

Zakupich — персональный Telegram-бот для списка покупок. Пользователь отправляет
товары обычным текстом, бот локально разбирает сообщение, группирует позиции по
категориям и ведет список от черновика до завершенного похода.

MVP работает полностью без OpenAI и других AI-сервисов в runtime. Shared lists,
таблица `list_members`, Redis и совместное редактирование в текущую версию не
входят.

## Возможности MVP

- один текущий список на пользователя;
- добавление одной или нескольких позиций через запятые, точки с запятой или
  переносы строк;
- сохранение исходного текста позиции и мягкий разбор количества;
- локальная автоматическая категоризация с fallback в `Прочие`;
- режим покупок с inline checklist;
- pagination по категориям, максимум 10 товаров на странице;
- выборочное удаление товаров и полная очистка текущего списка;
- завершение и архивирование похода;
- восстановление всех или выбранных товаров из архива.

## Требования

- Python 3.12+;
- Poetry;
- Docker Desktop или Docker Engine с Docker Compose;
- GNU Make — опционально, все команды можно выполнить напрямую через Poetry;
- Telegram bot token от BotFather — только для запуска самого бота.

## Быстрый старт

### 1. Установить зависимости

```bash
poetry install
```

Проверить, что приложение импортируется:

```bash
poetry run python -c "import app"
```

### 2. Настроить окружение

Создать локальный `.env` из безопасного шаблона:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Минимальная локальная конфигурация:

```env
TELEGRAM_BOT_TOKEN=replace-with-real-bot-token
DATABASE_URL=postgresql+asyncpg://shopping_user:shopping_password@localhost:5432/shopping_bot
ENVIRONMENT=local
LOG_LEVEL=INFO
PARSER_VERSION=local-v1
RUN_MIGRATIONS=false
```

| Переменная | Обязательна | Назначение |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Да | Telegram token. Можно использовать alias `BOT_TOKEN`. |
| `DATABASE_URL` | Да | Async SQLAlchemy URL PostgreSQL с драйвером `asyncpg`. |
| `ENVIRONMENT` | Нет | Имя окружения, по умолчанию `local`. |
| `LOG_LEVEL` | Нет | Уровень логирования, по умолчанию `INFO`. |
| `PARSER_VERSION` | Нет | Версия локального parser, по умолчанию `local-v1`. |
| `RUN_MIGRATIONS` | Только Docker | Entry point запускает Alembic перед ботом при `true`. |

`.env` содержит секреты и не должен попадать в Git. `OPENAI_API_KEY` для MVP не
нужен и OpenAI SDK не входит в runtime dependencies.

### 3. Запустить PostgreSQL

```bash
make db-up
```

Без Make:

```bash
docker compose up -d postgres
```

Проверить готовность:

```bash
docker compose ps postgres
```

Сервис должен перейти в состояние `healthy` и слушать `localhost:5432`.

### 4. Применить миграции и seed категорий

```bash
make migrate
make seed
```

Без Make:

```bash
poetry run alembic upgrade head
poetry run python -m app.infrastructure.db.seeds
```

Seed идемпотентный: его можно запускать повторно. При обычном запуске бот также
обновляет каталог категорий перед началом polling, но таблицы должны уже
существовать после миграций.

### 5. Запустить бота

```bash
make run
```

Эквивалентные команды:

```bash
poetry run python -m app.main
poetry run zakupich-bot
```

После строки `Starting Telegram bot polling` откройте бота в Telegram и
отправьте `/start` или список вроде `молоко, хлеб, яйца`.

## Проверки

PostgreSQL должен быть запущен перед `pytest`, поскольку integration tests
работают со стандартной локальной БД `shopping_bot` на `localhost:5432`.

```bash
make test
make lint
make format-check
make pre-commit
```

Прямые команды:

```bash
poetry run pytest --basetemp .pytest_tmp
poetry run ruff check .
poetry run ruff format --check .
poetry run pre-commit run --all-files
```

В проекте намеренно нет отдельного `TEST_DATABASE_URL`. Integration fixtures
используют фиксированное локальное подключение из `tests/integration/conftest.py`
и очищают прикладные таблицы до и после каждого теста. Не храните в локальной БД
`shopping_bot` данные, которые нужно сохранить во время тестового запуска.

## Команды Makefile

| Команда | Действие |
| --- | --- |
| `make install` | Установить зависимости через Poetry. |
| `make db-up` | Запустить локальный PostgreSQL. |
| `make db-down` | Остановить Compose stack. Данные останутся в volume. |
| `make migrate` | Применить Alembic migrations до `head`. |
| `make downgrade` | Откатить одну миграцию. |
| `make seed` | Идемпотентно обновить каталог категорий. |
| `make revision name="description"` | Создать autogenerate migration. |
| `make run` | Запустить Telegram polling. |
| `make test` | Запустить весь pytest suite. |
| `make lint` | Запустить `ruff check`. |
| `make format` | Отформатировать Python-файлы. |
| `make format-check` | Проверить форматирование без изменений. |
| `make pre-commit` | Запустить все pre-commit hooks. |

## Структура проекта

```text
app/
  domain/          доменные правила, parsing и категории
  application/     DTO, ports, services и use cases
  infrastructure/  SQLAlchemy repositories, UnitOfWork и database setup
  presentation/    aiogram handlers, keyboards, callbacks и formatters
  core/            settings, constants и logging
migrations/        Alembic migrations
tests/
  unit/            быстрые изолированные тесты
  integration/     PostgreSQL repository/use-case flows
```

Handlers должны оставаться тонкими, а бизнес-логика — находиться в application и
domain слоях. Текущая схема не содержит `list_members`.

## Troubleshooting

### PostgreSQL connection refused

Убедитесь, что Docker daemon запущен, контейнер healthy, а порт `5432` не занят:

```bash
docker compose ps postgres
docker compose logs postgres
```

Если локальный PostgreSQL уже использует порт `5432`, остановите его или осознанно
измените mapping в `docker-compose.yml` и `DATABASE_URL`.

### Settings validation error

Проверьте наличие `.env`, непустые `TELEGRAM_BOT_TOKEN`/`BOT_TOKEN` и
`DATABASE_URL`. Alembic также загружает общие settings, поэтому для локальных
миграций `.env` должен содержать token; для миграции достаточно синтаксически
валидного placeholder, если сам бот не запускается.

### Таблицы или категории отсутствуют

```bash
make migrate
make seed
```

Не создавайте таблицы вручную: схема управляется Alembic.

### TelegramConflictError или polling уже запущен

Для одного token должен работать только один polling process. Остановите второй
локальный процесс или deployment instance и запустите бот снова.

### Make не найден или не видит Makefile в Windows

Можно использовать прямые Poetry-команды из разделов выше. Для старого GnuWin32
Make иногда помогает явное имя файла:

```bash
make -f Makefile test
```

### Poetry или Python недоступны в PATH в Codex workspace

Если `.venv` уже создана, можно использовать bundled Python и пакеты окружения:

```powershell
$env:PYTHONPATH="$PWD\.venv\Lib\site-packages"
$python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $python -m pytest --basetemp .pytest_tmp
& $python -m ruff check .
& $python -m ruff format --check .
```

Это аварийный локальный fallback, а не замена `poetry install` для нового
окружения.

## Docker и deployment

Собрать production image:

```bash
docker build -t zakupich:local .
```

Image запускает `zakupich-bot`. При `RUN_MIGRATIONS=true` entry point сначала
выполняет `alembic upgrade head`.

Для Northflank рекомендуется один service `zakupich-bot` с одной replica и image:

```text
ghcr.io/<github-owner>/zakupich:latest
ghcr.io/<github-owner>/zakupich:<commit-sha>
```

Переменные service:

```env
BOT_TOKEN=replace-with-telegram-token
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
ENVIRONMENT=production
LOG_LEVEL=INFO
PARSER_VERSION=local-v1
RUN_MIGRATIONS=true
```

Не запускайте несколько replicas с одним Telegram token при long polling.
