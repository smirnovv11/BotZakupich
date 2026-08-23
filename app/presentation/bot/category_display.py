"""Shared category display helpers for Telegram messages and keyboards."""

from app.domain.enums import CategoryCodeEnum

CATEGORY_EMOJI_BY_CODE = {
    CategoryCodeEnum.DAIRY: "🥛",
    CategoryCodeEnum.BAKERY: "🥖",
    CategoryCodeEnum.VEGETABLES_GREENS: "🥬",
    CategoryCodeEnum.FRUITS_BERRIES: "🍎",
    CategoryCodeEnum.MEAT_POULTRY: "🥩",
    CategoryCodeEnum.FISH_SEAFOOD: "🐟",
    CategoryCodeEnum.SAUSAGES_DELI: "🥓",
    CategoryCodeEnum.EGGS: "🥚",
    CategoryCodeEnum.GRAINS_PASTA_FLOUR: "🍝",
    CategoryCodeEnum.CANNED: "🥫",
    CategoryCodeEnum.FROZEN: "❄️",
    CategoryCodeEnum.SWEETS_SNACKS: "🍫",
    CategoryCodeEnum.DRINKS: "🥤",
    CategoryCodeEnum.TEA_COFFEE: "☕",
    CategoryCodeEnum.SAUCES_SPICES: "🧂",
    CategoryCodeEnum.HOUSEHOLD_CHEMICALS: "🧽",
    CategoryCodeEnum.HYGIENE: "🧼",
    CategoryCodeEnum.HOME_GOODS: "🏠",
    CategoryCodeEnum.OTHER: "🧩",
}


def category_emoji(category_code: str) -> str:
    return CATEGORY_EMOJI_BY_CODE.get(
        category_code,
        CATEGORY_EMOJI_BY_CODE[CategoryCodeEnum.OTHER],
    )


def category_title(category_code: str, category_name_ru: str) -> str:
    return f"{category_emoji(category_code)} {category_name_ru}"
