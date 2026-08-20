"""Inline keyboards for archived shopping trips."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import ArchivedListDTO, ListArchivesResult, ListItemDTO
from app.core.constants import ButtonTextEnum
from app.presentation.bot.callbacks import (
    build_open_archived_list_callback,
    build_restore_archived_item_callback,
    build_restore_archived_list_callback,
)


def archive_list_keyboard(archives: ListArchivesResult) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_archive_summary_button_text(index, archive.item_count),
                    callback_data=build_open_archived_list_callback(archive.list_id),
                ),
            ]
            for index, archive in enumerate(archives.archives, start=1)
        ],
    )


def archived_list_keyboard(archived_list: ArchivedListDTO) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=ButtonTextEnum.RESTORE_ALL,
                callback_data=build_restore_archived_list_callback(
                    archived_list.list_id,
                ),
            ),
        ],
    ]

    inline_keyboard.extend(
        [
            InlineKeyboardButton(
                text=_restore_item_button_text(item),
                callback_data=build_restore_archived_item_callback(
                    archived_list.list_id,
                    item.item_id,
                ),
            ),
        ]
        for category in archived_list.categories
        for item in category.items
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def _archive_summary_button_text(index: int, item_count: int) -> str:
    return f"📦 Поход {index} · товаров: {item_count}"


def _restore_item_button_text(item: ListItemDTO) -> str:
    return f"♻️ {item.display_text}"
