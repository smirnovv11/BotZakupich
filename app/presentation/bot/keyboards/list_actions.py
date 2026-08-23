"""Inline keyboards for current list actions."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import CurrentListDTO, ListItemDTO
from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.presentation.bot.callbacks import (
    build_confirm_delete_selected_items_callback,
    build_delete_page_fingerprint,
    build_edit_delete_page_callback,
    build_toggle_delete_item_callback,
)
from app.presentation.bot.category_display import category_emoji
from app.presentation.bot.pagination import get_checklist_page


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
    page_index: int = 0,
) -> InlineKeyboardMarkup:
    page = get_checklist_page(current_list.categories, page_index)
    if page is None:
        return InlineKeyboardMarkup(inline_keyboard=[])

    selected_ids = set(selected_item_ids)
    selected_item_mask = _delete_selection_mask(
        page_items=page.items,
        selected_item_ids=selected_ids,
    )
    page_fingerprint = build_delete_page_fingerprint(
        tuple(item.item_id for item in page.items),
    )
    item_rows = [
        [
            InlineKeyboardButton(
                text=_delete_item_button_text(
                    item,
                    category.category_code,
                    selected_ids,
                ),
                callback_data=build_toggle_delete_item_callback(
                    item.item_id,
                    page.page_index,
                    selected_item_mask,
                    page_fingerprint,
                ),
            ),
        ]
        for category in page.categories
        for item in category.items
    ]

    navigation_row = _delete_navigation_row(
        page_index=page.page_index,
        has_previous=page.has_previous,
        has_next=page.has_next,
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *item_rows,
            *([navigation_row] if navigation_row else []),
            [
                InlineKeyboardButton(
                    text=ButtonTextEnum.DELETE_SELECTED,
                    callback_data=build_confirm_delete_selected_items_callback(
                        page.page_index,
                        selected_item_mask,
                        page_fingerprint,
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
    category_code: str,
    selected_item_ids: set[int],
) -> str:
    marker = "☑️" if item.item_id in selected_item_ids else "☐"
    return f"{marker} {category_emoji(category_code)} {item.display_text}"


def _delete_navigation_row(
    *,
    page_index: int,
    has_previous: bool,
    has_next: bool,
) -> list[InlineKeyboardButton]:
    buttons = []
    if has_previous:
        buttons.append(
            InlineKeyboardButton(
                text=ButtonTextEnum.BACK,
                callback_data=build_edit_delete_page_callback(page_index - 1),
            ),
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=ButtonTextEnum.NEXT_PAGE,
                callback_data=build_edit_delete_page_callback(page_index + 1),
            ),
        )

    return buttons


def _delete_selection_mask(
    *,
    page_items: tuple[ListItemDTO, ...],
    selected_item_ids: set[int],
) -> int:
    selected_item_mask = 0
    for index, item in enumerate(page_items):
        if item.item_id in selected_item_ids:
            selected_item_mask |= 1 << index

    return selected_item_mask
