from app.application.services.parser import LocalMessageParser
from app.domain.parsing import ParsedItemCandidate, split_message_into_item_candidates


def candidate_texts(candidates: list[ParsedItemCandidate]) -> list[str]:
    return [candidate.display_text for candidate in candidates]


def test_single_item_message_returns_one_candidate() -> None:
    candidates = split_message_into_item_candidates("молоко")

    assert candidate_texts(candidates) == ["молоко"]


def test_comma_separated_message_returns_multiple_candidates() -> None:
    candidates = split_message_into_item_candidates("молоко, хлеб, яйца")

    assert candidate_texts(candidates) == ["молоко", "хлеб", "яйца"]


def test_semicolon_separated_message_returns_multiple_candidates() -> None:
    candidates = split_message_into_item_candidates("молоко; хлеб; яйца")

    assert candidate_texts(candidates) == ["молоко", "хлеб", "яйца"]


def test_multiline_message_returns_multiple_candidates() -> None:
    candidates = split_message_into_item_candidates("молоко\nхлеб\nяйца")

    assert candidate_texts(candidates) == ["молоко", "хлеб", "яйца"]


def test_mixed_separators_return_multiple_candidates() -> None:
    candidates = split_message_into_item_candidates("молоко, хлеб\nяйца; сыр")

    assert candidate_texts(candidates) == ["молоко", "хлеб", "яйца", "сыр"]


def test_display_text_preserves_quantity_phrase() -> None:
    candidates = split_message_into_item_candidates("2 литра молока")

    assert candidate_texts(candidates) == ["2 литра молока"]


def test_whitespace_is_trimmed_around_display_text() -> None:
    candidates = split_message_into_item_candidates("  молоко  ,  хлеб  ")

    assert candidate_texts(candidates) == ["молоко", "хлеб"]


def test_empty_message_returns_no_candidates() -> None:
    candidates = split_message_into_item_candidates(" \n\t ")

    assert candidates == []


def test_ambiguous_message_without_explicit_separator_is_one_candidate() -> None:
    candidates = split_message_into_item_candidates("молоко и хлеб")

    assert candidate_texts(candidates) == ["молоко и хлеб"]


def test_empty_split_part_falls_back_to_whole_message() -> None:
    candidates = split_message_into_item_candidates("молоко,, хлеб")

    assert candidate_texts(candidates) == ["молоко,, хлеб"]


def test_separator_only_message_falls_back_to_one_candidate() -> None:
    candidates = split_message_into_item_candidates(",,")

    assert candidate_texts(candidates) == [",,"]


def test_application_parser_delegates_to_local_splitter() -> None:
    candidates = LocalMessageParser().split("молоко, хлеб")

    assert candidate_texts(candidates) == ["молоко", "хлеб"]
