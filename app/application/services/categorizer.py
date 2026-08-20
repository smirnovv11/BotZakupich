"""Application-facing local categorizer service."""

from dataclasses import dataclass

from app.domain.categories import categorize_product_key, get_default_category


@dataclass(frozen=True, slots=True)
class CategorizationResult:
    category_code: str
    category_name_ru: str
    is_fallback: bool


class LocalCategorizer:
    def categorize(self, product_key: str) -> CategorizationResult:
        category = categorize_product_key(product_key)
        default_category = get_default_category()

        return CategorizationResult(
            category_code=category.code,
            category_name_ru=category.name_ru,
            is_fallback=category.code == default_category.code,
        )
