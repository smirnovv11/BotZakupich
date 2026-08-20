import inspect
from types import ModuleType

from app.core import constants
from app.domain import enums
from app.domain.enums import CATEGORY_NAMES_RU


def enum_values(enum_class: type) -> list[str]:
    return [
        value
        for name, value in vars(enum_class).items()
        if name.isupper() and isinstance(value, str)
    ]


def public_classes(module: ModuleType) -> list[type]:
    return [
        member
        for _, member in inspect.getmembers(module, inspect.isclass)
        if member.__module__ == module.__name__ and not member.__name__.startswith("_")
    ]


def test_public_enum_like_classes_end_with_enum() -> None:
    classes = public_classes(enums) + public_classes(constants)

    assert classes
    assert all(enum_class.__name__.endswith("Enum") for enum_class in classes)


def test_enum_like_class_values_are_unique() -> None:
    for enum_class in public_classes(enums) + public_classes(constants):
        values = enum_values(enum_class)

        assert values
        assert len(values) == len(set(values))


def test_shopping_list_status_values_match_schema() -> None:
    assert enum_values(enums.ShoppingListStatusEnum) == [
        "draft",
        "shopping",
        "archived",
    ]


def test_shopping_item_status_values_match_schema() -> None:
    assert enum_values(enums.ShoppingItemStatusEnum) == [
        "pending",
        "bought",
    ]


def test_parser_source_values_match_schema_check_constraint() -> None:
    assert enum_values(enums.ParserSourceEnum) == [
        "local",
        "fallback",
    ]


def test_category_other_is_fallback_to_miscellaneous_label() -> None:
    assert enums.CategoryCodeEnum.OTHER == "other"
    assert CATEGORY_NAMES_RU[enums.CategoryCodeEnum.OTHER] == "Прочие"


def test_category_codes_cover_mvp_category_labels() -> None:
    assert set(enum_values(enums.CategoryCodeEnum)) == set(CATEGORY_NAMES_RU)
    assert len(CATEGORY_NAMES_RU) == 19
