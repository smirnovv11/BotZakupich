from datetime import UTC, datetime
from decimal import Decimal

from app.application.dto import (
    AddedItemDTO,
    AddItemsResult,
    ArchivedListDTO,
    ArchivedListSummaryDTO,
    CurrentListDTO,
    FinishShoppingResult,
    ListArchivesResult,
    ListCategoryDTO,
    ListItemDTO,
    RestoreArchivedItemsResult,
    RestoredItemDTO,
    StartShoppingResult,
)
from app.application.errors import ApplicationError, ApplicationErrorCodeEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.formatters import (
    DUPLICATE_MESSAGE,
    EMPTY_ADD_MESSAGE,
    EMPTY_ARCHIVE_MESSAGE,
    EMPTY_ARCHIVED_LIST_MESSAGE,
    EMPTY_LIST_MESSAGE,
    SHOPPING_CHECKLIST_EMPTY_MESSAGE,
    format_added_items,
    format_archive_error,
    format_archive_list,
    format_archived_list,
    format_checklist,
    format_clear_result,
    format_current_list,
    format_finish_shopping_result,
    format_restore_result,
    format_shopping_error,
    format_shopping_started,
)


def make_added_item(
    item_id: int,
    display_text: str,
    *,
    category_code: str = CategoryCodeEnum.DAIRY,
    category_name_ru: str = "Молочные продукты",
    is_category_fallback: bool = False,
    position: int = 1,
) -> AddedItemDTO:
    return AddedItemDTO(
        item_id=item_id,
        display_text=display_text,
        product_key=display_text,
        category_code=category_code,
        category_name_ru=category_name_ru,
        is_category_fallback=is_category_fallback,
        position=position,
    )


def test_format_added_items_single_item() -> None:
    result = AddItemsResult(
        user_id=1,
        list_id=2,
        list_status="draft",
        input_message_id=3,
        added_items=(make_added_item(10, "молоко"),),
    )

    assert format_added_items(result) == "✅ Добавил:\n• молоко — 🥛 Молочные продукты"


def test_format_added_items_multiple_items() -> None:
    result = AddItemsResult(
        user_id=1,
        list_id=2,
        list_status="draft",
        input_message_id=3,
        added_items=(
            make_added_item(10, "молоко", position=1),
            make_added_item(
                11,
                "хлеб",
                category_code=CategoryCodeEnum.BAKERY,
                category_name_ru="Хлеб и выпечка",
                position=2,
            ),
        ),
    )

    assert format_added_items(result) == (
        "✅ Добавил:\n• молоко — 🥛 Молочные продукты\n• хлеб — 🥖 Хлеб и выпечка"
    )


def test_format_added_items_with_unknown_category_fallback() -> None:
    result = AddItemsResult(
        user_id=1,
        list_id=2,
        list_status="draft",
        input_message_id=3,
        added_items=(
            make_added_item(
                10,
                "манго сушеное",
                category_code=CategoryCodeEnum.OTHER,
                category_name_ru="Прочие",
                is_category_fallback=True,
            ),
        ),
    )

    assert format_added_items(result) == (
        "✅ Добавил:\n"
        "• манго сушеное — 🧩 Прочие\n"
        "\n"
        '🧩 Пока не удалось распознать категорию, положил в "Прочие": '
        "манго сушеное"
    )


def test_format_added_items_duplicate_message() -> None:
    result = AddItemsResult(
        user_id=1,
        list_id=2,
        list_status="draft",
        input_message_id=3,
        added_items=(),
        is_duplicate_message=True,
    )

    assert format_added_items(result) == DUPLICATE_MESSAGE


def test_format_added_items_empty_result() -> None:
    result = AddItemsResult(
        user_id=1,
        list_id=2,
        list_status="draft",
        input_message_id=3,
        added_items=(),
    )

    assert format_added_items(result) == EMPTY_ADD_MESSAGE


def test_format_empty_current_list() -> None:
    current_list = CurrentListDTO(
        list_id=None,
        list_status=None,
        title=None,
        categories=(),
    )

    assert format_current_list(current_list) == EMPTY_LIST_MESSAGE


def test_format_current_list_grouped_with_item_statuses() -> None:
    current_list = CurrentListDTO(
        list_id=1,
        list_status="shopping",
        title=None,
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=(
                    ListItemDTO(
                        item_id=1,
                        display_text="молоко",
                        status=ShoppingItemStatusEnum.PENDING,
                        position=1,
                        quantity_amount=Decimal("2"),
                        quantity_unit="л",
                    ),
                    ListItemDTO(
                        item_id=2,
                        display_text="сыр",
                        status=ShoppingItemStatusEnum.BOUGHT,
                        position=2,
                    ),
                ),
            ),
            ListCategoryDTO(
                category_code=CategoryCodeEnum.BAKERY,
                category_name_ru="Хлеб и выпечка",
                sort_order=20,
                items=(
                    ListItemDTO(
                        item_id=3,
                        display_text="хлеб",
                        status=ShoppingItemStatusEnum.PENDING,
                        position=3,
                    ),
                ),
            ),
        ),
    )

    assert format_current_list(current_list) == (
        "🧾 Текущий список:\n"
        "\n"
        "🥛 Молочные продукты:\n"
        "☐ молоко\n"
        "✅ сыр\n"
        "\n"
        "🥖 Хлеб и выпечка:\n"
        "☐ хлеб"
    )


def test_format_shopping_started() -> None:
    expected_text = "🛒 Начали покупки. В чеклисте товаров: 3."
    result = StartShoppingResult(
        list_id=1,
        list_status="shopping",
        shopping_started_at=None,
        item_count=3,
    )

    assert format_shopping_started(result) == expected_text


def test_format_checklist_empty() -> None:
    current_list = CurrentListDTO(
        list_id=None,
        list_status=None,
        title=None,
        categories=(),
    )

    assert format_checklist(current_list) == SHOPPING_CHECKLIST_EMPTY_MESSAGE


def test_format_checklist_grouped_with_item_statuses() -> None:
    current_list = CurrentListDTO(
        list_id=1,
        list_status="shopping",
        title=None,
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=(
                    ListItemDTO(
                        item_id=1,
                        display_text="молоко",
                        status=ShoppingItemStatusEnum.PENDING,
                        position=1,
                    ),
                    ListItemDTO(
                        item_id=2,
                        display_text="сыр",
                        status=ShoppingItemStatusEnum.BOUGHT,
                        position=2,
                    ),
                ),
            ),
        ),
    )

    assert format_checklist(current_list) == (
        "🛒 Чеклист покупок:\n\n🥛 Молочные продукты:\n☐ молоко\n✅ сыр"
    )


def test_format_shopping_error_uses_friendly_messages() -> None:
    assert format_shopping_error(
        ApplicationError(
            ApplicationErrorCodeEnum.EMPTY_DRAFT_LIST,
            "cannot start shopping with an empty list",
        ),
    ) == ("🧺 Список пуст. Сначала отправьте товары обычным сообщением.")
    assert format_shopping_error(
        ApplicationError(
            ApplicationErrorCodeEnum.LIST_NOT_DRAFT,
            "current shopping list is not in draft status",
        ),
    ) == ("🛒 Покупки уже начаты. Откройте чеклист и отмечайте товары.")


def test_format_finish_shopping_result() -> None:
    result = FinishShoppingResult(
        list_id=1,
        list_status="archived",
        archived_at=datetime(2026, 8, 20, 12, 30, tzinfo=UTC),
        archived_by_user_id=2,
    )

    assert (
        format_finish_shopping_result(result)
        == "🏁 Покупки завершены. Поход сохранен в архив: 20.08.2026 12:30."
    )


def test_format_empty_archive_list() -> None:
    assert format_archive_list(ListArchivesResult(archives=())) == EMPTY_ARCHIVE_MESSAGE


def test_format_archive_list_summaries() -> None:
    result = ListArchivesResult(
        archives=(
            ArchivedListSummaryDTO(
                list_id=1,
                list_status="archived",
                title=None,
                archived_at=datetime(2026, 8, 20, 14, 0, tzinfo=UTC),
                item_count=3,
            ),
            ArchivedListSummaryDTO(
                list_id=2,
                list_status="archived",
                title=None,
                archived_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
                item_count=1,
            ),
        ),
    )

    assert format_archive_list(result) == (
        "📦 Архив покупок:\n"
        "1. 20.08.2026 14:00 — товаров: 3\n"
        "2. 20.08.2026 13:00 — товаров: 1"
    )


def test_format_empty_archived_list() -> None:
    archived_list = ArchivedListDTO(
        list_id=1,
        list_status="archived",
        title=None,
        archived_at=datetime(2026, 8, 20, 14, 0, tzinfo=UTC),
        categories=(),
    )

    assert format_archived_list(archived_list) == EMPTY_ARCHIVED_LIST_MESSAGE


def test_format_archived_list_grouped_with_final_statuses() -> None:
    archived_list = ArchivedListDTO(
        list_id=1,
        list_status="archived",
        title=None,
        archived_at=datetime(2026, 8, 20, 14, 0, tzinfo=UTC),
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=(
                    ListItemDTO(
                        item_id=1,
                        display_text="молоко",
                        status=ShoppingItemStatusEnum.BOUGHT,
                        position=1,
                    ),
                ),
            ),
            ListCategoryDTO(
                category_code=CategoryCodeEnum.BAKERY,
                category_name_ru="Хлеб и выпечка",
                sort_order=20,
                items=(
                    ListItemDTO(
                        item_id=2,
                        display_text="хлеб",
                        status=ShoppingItemStatusEnum.PENDING,
                        position=2,
                    ),
                ),
            ),
        ),
    )

    assert format_archived_list(archived_list) == (
        "📦 Архивный поход от 20.08.2026 14:00:\n"
        "\n"
        "🥛 Молочные продукты:\n"
        "✅ молоко\n"
        "\n"
        "🥖 Хлеб и выпечка:\n"
        "☐ хлеб"
    )


def test_format_restore_result_for_empty_single_and_multiple_items() -> None:
    assert (
        format_restore_result(
            RestoreArchivedItemsResult(
                list_id=1,
                list_status="draft",
                restored_items=(),
            ),
        )
        == "♻️ В архиве не нашел товаров для добавления."
    )
    assert (
        format_restore_result(
            RestoreArchivedItemsResult(
                list_id=1,
                list_status="draft",
                restored_items=(
                    RestoredItemDTO(
                        item_id=10,
                        restored_from_item_id=5,
                        display_text="молоко",
                        position=1,
                    ),
                ),
            ),
        )
        == "♻️ Добавил из архива: молоко."
    )
    assert (
        format_restore_result(
            RestoreArchivedItemsResult(
                list_id=1,
                list_status="draft",
                restored_items=(
                    RestoredItemDTO(10, 5, "молоко", 1),
                    RestoredItemDTO(11, 6, "хлеб", 2),
                ),
            ),
        )
        == "♻️ Добавил из архива товаров: 2."
    )


def test_format_archive_error_uses_friendly_messages() -> None:
    no_active_list_error = ApplicationError(
        ApplicationErrorCodeEnum.ACTIVE_LIST_NOT_FOUND,
        "user does not have an active shopping list",
    )

    assert format_archive_error(no_active_list_error) == (
        "🧺 Сейчас нет активного чеклиста покупок."
    )
    assert format_archive_error(
        ApplicationError(
            ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
            "archived shopping list was not found",
        ),
    ) == ("📦 Не нашел этот архивный поход.")
    assert format_archive_error(
        ApplicationError(
            ApplicationErrorCodeEnum.SELECTED_ARCHIVED_ITEM_NOT_IN_LIST,
            "selected archived item does not belong to archived list",
        ),
    ) == ("📦 Этот товар не относится к выбранному архивному походу.")


def test_format_application_errors_fall_back_for_unknown_value_error() -> None:
    unknown_shopping_error = ValueError("cannot start shopping with an empty list")

    assert format_shopping_error(unknown_shopping_error) == (
        "Не получилось выполнить действие. Попробуйте открыть список еще раз."
    )
    assert format_archive_error(ValueError("archived shopping list was not found")) == (
        "Не получилось выполнить действие с архивом. Попробуйте открыть архив еще раз."
    )


def test_format_clear_result_with_deleted_items_count() -> None:
    assert format_clear_result(3) == "✨ Список очищен. Удалено товаров: 3."


def test_format_clear_result_with_empty_list() -> None:
    assert format_clear_result(0) == "✨ Список очищен. Товаров в нем не было."
