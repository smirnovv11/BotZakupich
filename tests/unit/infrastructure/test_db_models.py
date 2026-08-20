from app.domain.enums import ShoppingItemStatusEnum, ShoppingListStatusEnum
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import (
    SHOPPING_ITEM_STATUS_ENUM_NAME,
    SHOPPING_LIST_STATUS_ENUM_NAME,
)
from sqlalchemy import CheckConstraint, Index, Text
from sqlalchemy.dialects.postgresql import ENUM


def check_constraints(table_name: str) -> set[str]:
    return {
        constraint.name
        for constraint in Base.metadata.tables[table_name].constraints
        if isinstance(constraint, CheckConstraint)
    }


def indexes(table_name: str) -> dict[str, Index]:
    return {index.name: index for index in Base.metadata.tables[table_name].indexes}


def test_metadata_contains_only_mvp_tables() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "shopping_lists",
        "categories",
        "input_messages",
        "shopping_items",
    }
    assert "list_members" not in Base.metadata.tables


def test_status_columns_use_expected_postgresql_enum_names() -> None:
    list_status = Base.metadata.tables["shopping_lists"].c.status.type
    item_status = Base.metadata.tables["shopping_items"].c.status.type

    assert isinstance(list_status, ENUM)
    assert list_status.name == SHOPPING_LIST_STATUS_ENUM_NAME
    assert not list_status.create_type
    assert list_status.enums == [
        ShoppingListStatusEnum.DRAFT,
        ShoppingListStatusEnum.SHOPPING,
        ShoppingListStatusEnum.ARCHIVED,
    ]

    assert isinstance(item_status, ENUM)
    assert item_status.name == SHOPPING_ITEM_STATUS_ENUM_NAME
    assert not item_status.create_type
    assert item_status.enums == [
        ShoppingItemStatusEnum.PENDING,
        ShoppingItemStatusEnum.BOUGHT,
    ]


def test_quantity_unit_stays_plain_text() -> None:
    quantity_unit = Base.metadata.tables["shopping_items"].c.quantity_unit.type

    assert isinstance(quantity_unit, Text)
    assert not isinstance(quantity_unit, ENUM)


def test_partial_indexes_match_current_list_and_default_category_rules() -> None:
    shopping_list_indexes = indexes("shopping_lists")
    category_indexes = indexes("categories")

    current_list_index = shopping_list_indexes[
        "shopping_lists_one_current_per_owner_uidx"
    ]
    default_category_index = category_indexes["categories_one_default_uidx"]

    assert current_list_index.unique
    assert str(current_list_index.dialect_options["postgresql"]["where"]) == (
        "status in ('draft', 'shopping')"
    )

    assert default_category_index.unique
    assert str(default_category_index.dialect_options["postgresql"]["where"]) == (
        "is_default = true"
    )


def test_input_messages_parser_source_check_exists() -> None:
    assert "input_messages_parser_source_check" in check_constraints("input_messages")


def test_shopping_items_status_consistency_check_exists() -> None:
    assert "shopping_items_status_bought_fields_check" in check_constraints(
        "shopping_items",
    )
