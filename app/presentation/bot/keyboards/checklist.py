"""Inline checklist keyboard for active shopping lists."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import CurrentListDTO, ListItemDTO
from app.domain.enums import ShoppingItemStatusEnum
from app.presentation.bot.callbacks import build_toggle_item_callback


def checklist_keyboard(current_list: CurrentListDTO) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_checklist_button_text(item),
                    callback_data=build_toggle_item_callback(item.item_id),
                ),
            ]
            for category in current_list.categories
            for item in category.items
        ],
    )


def _checklist_button_text(item: ListItemDTO) -> str:
    marker = "✅" if item.status == ShoppingItemStatusEnum.BOUGHT else "☐"
    return f"{marker} {item.display_text}"
