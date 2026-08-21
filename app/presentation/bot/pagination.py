"""Presentation-only pagination helpers for Telegram checklist keyboards."""

from dataclasses import dataclass
from math import ceil

from app.application.dto import ListCategoryDTO, ListItemDTO

CHECKLIST_PAGE_SIZE = 10


@dataclass(frozen=True, slots=True)
class ChecklistPage:
    category_code: str
    category_name_ru: str
    sort_order: int
    items: tuple[ListItemDTO, ...]
    page_index: int
    total_pages: int

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
) -> tuple[ChecklistPage, ...]:
    pages: list[tuple[ListCategoryDTO, tuple[ListItemDTO, ...]]] = []
    for category in sorted(categories, key=lambda item: item.sort_order):
        if not category.items:
            continue

        page_count = ceil(len(category.items) / page_size)
        for page_number in range(page_count):
            start_index = page_number * page_size
            end_index = start_index + page_size
            pages.append((category, category.items[start_index:end_index]))

    total_pages = len(pages)
    return tuple(
        ChecklistPage(
            category_code=category.category_code,
            category_name_ru=category.category_name_ru,
            sort_order=category.sort_order,
            items=items,
            page_index=page_index,
            total_pages=total_pages,
        )
        for page_index, (category, items) in enumerate(pages)
    )


def get_checklist_page(
    categories: tuple[ListCategoryDTO, ...],
    page_index: int,
    *,
    page_size: int = CHECKLIST_PAGE_SIZE,
) -> ChecklistPage | None:
    pages = build_checklist_pages(categories, page_size=page_size)
    if not pages:
        return None

    clamped_index = clamp_page_index(page_index, len(pages))
    return pages[clamped_index]


def clamp_page_index(page_index: int, total_pages: int) -> int:
    if total_pages <= 0:
        return 0

    return min(max(page_index, 0), total_pages - 1)
