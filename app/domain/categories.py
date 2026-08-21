"""Category catalog for the shopping bot MVP."""

from dataclasses import dataclass
from string import punctuation

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
    "сливки": CategoryCodeEnum.DAIRY,
    "сметана": CategoryCodeEnum.DAIRY,
    "кефир": CategoryCodeEnum.DAIRY,
    "ряженка": CategoryCodeEnum.DAIRY,
    "снежок": CategoryCodeEnum.DAIRY,
    "сыр": CategoryCodeEnum.DAIRY,
    "сырок": CategoryCodeEnum.DAIRY,
    "сырки": CategoryCodeEnum.DAIRY,
    "творог": CategoryCodeEnum.DAIRY,
    "йогурт": CategoryCodeEnum.DAIRY,
    "йогурты": CategoryCodeEnum.DAIRY,
    "масло": CategoryCodeEnum.DAIRY,
    "сливочное масло": CategoryCodeEnum.DAIRY,
    "моцарелла": CategoryCodeEnum.DAIRY,
    "пармезан": CategoryCodeEnum.DAIRY,
    "хлеб": CategoryCodeEnum.BAKERY,
    "батон": CategoryCodeEnum.BAKERY,
    "лаваш": CategoryCodeEnum.BAKERY,
    "булочки": CategoryCodeEnum.BAKERY,
    "булка": CategoryCodeEnum.BAKERY,
    "багет": CategoryCodeEnum.BAKERY,
    "пита": CategoryCodeEnum.BAKERY,
    "круассан": CategoryCodeEnum.BAKERY,
    "круассаны": CategoryCodeEnum.BAKERY,
    "лепешки": CategoryCodeEnum.BAKERY,
    "сухари": CategoryCodeEnum.BAKERY,
    "огурцы": CategoryCodeEnum.VEGETABLES_GREENS,
    "огурец": CategoryCodeEnum.VEGETABLES_GREENS,
    "помидоры": CategoryCodeEnum.VEGETABLES_GREENS,
    "помидор": CategoryCodeEnum.VEGETABLES_GREENS,
    "томат": CategoryCodeEnum.VEGETABLES_GREENS,
    "томаты": CategoryCodeEnum.VEGETABLES_GREENS,
    "картошка": CategoryCodeEnum.VEGETABLES_GREENS,
    "картошки": CategoryCodeEnum.VEGETABLES_GREENS,
    "картофель": CategoryCodeEnum.VEGETABLES_GREENS,
    "лук": CategoryCodeEnum.VEGETABLES_GREENS,
    "чеснок": CategoryCodeEnum.VEGETABLES_GREENS,
    "морковь": CategoryCodeEnum.VEGETABLES_GREENS,
    "капуста": CategoryCodeEnum.VEGETABLES_GREENS,
    "зелень": CategoryCodeEnum.VEGETABLES_GREENS,
    "укроп": CategoryCodeEnum.VEGETABLES_GREENS,
    "петрушка": CategoryCodeEnum.VEGETABLES_GREENS,
    "салат": CategoryCodeEnum.VEGETABLES_GREENS,
    "айсберг": CategoryCodeEnum.VEGETABLES_GREENS,
    "шпинат": CategoryCodeEnum.VEGETABLES_GREENS,
    "перец болгарский": CategoryCodeEnum.VEGETABLES_GREENS,
    "кабачок": CategoryCodeEnum.VEGETABLES_GREENS,
    "кабачки": CategoryCodeEnum.VEGETABLES_GREENS,
    "баклажан": CategoryCodeEnum.VEGETABLES_GREENS,
    "баклажаны": CategoryCodeEnum.VEGETABLES_GREENS,
    "свекла": CategoryCodeEnum.VEGETABLES_GREENS,
    "редис": CategoryCodeEnum.VEGETABLES_GREENS,
    "яблоки": CategoryCodeEnum.FRUITS_BERRIES,
    "яблоко": CategoryCodeEnum.FRUITS_BERRIES,
    "бананы": CategoryCodeEnum.FRUITS_BERRIES,
    "банан": CategoryCodeEnum.FRUITS_BERRIES,
    "апельсины": CategoryCodeEnum.FRUITS_BERRIES,
    "апельсин": CategoryCodeEnum.FRUITS_BERRIES,
    "лимоны": CategoryCodeEnum.FRUITS_BERRIES,
    "лимон": CategoryCodeEnum.FRUITS_BERRIES,
    "груши": CategoryCodeEnum.FRUITS_BERRIES,
    "груша": CategoryCodeEnum.FRUITS_BERRIES,
    "виноград": CategoryCodeEnum.FRUITS_BERRIES,
    "клубника": CategoryCodeEnum.FRUITS_BERRIES,
    "мандарины": CategoryCodeEnum.FRUITS_BERRIES,
    "мандарин": CategoryCodeEnum.FRUITS_BERRIES,
    "киви": CategoryCodeEnum.FRUITS_BERRIES,
    "ананас": CategoryCodeEnum.FRUITS_BERRIES,
    "персики": CategoryCodeEnum.FRUITS_BERRIES,
    "персик": CategoryCodeEnum.FRUITS_BERRIES,
    "арбуз": CategoryCodeEnum.FRUITS_BERRIES,
    "дыня": CategoryCodeEnum.FRUITS_BERRIES,
    "черника": CategoryCodeEnum.FRUITS_BERRIES,
    "малина": CategoryCodeEnum.FRUITS_BERRIES,
    "мясо": CategoryCodeEnum.MEAT_POULTRY,
    "курица": CategoryCodeEnum.MEAT_POULTRY,
    "цыпленок": CategoryCodeEnum.MEAT_POULTRY,
    "свинина": CategoryCodeEnum.MEAT_POULTRY,
    "говядина": CategoryCodeEnum.MEAT_POULTRY,
    "индейка": CategoryCodeEnum.MEAT_POULTRY,
    "фарш": CategoryCodeEnum.MEAT_POULTRY,
    "бедра": CategoryCodeEnum.MEAT_POULTRY,
    "бедро": CategoryCodeEnum.MEAT_POULTRY,
    "голень": CategoryCodeEnum.MEAT_POULTRY,
    "голени": CategoryCodeEnum.MEAT_POULTRY,
    "крылья": CategoryCodeEnum.MEAT_POULTRY,
    "филе": CategoryCodeEnum.MEAT_POULTRY,
    "грудка": CategoryCodeEnum.MEAT_POULTRY,
    "грудки": CategoryCodeEnum.MEAT_POULTRY,
    "окорочка": CategoryCodeEnum.MEAT_POULTRY,
    "шея": CategoryCodeEnum.MEAT_POULTRY,
    "ребра": CategoryCodeEnum.MEAT_POULTRY,
    "стейк": CategoryCodeEnum.MEAT_POULTRY,
    "котлеты": CategoryCodeEnum.MEAT_POULTRY,
    "печень": CategoryCodeEnum.MEAT_POULTRY,
    "рыба": CategoryCodeEnum.FISH_SEAFOOD,
    "лосось": CategoryCodeEnum.FISH_SEAFOOD,
    "форель": CategoryCodeEnum.FISH_SEAFOOD,
    "тунец": CategoryCodeEnum.FISH_SEAFOOD,
    "селедка": CategoryCodeEnum.FISH_SEAFOOD,
    "креветки": CategoryCodeEnum.FISH_SEAFOOD,
    "треска": CategoryCodeEnum.FISH_SEAFOOD,
    "скумбрия": CategoryCodeEnum.FISH_SEAFOOD,
    "хек": CategoryCodeEnum.FISH_SEAFOOD,
    "минтай": CategoryCodeEnum.FISH_SEAFOOD,
    "семга": CategoryCodeEnum.FISH_SEAFOOD,
    "краб": CategoryCodeEnum.FISH_SEAFOOD,
    "крабовые палочки": CategoryCodeEnum.FISH_SEAFOOD,
    "мидии": CategoryCodeEnum.FISH_SEAFOOD,
    "кальмар": CategoryCodeEnum.FISH_SEAFOOD,
    "икра": CategoryCodeEnum.FISH_SEAFOOD,
    "колбаса": CategoryCodeEnum.SAUSAGES_DELI,
    "сосиски": CategoryCodeEnum.SAUSAGES_DELI,
    "сардельки": CategoryCodeEnum.SAUSAGES_DELI,
    "ветчина": CategoryCodeEnum.SAUSAGES_DELI,
    "бекон": CategoryCodeEnum.SAUSAGES_DELI,
    "салями": CategoryCodeEnum.SAUSAGES_DELI,
    "паштет": CategoryCodeEnum.SAUSAGES_DELI,
    "карбонад": CategoryCodeEnum.SAUSAGES_DELI,
    "буженина": CategoryCodeEnum.SAUSAGES_DELI,
    "яйца": CategoryCodeEnum.EGGS,
    "яйцо": CategoryCodeEnum.EGGS,
    "рис": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "гречка": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "овсянка": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "геркулес": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "пшено": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "перловка": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "булгур": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "кус-кус": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "кускус": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "макароны": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "спагетти": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "лапша": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "паста": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "мука": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "манка": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "крупа": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "хлопья": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "мюсли": CategoryCodeEnum.GRAINS_PASTA_FLOUR,
    "фасоль": CategoryCodeEnum.CANNED,
    "горошек": CategoryCodeEnum.CANNED,
    "кукуруза": CategoryCodeEnum.CANNED,
    "оливки": CategoryCodeEnum.CANNED,
    "маслины": CategoryCodeEnum.CANNED,
    "тушенка": CategoryCodeEnum.CANNED,
    "консервы": CategoryCodeEnum.CANNED,
    "шпроты": CategoryCodeEnum.CANNED,
    "пельмени": CategoryCodeEnum.FROZEN,
    "вареники": CategoryCodeEnum.FROZEN,
    "хинкали": CategoryCodeEnum.FROZEN,
    "заморозка": CategoryCodeEnum.FROZEN,
    "мороженое": CategoryCodeEnum.FROZEN,
    "замороженные овощи": CategoryCodeEnum.FROZEN,
    "замороженные ягоды": CategoryCodeEnum.FROZEN,
    "сахар": CategoryCodeEnum.SWEETS_SNACKS,
    "шоколад": CategoryCodeEnum.SWEETS_SNACKS,
    "шоколадка": CategoryCodeEnum.SWEETS_SNACKS,
    "печенье": CategoryCodeEnum.SWEETS_SNACKS,
    "конфеты": CategoryCodeEnum.SWEETS_SNACKS,
    "вафли": CategoryCodeEnum.SWEETS_SNACKS,
    "пряники": CategoryCodeEnum.SWEETS_SNACKS,
    "зефир": CategoryCodeEnum.SWEETS_SNACKS,
    "мармелад": CategoryCodeEnum.SWEETS_SNACKS,
    "батончик": CategoryCodeEnum.SWEETS_SNACKS,
    "чипсы": CategoryCodeEnum.SWEETS_SNACKS,
    "сухарики": CategoryCodeEnum.SWEETS_SNACKS,
    "попкорн": CategoryCodeEnum.SWEETS_SNACKS,
    "орешки": CategoryCodeEnum.SWEETS_SNACKS,
    "арахис": CategoryCodeEnum.SWEETS_SNACKS,
    "фисташки": CategoryCodeEnum.SWEETS_SNACKS,
    "семечки": CategoryCodeEnum.SWEETS_SNACKS,
    "вода": CategoryCodeEnum.DRINKS,
    "минералка": CategoryCodeEnum.DRINKS,
    "сок": CategoryCodeEnum.DRINKS,
    "морс": CategoryCodeEnum.DRINKS,
    "компот": CategoryCodeEnum.DRINKS,
    "кола": CategoryCodeEnum.DRINKS,
    "кока-кола": CategoryCodeEnum.DRINKS,
    "кока кола": CategoryCodeEnum.DRINKS,
    "coca-cola": CategoryCodeEnum.DRINKS,
    "coca cola": CategoryCodeEnum.DRINKS,
    "пепси": CategoryCodeEnum.DRINKS,
    "pepsi": CategoryCodeEnum.DRINKS,
    "sprite": CategoryCodeEnum.DRINKS,
    "спрайт": CategoryCodeEnum.DRINKS,
    "fanta": CategoryCodeEnum.DRINKS,
    "фанта": CategoryCodeEnum.DRINKS,
    "газировка": CategoryCodeEnum.DRINKS,
    "лимонад": CategoryCodeEnum.DRINKS,
    "чай": CategoryCodeEnum.TEA_COFFEE,
    "зеленый чай": CategoryCodeEnum.TEA_COFFEE,
    "черный чай": CategoryCodeEnum.TEA_COFFEE,
    "кофе": CategoryCodeEnum.TEA_COFFEE,
    "капсулы кофе": CategoryCodeEnum.TEA_COFFEE,
    "какао": CategoryCodeEnum.TEA_COFFEE,
    "соль": CategoryCodeEnum.SAUCES_SPICES,
    "перец": CategoryCodeEnum.SAUCES_SPICES,
    "майонез": CategoryCodeEnum.SAUCES_SPICES,
    "кетчуп": CategoryCodeEnum.SAUCES_SPICES,
    "соус": CategoryCodeEnum.SAUCES_SPICES,
    "горчица": CategoryCodeEnum.SAUCES_SPICES,
    "уксус": CategoryCodeEnum.SAUCES_SPICES,
    "масло растительное": CategoryCodeEnum.SAUCES_SPICES,
    "растительное масло": CategoryCodeEnum.SAUCES_SPICES,
    "подсолнечное масло": CategoryCodeEnum.SAUCES_SPICES,
    "оливковое масло": CategoryCodeEnum.SAUCES_SPICES,
    "паприка": CategoryCodeEnum.SAUCES_SPICES,
    "корица": CategoryCodeEnum.SAUCES_SPICES,
    "лавровый лист": CategoryCodeEnum.SAUCES_SPICES,
    "приправы": CategoryCodeEnum.SAUCES_SPICES,
    "специи": CategoryCodeEnum.SAUCES_SPICES,
    "порошок": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "гель для стирки": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "капсулы для стирки": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "кондиционер для белья": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "средство для посуды": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "таблетки для посудомойки": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "чистящее средство": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "губки": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "пакеты для мусора": CategoryCodeEnum.HOUSEHOLD_CHEMICALS,
    "мыло": CategoryCodeEnum.HYGIENE,
    "шампунь": CategoryCodeEnum.HYGIENE,
    "гель для душа": CategoryCodeEnum.HYGIENE,
    "зубная паста": CategoryCodeEnum.HYGIENE,
    "зубная щетка": CategoryCodeEnum.HYGIENE,
    "дезодорант": CategoryCodeEnum.HYGIENE,
    "бритва": CategoryCodeEnum.HYGIENE,
    "прокладки": CategoryCodeEnum.HYGIENE,
    "тампоны": CategoryCodeEnum.HYGIENE,
    "влажные салфетки": CategoryCodeEnum.HYGIENE,
    "салфетки": CategoryCodeEnum.HOME_GOODS,
    "бумага": CategoryCodeEnum.HOME_GOODS,
    "туалетная бумага": CategoryCodeEnum.HOME_GOODS,
    "бумажные полотенца": CategoryCodeEnum.HOME_GOODS,
    "фольга": CategoryCodeEnum.HOME_GOODS,
    "пергамент": CategoryCodeEnum.HOME_GOODS,
    "пакеты": CategoryCodeEnum.HOME_GOODS,
    "мешки для мусора": CategoryCodeEnum.HOME_GOODS,
    "лампочки": CategoryCodeEnum.HOME_GOODS,
    "батарейки": CategoryCodeEnum.HOME_GOODS,
}

KEYWORD_CATEGORY_RULES = tuple(
    sorted(
        (
            (normalize_product_key(product_key), category_code)
            for product_key, category_code in PRODUCT_CATEGORY_RULES.items()
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    ),
)


def get_category_by_code(category_code: str) -> CategoryDefinition:
    return CATEGORY_BY_CODE[category_code]


def get_default_category() -> CategoryDefinition:
    return next(category for category in CATEGORY_DEFINITIONS if category.is_default)


def categorize_product_key(product_key: str) -> CategoryDefinition:
    normalized_product_key = normalize_product_key(product_key)
    category_code = PRODUCT_CATEGORY_RULES.get(normalized_product_key)
    if category_code is None:
        category_code = find_keyword_category_code(normalized_product_key)
    if category_code is None:
        category_code = get_default_category().code

    return get_category_by_code(category_code)


def find_keyword_category_code(product_key: str) -> str | None:
    searchable_product_key = normalize_for_keyword_match(product_key)
    if not searchable_product_key:
        return None

    for keyword, category_code in KEYWORD_CATEGORY_RULES:
        searchable_keyword = normalize_for_keyword_match(keyword)
        if contains_keyword(searchable_product_key, searchable_keyword):
            return category_code

    return None


def normalize_for_keyword_match(value: str) -> str:
    normalized_value = normalize_product_key(value)
    translation_table = str.maketrans(
        {character: " " for character in punctuation if character != "%"},
    )

    return " ".join(normalized_value.translate(translation_table).split())


def contains_keyword(product_key: str, keyword: str) -> bool:
    if not keyword:
        return False

    return f" {keyword} " in f" {product_key} "
