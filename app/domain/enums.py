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
