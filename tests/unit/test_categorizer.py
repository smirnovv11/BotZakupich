import inspect

import pytest
from app.application.services import categorizer
from app.application.services.categorizer import LocalCategorizer
from app.domain.enums import CategoryCodeEnum


def test_milk_is_categorized_as_dairy() -> None:
    result = LocalCategorizer().categorize("молоко")

    assert result.category_code == CategoryCodeEnum.DAIRY
    assert result.category_name_ru == "Молочные продукты"
    assert result.is_fallback is False


def test_bread_is_categorized_as_bakery() -> None:
    result = LocalCategorizer().categorize("хлеб")

    assert result.category_code == CategoryCodeEnum.BAKERY
    assert result.category_name_ru == "Хлеб и выпечка"
    assert result.is_fallback is False


@pytest.mark.parametrize(
    ("product_key", "category_code"),
    (
        ("кола", CategoryCodeEnum.DRINKS),
        ("чипсы", CategoryCodeEnum.SWEETS_SNACKS),
        ("сливки", CategoryCodeEnum.DAIRY),
        ("мясо", CategoryCodeEnum.MEAT_POULTRY),
        ("курица", CategoryCodeEnum.MEAT_POULTRY),
        ("свинина", CategoryCodeEnum.MEAT_POULTRY),
        ("бедра", CategoryCodeEnum.MEAT_POULTRY),
        ("голень", CategoryCodeEnum.MEAT_POULTRY),
    ),
)
def test_household_dictionary_categorizes_common_products(
    product_key: str,
    category_code: str,
) -> None:
    result = LocalCategorizer().categorize(product_key)

    assert result.category_code == category_code
    assert result.is_fallback is False


@pytest.mark.parametrize(
    ("product_key", "category_code"),
    (
        ("сливки 10%", CategoryCodeEnum.DAIRY),
        ("куриные бедра", CategoryCodeEnum.MEAT_POULTRY),
        ("чипсы lays", CategoryCodeEnum.SWEETS_SNACKS),
        ("кока-кола zero", CategoryCodeEnum.DRINKS),
    ),
)
def test_household_dictionary_categorizes_phrases_with_details(
    product_key: str,
    category_code: str,
) -> None:
    result = LocalCategorizer().categorize(product_key)

    assert result.category_code == category_code
    assert result.is_fallback is False


@pytest.mark.parametrize(
    ("product_key", "category_code"),
    (
        ("ряженка", CategoryCodeEnum.DAIRY),
        ("багет", CategoryCodeEnum.BAKERY),
        ("свекла", CategoryCodeEnum.VEGETABLES_GREENS),
        ("мандарины", CategoryCodeEnum.FRUITS_BERRIES),
        ("грудка", CategoryCodeEnum.MEAT_POULTRY),
        ("скумбрия", CategoryCodeEnum.FISH_SEAFOOD),
        ("сосиски", CategoryCodeEnum.SAUSAGES_DELI),
        ("гречка", CategoryCodeEnum.GRAINS_PASTA_FLOUR),
        ("тушенка", CategoryCodeEnum.CANNED),
        ("пельмени", CategoryCodeEnum.FROZEN),
        ("фисташки", CategoryCodeEnum.SWEETS_SNACKS),
        ("спрайт", CategoryCodeEnum.DRINKS),
        ("какао", CategoryCodeEnum.TEA_COFFEE),
        ("лавровый лист", CategoryCodeEnum.SAUCES_SPICES),
        ("капсулы для стирки", CategoryCodeEnum.HOUSEHOLD_CHEMICALS),
        ("гель для душа", CategoryCodeEnum.HYGIENE),
        ("фольга", CategoryCodeEnum.HOME_GOODS),
    ),
)
def test_extended_household_dictionary_categorizes_more_common_products(
    product_key: str,
    category_code: str,
) -> None:
    result = LocalCategorizer().categorize(product_key)

    assert result.category_code == category_code
    assert result.is_fallback is False


@pytest.mark.parametrize(
    ("product_key", "category_code"),
    (
        ("растительное масло", CategoryCodeEnum.SAUCES_SPICES),
        ("оливковое масло extra virgin", CategoryCodeEnum.SAUCES_SPICES),
        ("сливочное масло 82%", CategoryCodeEnum.DAIRY),
        ("влажные салфетки", CategoryCodeEnum.HYGIENE),
    ),
)
def test_longer_household_phrases_have_priority_over_short_keywords(
    product_key: str,
    category_code: str,
) -> None:
    result = LocalCategorizer().categorize(product_key)

    assert result.category_code == category_code
    assert result.is_fallback is False


def test_yo_is_normalized_before_categorization() -> None:
    result = LocalCategorizer().categorize("бёдра")

    assert result.category_code == CategoryCodeEnum.MEAT_POULTRY
    assert result.is_fallback is False


def test_unknown_product_falls_back_to_other() -> None:
    result = LocalCategorizer().categorize("манго сушеное")

    assert result.category_code == CategoryCodeEnum.OTHER
    assert result.category_name_ru == "Прочие"
    assert result.is_fallback is True


def test_input_is_normalized_before_categorization() -> None:
    result = LocalCategorizer().categorize("  МОЛОКА  ")

    assert result.category_code == CategoryCodeEnum.DAIRY
    assert result.category_name_ru == "Молочные продукты"
    assert result.is_fallback is False


def test_empty_product_key_falls_back_to_other() -> None:
    result = LocalCategorizer().categorize(" \n\t ")

    assert result.category_code == CategoryCodeEnum.OTHER
    assert result.category_name_ru == "Прочие"
    assert result.is_fallback is True


def test_categorizer_module_does_not_import_openai() -> None:
    source = inspect.getsource(categorizer)

    assert "openai" not in source.casefold()
