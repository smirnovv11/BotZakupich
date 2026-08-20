"""Local parsing primitives for user shopping-list messages."""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

ITEM_SEPARATOR_PATTERN = re.compile(r"(?<!\d),|,(?!\d)|[;\n]")
LEADING_QUANTITY_PATTERN = re.compile(
    r"^(?P<amount>\d+(?:[,.]\d+)?)\s+(?P<unit>\S+)\s+(?P<product>.+)$",
)
KNOWN_QUANTITY_UNITS = frozenset(
    {
        "л",
        "литр",
        "литра",
        "литров",
        "кг",
        "г",
        "гр",
        "штука",
        "штуки",
        "шт",
        "пачка",
        "пачки",
        "упаковка",
        "банка",
    },
)
WHITESPACE_PATTERN = re.compile(r"\s+")
PRODUCT_KEY_ALIASES = {
    "молока": "молоко",
}


@dataclass(frozen=True, slots=True)
class ParsedItemCandidate:
    display_text: str
    product_key: str
    quantity_amount: Decimal | None = None
    quantity_unit: str | None = None


def split_message_into_item_candidates(raw_text: str) -> list[ParsedItemCandidate]:
    stripped_text = raw_text.strip()

    if not stripped_text:
        return []

    if not ITEM_SEPARATOR_PATTERN.search(stripped_text):
        return [parse_item_candidate(stripped_text)]

    parts = [
        normalize_display_text(part) for part in ITEM_SEPARATOR_PATTERN.split(raw_text)
    ]
    valid_parts = [part for part in parts if part]

    if len(valid_parts) < 2 or len(valid_parts) != len(parts):
        return [parse_item_candidate(stripped_text)]

    return [parse_item_candidate(part) for part in valid_parts]


def parse_item_candidate(raw_text: str) -> ParsedItemCandidate:
    display_text = normalize_display_text(raw_text)
    product_key = normalize_product_key(display_text)

    amount, unit, product_text = parse_leading_quantity(display_text)
    if amount is None or unit is None or product_text is None:
        return ParsedItemCandidate(display_text=display_text, product_key=product_key)

    return ParsedItemCandidate(
        display_text=display_text,
        product_key=normalize_product_key(product_text),
        quantity_amount=amount,
        quantity_unit=unit,
    )


def normalize_display_text(raw_text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", raw_text.strip())


def normalize_product_key(raw_text: str) -> str:
    product_key = normalize_display_text(raw_text).casefold()

    return PRODUCT_KEY_ALIASES.get(product_key, product_key)


def parse_leading_quantity(
    raw_text: str,
) -> tuple[Decimal | None, str | None, str | None]:
    match = LEADING_QUANTITY_PATTERN.match(normalize_display_text(raw_text))
    if match is None:
        return None, None, None

    unit = match.group("unit").casefold()
    product_text = match.group("product")
    if unit not in KNOWN_QUANTITY_UNITS or not product_text:
        return None, None, None

    try:
        amount = Decimal(match.group("amount").replace(",", "."))
    except InvalidOperation:
        return None, None, None

    return amount, unit, product_text
