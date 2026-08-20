from datetime import UTC, datetime

from app.application.dto import (
    ArchivedListDTO,
    ArchivedListSummaryDTO,
    ListArchivesResult,
    ListCategoryDTO,
    ListItemDTO,
)
from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.keyboards.archive import (
    archive_list_keyboard,
    archived_list_keyboard,
)


def test_archive_list_keyboard_has_open_button_per_archive() -> None:
    keyboard = archive_list_keyboard(
        ListArchivesResult(
            archives=(
                ArchivedListSummaryDTO(
                    list_id=11,
                    list_status="archived",
                    title=None,
                    archived_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
                    item_count=2,
                ),
                ArchivedListSummaryDTO(
                    list_id=12,
                    list_status="archived",
                    title=None,
                    archived_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
                    item_count=1,
                ),
            ),
        ),
    )

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["📦 Поход 1 · товаров: 2"],
        ["📦 Поход 2 · товаров: 1"],
    ]
    assert [
        [button.callback_data for button in row] for row in keyboard.inline_keyboard
    ] == [
        [f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:11"],
        [f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:12"],
    ]


def test_archived_list_keyboard_has_restore_all_and_restore_item_buttons() -> None:
    keyboard = archived_list_keyboard(
        ArchivedListDTO(
            list_id=11,
            list_status="archived",
            title=None,
            archived_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
            categories=(
                ListCategoryDTO(
                    category_code=CategoryCodeEnum.DAIRY,
                    category_name_ru="Молочные продукты",
                    sort_order=10,
                    items=(
                        ListItemDTO(
                            item_id=101,
                            display_text="молоко",
                            status=ShoppingItemStatusEnum.BOUGHT,
                            position=1,
                        ),
                        ListItemDTO(
                            item_id=102,
                            display_text="сыр",
                            status=ShoppingItemStatusEnum.PENDING,
                            position=2,
                        ),
                    ),
                ),
            ),
        ),
    )

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        [ButtonTextEnum.RESTORE_ALL],
        ["♻️ молоко"],
        ["♻️ сыр"],
    ]
    assert [
        [button.callback_data for button in row] for row in keyboard.inline_keyboard
    ] == [
        [f"{CallbackPrefixEnum.RESTORE_ARCHIVED_LIST}:11"],
        [f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:11:101"],
        [f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:11:102"],
    ]
