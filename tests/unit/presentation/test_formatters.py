from decimal import Decimal

from app.application.dto import (
    AddedItemDTO,
    AddItemsResult,
    CurrentListDTO,
    ListCategoryDTO,
    ListItemDTO,
)
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.formatters import (
    DUPLICATE_MESSAGE,
    EMPTY_ADD_MESSAGE,
    EMPTY_LIST_MESSAGE,
    format_added_items,
    format_current_list,
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

    assert format_added_items(result) == "Добавил:\n- молоко — Молочные продукты"


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
        "Добавил:\n- молоко — Молочные продукты\n- хлеб — Хлеб и выпечка"
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
        "Добавил:\n"
        "- манго сушеное — Прочие\n"
        "\n"
        'Пока не удалось распознать категорию, положил в "Прочие": '
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
        "Текущий список:\n"
        "\n"
        "Молочные продукты:\n"
        "[ ] молоко\n"
        "[x] сыр\n"
        "\n"
        "Хлеб и выпечка:\n"
        "[ ] хлеб"
    )
