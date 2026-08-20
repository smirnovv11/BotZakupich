import logging

import pytest
from app.core.logging import configure_logging


def test_configure_logging_sets_root_level(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_config: dict[str, object] = {}
    monkeypatch.setattr(logging.config, "dictConfig", captured_config.update)

    configure_logging("DEBUG")

    assert captured_config["root"] == {
        "handlers": ["console"],
        "level": "DEBUG",
    }
