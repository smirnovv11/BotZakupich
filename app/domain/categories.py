"""Category catalog for the shopping bot MVP."""

from dataclasses import dataclass

from app.domain.enums import CategoryCodeEnum


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
