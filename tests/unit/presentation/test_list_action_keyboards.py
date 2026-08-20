from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.presentation.bot.keyboards.list_actions import (
    clear_list_confirmation_keyboard,
    current_list_actions_keyboard,
)


def test_current_list_actions_keyboard_has_clear_button() -> None:
    keyboard = current_list_actions_keyboard()
    button = keyboard.inline_keyboard[0][0]

    assert button.text == ButtonTextEnum.CLEAR_LIST
    assert button.callback_data == CallbackPrefixEnum.CLEAR_LIST


def test_clear_list_confirmation_keyboard_has_confirm_and_cancel_buttons() -> None:
    keyboard = clear_list_confirmation_keyboard()
    confirm_button, cancel_button = keyboard.inline_keyboard[0]

    assert confirm_button.text == ButtonTextEnum.CONFIRM_CLEAR_LIST
    assert confirm_button.callback_data == CallbackPrefixEnum.CONFIRM_CLEAR_LIST
    assert cancel_button.text == ButtonTextEnum.CANCEL
    assert cancel_button.callback_data == CallbackPrefixEnum.CANCEL_CLEAR_LIST
