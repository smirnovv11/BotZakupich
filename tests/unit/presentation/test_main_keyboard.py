from app.core.constants import ButtonTextEnum
from app.presentation.bot.keyboards.main import main_menu_keyboard


def test_main_menu_keyboard_uses_expected_button_texts() -> None:
    keyboard = main_menu_keyboard()

    assert [[button.text for button in row] for row in keyboard.keyboard] == [
        [ButtonTextEnum.SHOW_LIST, ButtonTextEnum.START_SHOPPING],
        [ButtonTextEnum.ARCHIVE],
    ]


def test_main_menu_keyboard_is_resize_friendly() -> None:
    keyboard = main_menu_keyboard()

    assert keyboard.resize_keyboard is True


def test_main_menu_keyboard_has_no_callback_data() -> None:
    keyboard = main_menu_keyboard()

    assert all(
        not hasattr(button, "callback_data")
        for row in keyboard.keyboard
        for button in row
    )
