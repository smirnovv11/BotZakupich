"""Category catalog for the shopping bot MVP."""

from dataclasses import dataclass

from app.domain.enums import CategoryCodeEnum
from app.domain.parsing import normalize_product_key


@dataclass(frozen=True)
class CategoryDefinition:
    code: str
    name_ru: str
    sort_order: int
    is_default: bool = False


CATEGORY_DEFINITIONS = (
    CategoryDefinition(CategoryCodeEnum.DAIRY, "Молочные продукты", 10),
    CategoryDefinition(CategoryCodeEnum.BAKERY, "Хлеб и выпечка", 20),
    CategoryDefinition(CategoryCodeEnum.VEGETABLES_GREENS, "Овощи и зелень", 30),
    CategoryDefinition(CategoryCodeEnum.FRUITS_BERRIES, "Фрукты и ягоды", 40),
    CategoryDefinition(CategoryCodeEnum.MEAT_POULTRY, "Мясо и птица", 50),
    CategoryDefinition(CategoryCodeEnum.FISH_SEAFOOD, "Рыба и морепродукты", 60),
    CategoryDefinition(CategoryCodeEnum.SAUSAGES_DELI, "Колбасы и деликатесы", 70),
    CategoryDefinition(CategoryCodeEnum.EGGS, "Яйца", 80),
    CategoryDefinition(
        CategoryCodeEnum.GRAINS_PASTA_FLOUR,
        "Крупы, макароны, мука",
        90,
    ),
    CategoryDefinition(CategoryCodeEnum.CANNED, "Консервы", 100),
    CategoryDefinition(CategoryCodeEnum.FROZEN, "Заморозка", 110),
    CategoryDefinition(CategoryCodeEnum.SWEETS_SNACKS, "Сладости и снеки", 120),
    CategoryDefinition(CategoryCodeEnum.DRINKS, "Напитки", 130),
    CategoryDefinition(CategoryCodeEnum.TEA_COFFEE, "Чай, кофе", 140),
    CategoryDefinition(CategoryCodeEnum.SAUCES_SPICES, "Соусы и специи", 150),
    CategoryDefinition(CategoryCodeEnum.HOUSEHOLD_CHEMICALS, "Бытовая химия", 160),
    CategoryDefinition(CategoryCodeEnum.HYGIENE, "Гигиена", 170),
    CategoryDefinition(CategoryCodeEnum.HOME_GOODS, "Товары для дома", 180),
    CategoryDefinition(CategoryCodeEnum.OTHER, "Прочие", 1000, is_default=True),
)

CATEGORY_BY_CODE = {category.code: category for category in CATEGORY_DEFINITIONS}

PRODUCT_CATEGORY_RULES = {
    "молоко": CategoryCodeEnum.DAIRY,
    "молока": CategoryCodeEnum.DAIRY,
    "кефир": CategoryCodeEnum.DAIRY,
    "сыр": CategoryCodeEnum.DAIRY,
    "творог": CategoryCodeEnum.DAIRY,
    "йогурт": CategoryCodeEnum.DAIRY,
    "хлеб": CategoryCodeEnum.BAKERY,
    "батон": CategoryCodeEnum.BAKERY,
    "булочки": CategoryCodeEnum.BAKERY,
    "огурцы": CategoryCodeEnum.VEGETABLES_GREENS,
    "помидоры": CategoryCodeEnum.VEGETABLES_GREENS,
    "картошка": CategoryCodeEnum.VEGETABLES_GREENS,
    "картошки": CategoryCodeEnum.VEGETABLES_GREENS,
    "яблоки": CategoryCodeEnum.FRUITS_BERRIES,
    "бананы": CategoryCodeEnum.FRUITS_BERRIES,
    "курица": CategoryCodeEnum.MEAT_POULTRY,
    "фарш": CategoryCodeEnum.MEAT_POULTRY,
    "рыба": CategoryCodeEnum.FISH_SEAFOOD,
    "лосось": CategoryCodeEnum.FISH_SEAFOOD,
    "колбаса": CategoryCodeEnum.SAUSAGES_DELI,
    "яйца": CategoryCodeEnum.EGGS,
    "рис": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "макароны": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "мука": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "сахар": CategoryCodeEnum.SWEETS_SNACKS,
    "шоколад": CategoryCodeEnum.SWEETS_SNACKS,
    "вода": CategoryCodeEnum.DRINKS,
    "сок": CategoryCodeEnum.DRINKS,
    "чай": CategoryCodeEnum.TEA_COFFEE,
    "кофе": CategoryCodeEnum.TEA_COFFEE,
    "соль": CategoryCodeEnum.SAUCES_SPICES,
    "перец": CategoryCodeEnum.SAUCES_SPICES,
    "порошок": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "мыло": CategoryCodeEnum.HYGIENE,
    "салфетки": CategoryCodeEnum.HOME_GOODS,
}


def get_category_by_code(category_code: str) -> CategoryDefinition:
    return CATEGORY_BY_CODE[category_code]


def get_default_category() -> CategoryDefinition:
    return next(category for category in CATEGORY_DEFINITIONS if category.is_default)


def categorize_product_key(product_key: str) -> CategoryDefinition:
    normalized_product_key = normalize_product_key(product_key)
    category_code = PRODUCT_CATEGORY_RULES.get(
        normalized_product_key,
        get_default_category().code,
    )

    return get_category_by_code(category_code)
