from aiogram.types import User
from app.core.constants import ButtonTextEnum
from app.presentation.bot.handlers.items import (
    MENU_BUTTON_TEXTS,
    is_add_item_text,
    is_command_text,
    is_menu_button_text,
    telegram_user_from_aiogram_user,
)


def test_telegram_user_dto_mapping_from_aiogram_user() -> None:
    telegram_user = User(
        id=12345,
        is_bot=False,
        first_name="Покупатель",
        last_name="Тестовый",
        username="buyer",
        language_code="ru",
    )

    result = telegram_user_from_aiogram_user(telegram_user)

    assert result.telegram_user_id == 12345
    assert result.telegram_username == "buyer"
    assert result.first_name == "Покупатель"
    assert result.last_name == "Тестовый"
    assert result.language_code == "ru"


def test_telegram_user_mapping_rejects_missing_user() -> None:
    try:
        telegram_user_from_aiogram_user(None)
    except ValueError as error:
        assert str(error) == "telegram user is missing"
    else:
        raise AssertionError("expected ValueError")


def test_menu_button_guard_excludes_all_button_texts_from_add_item_handling() -> None:
    expected_menu_texts = {
        ButtonTextEnum.SHOW_LIST,
        ButtonTextEnum.RESTORE_ALL,
        ButtonTextEnum.RESTORE_SELECTED,
        ButtonTextEnum.BACK,
    }

    assert set(MENU_BUTTON_TEXTS) == expected_menu_texts
    assert all(is_menu_button_text(text) for text in expected_menu_texts)
    assert all(not is_add_item_text(text) for text in expected_menu_texts)
    assert ButtonTextEnum.START_SHOPPING not in MENU_BUTTON_TEXTS
    assert ButtonTextEnum.FINISH_SHOPPING not in MENU_BUTTON_TEXTS
    assert ButtonTextEnum.ARCHIVE not in MENU_BUTTON_TEXTS


def test_command_guard_excludes_slash_commands_from_add_item_handling() -> None:
    assert is_command_text("/list") is True
    assert is_add_item_text("/list") is False


def test_regular_non_empty_text_is_add_item_text() -> None:
    assert is_add_item_text("молоко, хлеб") is True
    assert is_add_item_text("  ") is False
