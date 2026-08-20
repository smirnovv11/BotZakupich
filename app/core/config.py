"""Application settings loaded from environment variables."""

import logging

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration with secrets hidden from representations."""

    telegram_bot_token: SecretStr
    database_url: SecretStr
    environment: str = "local"
    log_level: str = "INFO"
    parser_version: str = "local-v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator(
        "telegram_bot_token",
        "database_url",
        "environment",
        "parser_version",
    )
    @classmethod
    def validate_non_empty_value(cls, value: SecretStr | str) -> SecretStr | str:
        raw_value = value.get_secret_value() if isinstance(value, SecretStr) else value
        if not raw_value.strip():
            raise ValueError("value must not be empty")
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        normalized_value = value.strip().upper()
        if normalized_value not in logging.getLevelNamesMapping():
            raise ValueError(f"unsupported log level: {value}")
        return normalized_value
