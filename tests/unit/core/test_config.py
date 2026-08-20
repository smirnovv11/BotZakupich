from pathlib import Path

import pytest
from app.core.config import Settings
from pydantic import ValidationError

TELEGRAM_TOKEN = "123456:test-token"
DATABASE_URL = (
    "postgresql+asyncpg://shopping_user:shopping_password@localhost:5432/shopping_bot"
)


def test_settings_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TELEGRAM_TOKEN)
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("PARSER_VERSION", "test-v1")

    settings = Settings(_env_file=None)

    assert settings.telegram_bot_token.get_secret_value() == TELEGRAM_TOKEN
    assert settings.database_url.get_secret_value() == DATABASE_URL
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.parser_version == "test-v1"


def test_settings_accept_northflank_bot_token_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("BOT_TOKEN", TELEGRAM_TOKEN)
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    settings = Settings(_env_file=None)

    assert settings.telegram_bot_token.get_secret_value() == TELEGRAM_TOKEN


def test_settings_load_from_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for variable_name in (
        "TELEGRAM_BOT_TOKEN",
        "DATABASE_URL",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "PARSER_VERSION",
    ):
        monkeypatch.delenv(variable_name, raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            (
                f"TELEGRAM_BOT_TOKEN={TELEGRAM_TOKEN}",
                f"DATABASE_URL={DATABASE_URL}",
                "ENVIRONMENT=local",
                "LOG_LEVEL=WARNING",
                "PARSER_VERSION=local-v2",
            )
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.environment == "local"
    assert settings.log_level == "WARNING"
    assert settings.parser_version == "local-v2"


def test_settings_repr_masks_secrets() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token=TELEGRAM_TOKEN,
        database_url=DATABASE_URL,
    )

    representation = repr(settings)

    assert TELEGRAM_TOKEN not in representation
    assert DATABASE_URL not in representation
    assert "**********" in representation


def test_settings_reject_unsupported_log_level() -> None:
    with pytest.raises(ValidationError, match="unsupported log level"):
        Settings(
            _env_file=None,
            telegram_bot_token=TELEGRAM_TOKEN,
            database_url=DATABASE_URL,
            log_level="verbose",
        )
