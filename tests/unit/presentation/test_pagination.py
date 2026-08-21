from app.application.dto import ListCategoryDTO, ListItemDTO
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.pagination import (
    CHECKLIST_PAGE_SIZE,
    build_checklist_pages,
    clamp_page_index,
    get_checklist_page,
)


def make_item(item_id: int) -> ListItemDTO:
    return ListItemDTO(
        item_id=item_id,
        display_text=f"товар {item_id}",
        status=ShoppingItemStatusEnum.PENDING,
        position=item_id,
    )


def test_build_checklist_pages_sorts_categories_and_splits_large_categories() -> None:
    pages = build_checklist_pages(
        (
            ListCategoryDTO(
                category_code=CategoryCodeEnum.BAKERY,
                category_name_ru="Хлеб и выпечка",
                sort_order=20,
                items=(make_item(201),),
            ),
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=tuple(make_item(item_id) for item_id in range(1, 13)),
            ),
            ListCategoryDTO(
                category_code=CategoryCodeEnum.OTHER,
                category_name_ru="Прочие",
                sort_order=1000,
                items=(),
            ),
        ),
    )

    assert len(pages) == 3
    assert [page.category_code for page in pages] == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
    ]
    assert [len(page.items) for page in pages] == [
        CHECKLIST_PAGE_SIZE,
        2,
        1,
    ]
    assert pages[0].page_index == 0
    assert pages[0].total_pages == 3
    assert pages[0].has_previous is False
    assert pages[0].has_next is True
    assert pages[2].has_previous is True
    assert pages[2].has_next is False


def test_get_checklist_page_clamps_out_of_range_indexes() -> None:
    categories = (
        ListCategoryDTO(
            category_code=CategoryCodeEnum.DAIRY,
            category_name_ru="Молочные продукты",
            sort_order=10,
            items=(make_item(1),),
        ),
    )

    assert get_checklist_page(categories, -1).page_index == 0
    assert get_checklist_page(categories, 99).page_index == 0


def test_clamp_page_index() -> None:
    assert clamp_page_index(-1, 3) == 0
    assert clamp_page_index(2, 3) == 2
    assert clamp_page_index(9, 3) == 2
    assert clamp_page_index(9, 0) == 0
