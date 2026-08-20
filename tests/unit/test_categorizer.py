import inspect

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
