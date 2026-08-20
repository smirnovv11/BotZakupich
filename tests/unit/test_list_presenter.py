from dataclasses import dataclass
from decimal import Decimal

import pytest
from app.application.services.list_presenter import (
    ListPresenter,
    empty_current_list,
)
from app.domain.enums import (
    CategoryCodeEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)


@dataclass(frozen=True, slots=True)
class FakeList:
    id: int
    status: str
    title: str | None = None


@dataclass(frozen=True, slots=True)
class FakeCategory:
    id: int
    code: str
    name_ru: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class FakeItem:
    id: int
    category_id: int
    display_text: str
    status: str
    position: int
    quantity_amount: Decimal | None = None
    quantity_unit: str | None = None


def test_presenter_groups_items_by_category_and_sorts_categories() -> None:
    result = ListPresenter().present(
        FakeList(id=1, status=ShoppingListStatusEnum.DRAFT, title="Покупки"),
        items=[
            FakeItem(1, 2, "хлеб", ShoppingItemStatusEnum.PENDING, 2),
            FakeItem(2, 1, "молоко", ShoppingItemStatusEnum.PENDING, 1),
        ],
        categories=[
            FakeCategory(2, CategoryCodeEnum.BAKERY, "Хлеб и выпечка", 20),
            FakeCategory(1, CategoryCodeEnum.DAIRY, "Молочные продукты", 10),
        ],
    )

    assert result.list_id == 1
    assert result.list_status == ShoppingListStatusEnum.DRAFT
    assert result.title == "Покупки"
    assert result.is_empty is False
    assert [category.category_code for category in result.categories] == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
    ]


def test_presenter_sorts_items_inside_category_by_position() -> None:
    result = ListPresenter().present(
        FakeList(id=1, status=ShoppingListStatusEnum.DRAFT),
        items=[
            FakeItem(1, 1, "яйца", ShoppingItemStatusEnum.PENDING, 3),
            FakeItem(2, 1, "молоко", ShoppingItemStatusEnum.BOUGHT, 1),
            FakeItem(3, 1, "сыр", ShoppingItemStatusEnum.PENDING, 2),
        ],
        categories=[
            FakeCategory(1, CategoryCodeEnum.DAIRY, "Молочные продукты", 10),
        ],
    )

    assert [item.display_text for item in result.categories[0].items] == [
        "молоко",
        "сыр",
        "яйца",
    ]
    assert [item.status for item in result.categories[0].items] == [
        ShoppingItemStatusEnum.BOUGHT,
        ShoppingItemStatusEnum.PENDING,
        ShoppingItemStatusEnum.PENDING,
    ]


def test_presenter_carries_quantity_fields() -> None:
    result = ListPresenter().present(
        FakeList(id=1, status=ShoppingListStatusEnum.DRAFT),
        items=[
            FakeItem(
                1,
                1,
                "2 литра молока",
                ShoppingItemStatusEnum.PENDING,
                1,
                Decimal("2"),
                "литра",
            ),
        ],
        categories=[
            FakeCategory(1, CategoryCodeEnum.DAIRY, "Молочные продукты", 10),
        ],
    )

    item = result.categories[0].items[0]

    assert item.quantity_amount == Decimal("2")
    assert item.quantity_unit == "литра"


def test_empty_current_list_has_explicit_empty_state() -> None:
    result = empty_current_list()

    assert result.list_id is None
    assert result.list_status is None
    assert result.title is None
    assert result.categories == ()
    assert result.is_empty is True


def test_presenter_empty_list_has_explicit_empty_state() -> None:
    result = ListPresenter().present(
        FakeList(id=1, status=ShoppingListStatusEnum.DRAFT),
        items=[],
        categories=[
            FakeCategory(1, CategoryCodeEnum.DAIRY, "Молочные продукты", 10),
        ],
    )

    assert result.list_id == 1
    assert result.categories == ()
    assert result.is_empty is True


def test_presenter_raises_for_missing_item_category() -> None:
    with pytest.raises(ValueError, match="category not found for item: 1"):
        ListPresenter().present(
            FakeList(id=1, status=ShoppingListStatusEnum.DRAFT),
            items=[
                FakeItem(1, 404, "молоко", ShoppingItemStatusEnum.PENDING, 1),
            ],
            categories=[],
        )
