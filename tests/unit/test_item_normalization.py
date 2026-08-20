from decimal import Decimal

from app.application.services.parser import LocalMessageParser
from app.domain.parsing import parse_item_candidate, split_message_into_item_candidates


def test_plain_item_gets_product_key_without_quantity() -> None:
    candidate = parse_item_candidate("молоко")

    assert candidate.display_text == "молоко"
    assert candidate.product_key == "молоко"
    assert candidate.quantity_amount is None
    assert candidate.quantity_unit is None


def test_integer_amount_and_unit_are_parsed_from_prefix() -> None:
    candidate = parse_item_candidate("2 литра молока")

    assert candidate.display_text == "2 литра молока"
    assert candidate.product_key == "молоко"
    assert candidate.quantity_amount == Decimal("2")
    assert candidate.quantity_unit == "литра"


def test_comma_decimal_amount_is_parsed_from_prefix() -> None:
    candidate = parse_item_candidate("0,5 л молока")

    assert candidate.display_text == "0,5 л молока"
    assert candidate.product_key == "молоко"
    assert candidate.quantity_amount == Decimal("0.5")
    assert candidate.quantity_unit == "л"


def test_dot_decimal_amount_is_parsed_from_prefix() -> None:
    candidate = parse_item_candidate("2.5 кг картошки")

    assert candidate.product_key == "картошки"
    assert candidate.quantity_amount == Decimal("2.5")
    assert candidate.quantity_unit == "кг"


def test_number_without_known_unit_is_not_parsed_as_quantity() -> None:
    candidate = parse_item_candidate("2 молока")

    assert candidate.display_text == "2 молока"
    assert candidate.product_key == "2 молока"
    assert candidate.quantity_amount is None
    assert candidate.quantity_unit is None


def test_unit_word_without_number_is_not_parsed_as_quantity() -> None:
    candidate = parse_item_candidate("пачка масла")

    assert candidate.display_text == "пачка масла"
    assert candidate.product_key == "пачка масла"
    assert candidate.quantity_amount is None
    assert candidate.quantity_unit is None


def test_display_text_is_trimmed_and_whitespace_normalized() -> None:
    candidate = parse_item_candidate("  2   литра   молока  ")

    assert candidate.display_text == "2 литра молока"
    assert candidate.product_key == "молоко"
    assert candidate.quantity_amount == Decimal("2")
    assert candidate.quantity_unit == "литра"


def test_product_key_is_lowercase_and_whitespace_normalized() -> None:
    candidate = parse_item_candidate("  Молоко   Безлактозное  ")

    assert candidate.display_text == "Молоко Безлактозное"
    assert candidate.product_key == "молоко безлактозное"


def test_split_list_normalizes_candidates_independently() -> None:
    candidates = split_message_into_item_candidates("2 литра молока, хлеб")

    assert candidates[0].display_text == "2 литра молока"
    assert candidates[0].product_key == "молоко"
    assert candidates[0].quantity_amount == Decimal("2")
    assert candidates[0].quantity_unit == "литра"
    assert candidates[1].display_text == "хлеб"
    assert candidates[1].product_key == "хлеб"
    assert candidates[1].quantity_amount is None
    assert candidates[1].quantity_unit is None


def test_application_parser_returns_normalized_candidates() -> None:
    candidates = LocalMessageParser().split("0,5 л молока\nХлеб")

    assert [candidate.product_key for candidate in candidates] == ["молоко", "хлеб"]
    assert candidates[0].quantity_amount == Decimal("0.5")
