from app.application.dto import CurrentListDTO, ListCategoryDTO, ListItemDTO
from app.core.constants import CallbackPrefixEnum
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
        [f"{CallbackPrefixEnum.TOGGLE_ITEM}:11"],
        [f"{CallbackPrefixEnum.TOGGLE_ITEM}:12"],
    ]
