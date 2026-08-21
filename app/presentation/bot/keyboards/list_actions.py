"""Inline keyboards for current list actions."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import CurrentListDTO, ListItemDTO
from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.presentation.bot.callbacks import (
    build_confirm_delete_selected_items_callback,
    build_toggle_delete_item_callback,
)


def current_list_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.EDIT_LIST,
                    callback_data=CallbackPrefixEnum.EDIT_LIST,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.CLEAR_LIST,
                    callback_data=CallbackPrefixEnum.CLEAR_LIST,
                ),
            ],
        ],
    )


def delete_items_keyboard(
    current_list: CurrentListDTO,
    selected_item_ids: tuple[int, ...],
) -> InlineKeyboardMarkup:
    selected_ids = set(selected_item_ids)
    item_rows = [
        [
            InlineKeyboardButton(
                text=_delete_item_button_text(item, selected_ids),
                callback_data=build_toggle_delete_item_callback(
                    item.item_id,
                    selected_item_ids,
                ),
            ),
        ]
        for category in current_list.categories
        for item in category.items
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *item_rows,
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.DELETE_SELECTED,
                    callback_data=build_confirm_delete_selected_items_callback(
                        selected_item_ids,
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.BACK,
                    callback_data=CallbackPrefixEnum.CANCEL_EDIT_LIST,
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


def _delete_item_button_text(
    item: ListItemDTO,
    selected_item_ids: set[int],
) -> str:
    marker = "☑️" if item.item_id in selected_item_ids else "☐"
    return f"{marker} {item.display_text}"
