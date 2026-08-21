from app.application.dto import CurrentListDTO, ListCategoryDTO, ListItemDTO
from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.keyboards.checklist import checklist_keyboard


def test_checklist_keyboard_has_one_toggle_button_per_item() -> None:
    keyboard = checklist_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="shopping",
            title=None,
            categories=(
                ListCategoryDTO(
                    category_code=CategoryCodeEnum.DAIRY,
                    category_name_ru="Молочные продукты",
                    sort_order=10,
                    items=(
                        ListItemDTO(
                            item_id=11,
                            display_text="молоко",
                            status=ShoppingItemStatusEnum.PENDING,
                            position=1,
                        ),
                        ListItemDTO(
                            item_id=12,
                            display_text="сыр",
                            status=ShoppingItemStatusEnum.BOUGHT,
                            position=2,
                        ),
                    ),
                ),
            ),
        ),
    )

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["☐ молоко"],
        ["✅ сыр"],
    ]
    assert [
        [button.callback_data for button in row] for row in keyboard.inline_keyboard
    ] == [
        [f"{CallbackPrefixEnum.TOGGLE_ITEM}:11:0"],
        [f"{CallbackPrefixEnum.TOGGLE_ITEM}:12:0"],
    ]


def test_checklist_keyboard_paginates_category_items() -> None:
    keyboard = checklist_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="shopping",
            title=None,
            categories=(
                ListCategoryDTO(
                    category_code=CategoryCodeEnum.DAIRY,
                    category_name_ru="Молочные продукты",
                    sort_order=10,
                    items=tuple(
                        ListItemDTO(
                            item_id=item_id,
                            display_text=f"товар {item_id}",
                            status=ShoppingItemStatusEnum.PENDING,
                            position=item_id,
                        )
                        for item_id in range(1, 13)
                    ),
                ),
            ),
        ),
    )

    assert len(keyboard.inline_keyboard) == 11
    assert keyboard.inline_keyboard[0][0].text == "☐ товар 1"
    assert keyboard.inline_keyboard[9][0].text == "☐ товар 10"
    assert keyboard.inline_keyboard[10][0].text == ButtonTextEnum.NEXT_PAGE
    assert keyboard.inline_keyboard[10][0].callback_data == (
        f"{CallbackPrefixEnum.SHOPPING_CHECKLIST_PAGE}:1"
    )


def test_checklist_keyboard_last_page_has_back_only() -> None:
    keyboard = checklist_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="shopping",
            title=None,
            categories=(
                ListCategoryDTO(
                    category_code=CategoryCodeEnum.DAIRY,
                    category_name_ru="Молочные продукты",
                    sort_order=10,
                    items=tuple(
                        ListItemDTO(
                            item_id=item_id,
                            display_text=f"товар {item_id}",
                            status=ShoppingItemStatusEnum.PENDING,
                            position=item_id,
                        )
                        for item_id in range(1, 13)
                    ),
                ),
            ),
        ),
        page_index=1,
    )

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["☐ товар 11"],
        ["☐ товар 12"],
        [ButtonTextEnum.BACK],
    ]
