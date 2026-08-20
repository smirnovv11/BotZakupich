"""Main reply keyboard for the Telegram bot."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.core.constants import ButtonTextEnum


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ButtonTextEnum.SHOW_LIST),
                KeyboardButton(text=ButtonTextEnum.START_SHOPPING),
            ],
            [
                KeyboardButton(text=ButtonTextEnum.FINISH_SHOPPING),
                KeyboardButton(text=ButtonTextEnum.ARCHIVE),
            ],
        ],
        resize_keyboard=True,
    )
