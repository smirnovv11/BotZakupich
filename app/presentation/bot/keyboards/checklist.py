"""Inline checklist keyboard for active shopping lists."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import CurrentListDTO, ListItemDTO
from app.core.constants import ButtonTextEnum
from app.domain.enums import ShoppingItemStatusEnum
from app.presentation.bot.callbacks import (
    build_shopping_checklist_page_callback,
    build_toggle_item_callback,
)
from app.presentation.bot.pagination import get_checklist_page


def checklist_keyboard(
    current_list: CurrentListDTO,
    page_index: int = 0,
) -> InlineKeyboardMarkup:
    page = get_checklist_page(current_list.categories, page_index)
    if page is None:
        return InlineKeyboardMarkup(inline_keyboard=[])

    item_rows = [
        [
            InlineKeyboardButton(
                text=_checklist_button_text(item),
                callback_data=build_toggle_item_callback(
                    item.item_id,
                    page.page_index,
                ),
            ),
        ]
        for item in page.items
    ]

    navigation_row = _navigation_row(
        page_index=page.page_index,
        has_previous=page.has_previous,
        has_next=page.has_next,
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *item_rows,
            *([navigation_row] if navigation_row else []),
        ],
    )


def _checklist_button_text(item: ListItemDTO) -> str:
    marker = "✅" if item.status == ShoppingItemStatusEnum.BOUGHT else "☐"
    return f"{marker} {item.display_text}"


def _navigation_row(
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
                callback_data=build_shopping_checklist_page_callback(page_index - 1),
            ),
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=ButtonTextEnum.NEXT_PAGE,
                callback_data=build_shopping_checklist_page_callback(page_index + 1),
            ),
        )

    return buttons
