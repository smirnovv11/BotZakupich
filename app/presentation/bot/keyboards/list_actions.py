"""Inline keyboards for current list actions."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.constants import ButtonTextEnum, CallbackPrefixEnum


def current_list_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.CLEAR_LIST,
                    callback_data=CallbackPrefixEnum.CLEAR_LIST,
                ),
            ],
        ],
    )


def clear_list_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.CONFIRM_CLEAR_LIST,
                    callback_data=CallbackPrefixEnum.CONFIRM_CLEAR_LIST,
                ),
                InlineKeyboardButton(
                    text=ButtonTextEnum.CANCEL,
                    callback_data=CallbackPrefixEnum.CANCEL_CLEAR_LIST,
                ),
            ],
        ],
    )
