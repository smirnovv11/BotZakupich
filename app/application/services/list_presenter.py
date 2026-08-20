"""Application-level current list presentation helpers."""

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal
from typing import Protocol

from app.application.dto import CurrentListDTO, ListCategoryDTO, ListItemDTO


class ListRecord(Protocol):
    id: int
    status: str
    title: str | None


class CategoryRecord(Protocol):
    id: int
    code: str
    name_ru: str
    sort_order: int


class ItemRecord(Protocol):
    id: int
    category_id: int
    display_text: str
    status: str
    position: int
    quantity_amount: Decimal | None
    quantity_unit: str | None


def empty_current_list() -> CurrentListDTO:
    return CurrentListDTO(
        list_id=None,
        list_status=None,
        title=None,
        categories=(),
    )


class ListPresenter:
    def present(
        self,
        shopping_list: ListRecord,
        items: Iterable[ItemRecord],
        categories: Iterable[CategoryRecord],
    ) -> CurrentListDTO:
        categories_by_id = {category.id: category for category in categories}
        items_by_category_id: dict[int, list[ItemRecord]] = defaultdict(list)

        for item in items:
            if item.category_id not in categories_by_id:
                raise ValueError(f"category not found for item: {item.id}")
            items_by_category_id[item.category_id].append(item)

        list_categories = [
            self._present_category(
                category,
                items_by_category_id[category.id],
            )
            for category in categories_by_id.values()
            if items_by_category_id[category.id]
        ]
        list_categories.sort(key=lambda category: category.sort_order)

        return CurrentListDTO(
            list_id=shopping_list.id,
            list_status=shopping_list.status,
            title=shopping_list.title,
            categories=tuple(list_categories),
        )

    def _present_category(
        self,
        category: CategoryRecord,
        items: list[ItemRecord],
    ) -> ListCategoryDTO:
        sorted_items = sorted(items, key=lambda item: item.position)

        return ListCategoryDTO(
            category_code=category.code,
            category_name_ru=category.name_ru,
            sort_order=category.sort_order,
            items=tuple(
                ListItemDTO(
                    item_id=item.id,
                    display_text=item.display_text,
                    status=item.status,
                    position=item.position,
                    quantity_amount=item.quantity_amount,
                    quantity_unit=item.quantity_unit,
                )
                for item in sorted_items
            ),
        )
