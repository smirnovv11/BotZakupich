import pytest
from app.application.dto import ListCategoryDTO, ListItemDTO
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.pagination import (
    CHECKLIST_PAGE_SIZE,
    CHECKLIST_PAGE_TAIL_ALLOWANCE,
    build_checklist_pages,
    clamp_page_index,
    get_checklist_page,
)


def make_item(item_id: int, *, position: int | None = None) -> ListItemDTO:
    return ListItemDTO(
        item_id=item_id,
        display_text=f"товар {item_id}",
        status=ShoppingItemStatusEnum.PENDING,
        position=item_id if position is None else position,
    )


def make_category(
    category_code: str,
    sort_order: int,
    item_ids: range | tuple[int, ...],
) -> ListCategoryDTO:
    return ListCategoryDTO(
        category_code=category_code,
        category_name_ru=category_code,
        sort_order=sort_order,
        items=tuple(make_item(item_id) for item_id in item_ids),
    )


@pytest.mark.parametrize(
    ("item_count", "expected_page_sizes"),
    [
        (0, []),
        (1, [1]),
        (10, [10]),
        (11, [11]),
        (12, [12]),
        (13, [10, 3]),
        (20, [10, 10]),
        (21, [10, 11]),
        (22, [10, 12]),
        (23, [10, 10, 3]),
        (31, [10, 10, 11]),
        (32, [10, 10, 12]),
        (33, [10, 10, 10, 3]),
    ],
)
def test_build_checklist_pages_absorbs_short_tail(
    item_count: int,
    expected_page_sizes: list[int],
) -> None:
    categories = (
        make_category(
            CategoryCodeEnum.DAIRY,
            10,
            range(1, item_count + 1),
        ),
    )

    pages = build_checklist_pages(categories)

    assert [len(page.items) for page in pages] == expected_page_sizes
    assert all(
        len(page.items) <= CHECKLIST_PAGE_SIZE + CHECKLIST_PAGE_TAIL_ALLOWANCE
        for page in pages
    )


def test_sparse_categories_share_one_page_in_category_order() -> None:
    pages = build_checklist_pages(
        (
            make_category(CategoryCodeEnum.BAKERY, 20, (4, 5)),
            make_category(CategoryCodeEnum.FRUITS_BERRIES, 40, (8,)),
            make_category(CategoryCodeEnum.DAIRY, 10, (1, 2, 3)),
            make_category(CategoryCodeEnum.VEGETABLES_GREENS, 30, (6, 7)),
            make_category(CategoryCodeEnum.OTHER, 1000, ()),
        ),
    )

    assert len(pages) == 1
    assert [category.category_code for category in pages[0].categories] == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
        CategoryCodeEnum.VEGETABLES_GREENS,
        CategoryCodeEnum.FRUITS_BERRIES,
    ]
    assert [item.item_id for item in pages[0].items] == list(range(1, 9))


def test_category_can_continue_and_mix_with_next_category() -> None:
    pages = build_checklist_pages(
        (
            make_category(CategoryCodeEnum.BAKERY, 20, (101,)),
            make_category(CategoryCodeEnum.DAIRY, 10, range(1, 13)),
        ),
    )

    assert [len(page.items) for page in pages] == [10, 3]
    assert [category.category_code for category in pages[0].categories] == [
        CategoryCodeEnum.DAIRY,
    ]
    assert [category.category_code for category in pages[1].categories] == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
    ]
    assert [item.item_id for item in pages[1].items] == [11, 12, 101]


def test_items_are_sorted_by_position_inside_category() -> None:
    category = ListCategoryDTO(
        category_code=CategoryCodeEnum.DAIRY,
        category_name_ru="Молочные продукты",
        sort_order=10,
        items=(
            make_item(1, position=30),
            make_item(2, position=10),
            make_item(3, position=20),
        ),
    )

    page = get_checklist_page((category,), 0)

    assert page is not None
    assert [item.item_id for item in page.items] == [2, 3, 1]


def test_get_checklist_page_clamps_out_of_range_indexes() -> None:
    categories = (make_category(CategoryCodeEnum.DAIRY, 10, (1,)),)

    assert get_checklist_page(categories, -1).page_index == 0
    assert get_checklist_page(categories, 99).page_index == 0


def test_clamp_page_index() -> None:
    assert clamp_page_index(-1, 3) == 0
    assert clamp_page_index(2, 3) == 2
    assert clamp_page_index(9, 3) == 2
    assert clamp_page_index(9, 0) == 0


@pytest.mark.parametrize(
    ("page_size", "tail_allowance"),
    [(0, 2), (-1, 2), (10, -1)],
)
def test_build_checklist_pages_rejects_invalid_limits(
    page_size: int,
    tail_allowance: int,
) -> None:
    with pytest.raises(ValueError):
        build_checklist_pages(
            (),
            page_size=page_size,
            tail_allowance=tail_allowance,
        )
