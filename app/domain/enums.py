"""Domain enum-like string constants for the shopping bot MVP."""


class ShoppingListStatusEnum:
    DRAFT = "draft"
    SHOPPING = "shopping"
    ARCHIVED = "archived"


class ShoppingItemStatusEnum:
    PENDING = "pending"
    BOUGHT = "bought"


class ParserSourceEnum:
    LOCAL = "local"
    FALLBACK = "fallback"


class CategoryCodeEnum:
    DAIRY = "dairy"
    BAKERY = "bakery"
    VEGETABLES_GREENS = "vegetables_greens"
    FRUITS_BERRIES = "fruits_berries"
    MEAT_POULTRY = "meat_poultry"
    FISH_SEAFOOD = "fish_seafood"
    SAUSAGES_DELI = "sausages_deli"
    EGGS = "eggs"
    GRAINS_PASTA_FLOUR = "grains_pasta_flour"
    CANNED = "canned"
    FROZEN = "frozen"
    SWEETS_SNACKS = "sweets_snacks"
    DRINKS = "drinks"
    TEA_COFFEE = "tea_coffee"
    SAUCES_SPICES = "sauces_spices"
    HOUSEHOLD_CHEMICALS = "household_chemicals"
    HYGIENE = "hygiene"
    HOME_GOODS = "home_goods"
    OTHER = "other"


CATEGORY_NAMES_RU = {
    CategoryCodeEnum.DAIRY: "Молочные продукты",
    CategoryCodeEnum.BAKERY: "Хлеб и выпечка",
    CategoryCodeEnum.VEGETABLES_GREENS: "Овощи и зелень",
    CategoryCodeEnum.FRUITS_BERRIES: "Фрукты и ягоды",
    CategoryCodeEnum.MEAT_POULTRY: "Мясо и птица",
    CategoryCodeEnum.FISH_SEAFOOD: "Рыба и морепродукты",
    CategoryCodeEnum.SAUSAGES_DELI: "Колбасы и деликатесы",
    CategoryCodeEnum.EGGS: "Яйца",
    CategoryCodeEnum.GRAINS_PASTA_FLOUR: "Крупы, макароны, мука",
    CategoryCodeEnum.CANNED: "Консервы",
    CategoryCodeEnum.FROZEN: "Заморозка",
    CategoryCodeEnum.SWEETS_SNACKS: "Сладости и снеки",
    CategoryCodeEnum.DRINKS: "Напитки",
    CategoryCodeEnum.TEA_COFFEE: "Чай, кофе",
    CategoryCodeEnum.SAUCES_SPICES: "Соусы и специи",
    CategoryCodeEnum.HOUSEHOLD_CHEMICALS: "Бытовая химия",
    CategoryCodeEnum.HYGIENE: "Гигиена",
    CategoryCodeEnum.HOME_GOODS: "Товары для дома",
    CategoryCodeEnum.OTHER: "Прочие",
}
