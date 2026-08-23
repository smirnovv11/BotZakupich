"""Presentation-only pagination helpers for Telegram checklist keyboards."""

from dataclasses import dataclass

from app.application.dto import ListCategoryDTO, ListItemDTO

CHECKLIST_PAGE_SIZE = 10
CHECKLIST_PAGE_TAIL_ALLOWANCE = 2


@dataclass(frozen=True, slots=True)
class ChecklistPage:
    categories: tuple[ListCategoryDTO, ...]
    page_index: int
    total_pages: int

    @property
    def items(self) -> tuple[ListItemDTO, ...]:
        return tuple(item for category in self.categories for item in category.items)

    @property
    def has_previous(self) -> bool:
        return self.page_index > 0

    @property
    def has_next(self) -> bool:
        return self.page_index < self.total_pages - 1


def build_checklist_pages(
    categories: tuple[ListCategoryDTO, ...],
    *,
    page_size: int = CHECKLIST_PAGE_SIZE,
    tail_allowance: int = CHECKLIST_PAGE_TAIL_ALLOWANCE,
) -> tuple[ChecklistPage, ...]:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    if tail_allowance < 0:
        raise ValueError("tail_allowance must not be negative")

    flattened_items: list[tuple[ListCategoryDTO, ListItemDTO]] = []
    for category in sorted(categories, key=lambda item: item.sort_order):
        flattened_items.extend(
            (category, item)
            for item in sorted(category.items, key=lambda item: item.position)
        )

    chunks = [
        flattened_items[start_index : start_index + page_size]
        for start_index in range(0, len(flattened_items), page_size)
    ]
    if len(chunks) > 1 and len(chunks[-1]) <= tail_allowance:
        chunks[-2].extend(chunks.pop())

    total_pages = len(chunks)
    return tuple(
        ChecklistPage(
            categories=_group_page_items(chunk),
            page_index=page_index,
            total_pages=total_pages,
        )
        for page_index, chunk in enumerate(chunks)
    )


def get_checklist_page(
    categories: tuple[ListCategoryDTO, ...],
    page_index: int,
    *,
    page_size: int = CHECKLIST_PAGE_SIZE,
    tail_allowance: int = CHECKLIST_PAGE_TAIL_ALLOWANCE,
) -> ChecklistPage | None:
    pages = build_checklist_pages(
        categories,
        page_size=page_size,
        tail_allowance=tail_allowance,
    )
    if not pages:
        return None

    clamped_index = clamp_page_index(page_index, len(pages))
    return pages[clamped_index]


def clamp_page_index(page_index: int, total_pages: int) -> int:
    if total_pages <= 0:
        return 0

    return min(max(page_index, 0), total_pages - 1)


def _group_page_items(
    page_items: list[tuple[ListCategoryDTO, ListItemDTO]],
) -> tuple[ListCategoryDTO, ...]:
    grouped_categories: list[ListCategoryDTO] = []
    for category, item in page_items:
        if (
            grouped_categories
            and grouped_categories[-1].category_code == category.category_code
        ):
            previous_category = grouped_categories[-1]
            grouped_categories[-1] = ListCategoryDTO(
                category_code=previous_category.category_code,
                category_name_ru=previous_category.category_name_ru,
                sort_order=previous_category.sort_order,
                items=(*previous_category.items, item),
            )
            continue

        grouped_categories.append(
            ListCategoryDTO(
                category_code=category.category_code,
                category_name_ru=category.category_name_ru,
                sort_order=category.sort_order,
                items=(item,),
            ),
        )

    return tuple(grouped_categories)
