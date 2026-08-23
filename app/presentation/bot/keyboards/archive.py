"""Inline keyboards for archived shopping trips."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.application.dto import ArchivedListDTO, ListArchivesResult, ListItemDTO
from app.core.constants import ButtonTextEnum
from app.presentation.bot.callbacks import (
    build_archived_restore_page_callback,
    build_open_archived_list_callback,
    build_restore_archived_item_callback,
    build_restore_archived_list_callback,
)
from app.presentation.bot.category_display import category_emoji
from app.presentation.bot.pagination import get_checklist_page


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


def archived_list_keyboard(
    archived_list: ArchivedListDTO,
    page_index: int = 0,
) -> InlineKeyboardMarkup:
    page = get_checklist_page(archived_list.categories, page_index)
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

    if page is not None:
        inline_keyboard.extend(
            [
                InlineKeyboardButton(
                    text=_restore_item_button_text(item, category.category_code),
                    callback_data=build_restore_archived_item_callback(
                        archived_list.list_id,
                        item.item_id,
                    ),
                ),
            ]
            for category in page.categories
            for item in category.items
        )
        navigation_row = _archive_restore_navigation_row(
            list_id=archived_list.list_id,
            page_index=page.page_index,
            has_previous=page.has_previous,
            has_next=page.has_next,
        )
        if navigation_row:
            inline_keyboard.append(navigation_row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def _archive_summary_button_text(index: int, item_count: int) -> str:
    return f"📦 Поход {index} · товаров: {item_count}"


def _restore_item_button_text(item: ListItemDTO, category_code: str) -> str:
    return f"♻️ {category_emoji(category_code)} {item.display_text}"


def _archive_restore_navigation_row(
    *,
    list_id: int,
    page_index: int,
    has_previous: bool,
    has_next: bool,
) -> list[InlineKeyboardButton]:
    buttons = []
    if has_previous:
        buttons.append(
            InlineKeyboardButton(
                text=ButtonTextEnum.BACK,
                callback_data=build_archived_restore_page_callback(
                    list_id,
                    page_index - 1,
                ),
            ),
        )
    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=ButtonTextEnum.NEXT_PAGE,
                callback_data=build_archived_restore_page_callback(
                    list_id,
                    page_index + 1,
                ),
            ),
        )

    return buttons
