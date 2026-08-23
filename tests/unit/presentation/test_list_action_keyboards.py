from app.application.dto import CurrentListDTO, ListCategoryDTO, ListItemDTO
from app.core.constants import ButtonTextEnum, CallbackPrefixEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.callbacks import build_delete_page_fingerprint
from app.presentation.bot.keyboards.list_actions import (
    clear_list_confirmation_keyboard,
    current_list_actions_keyboard,
    delete_items_keyboard,
)


def test_current_list_actions_keyboard_has_edit_and_clear_buttons() -> None:
    keyboard = current_list_actions_keyboard()
    edit_button = keyboard.inline_keyboard[0][0]
    clear_button = keyboard.inline_keyboard[1][0]

    assert edit_button.text == ButtonTextEnum.EDIT_LIST
    assert edit_button.callback_data == CallbackPrefixEnum.EDIT_LIST
    assert clear_button.text == ButtonTextEnum.CLEAR_LIST
    assert clear_button.callback_data == CallbackPrefixEnum.CLEAR_LIST


def test_delete_items_keyboard_marks_selected_items() -> None:
    keyboard = delete_items_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="draft",
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
                            display_text="сливки",
                            status=ShoppingItemStatusEnum.PENDING,
                            position=2,
                        ),
                    ),
                ),
            ),
        ),
        selected_item_ids=(12,),
    )

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["☐ 🥛 молоко"],
        ["☑️ 🥛 сливки"],
        [ButtonTextEnum.DELETE_SELECTED],
        [ButtonTextEnum.BACK_TO_LIST],
    ]
    assert keyboard.inline_keyboard[0][0].callback_data == (
        f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:11:0:2:"
        f"{build_delete_page_fingerprint((11, 12))}"
    )
    assert keyboard.inline_keyboard[1][0].callback_data == (
        f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:12:0:2:"
        f"{build_delete_page_fingerprint((11, 12))}"
    )
    assert keyboard.inline_keyboard[2][0].callback_data == (
        f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:0:2:"
        f"{build_delete_page_fingerprint((11, 12))}"
    )
    assert (
        keyboard.inline_keyboard[3][0].callback_data
        == CallbackPrefixEnum.CANCEL_EDIT_LIST
    )


def test_delete_items_keyboard_paginates_and_preserves_selected_ids() -> None:
    keyboard = delete_items_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="draft",
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
                        for item_id in range(1, 14)
                    ),
                ),
            ),
        ),
        selected_item_ids=(2, 11),
    )

    assert len(keyboard.inline_keyboard) == 13
    assert keyboard.inline_keyboard[1][0].text == "☑️ 🥛 товар 2"
    assert keyboard.inline_keyboard[10][0].text == ButtonTextEnum.NEXT_PAGE
    assert keyboard.inline_keyboard[10][0].callback_data == (
        f"{CallbackPrefixEnum.EDIT_DELETE_PAGE}:1"
    )
    assert keyboard.inline_keyboard[11][0].callback_data == (
        f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:0:2:"
        f"{build_delete_page_fingerprint(tuple(range(1, 11)))}"
    )


def test_delete_items_keyboard_encodes_twelve_selected_items() -> None:
    item_ids = tuple(range(1, 13))
    keyboard = delete_items_keyboard(
        CurrentListDTO(
            list_id=1,
            list_status="draft",
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
                        for item_id in item_ids
                    ),
                ),
            ),
        ),
        selected_item_ids=item_ids,
    )

    assert len(keyboard.inline_keyboard) == 14
    assert all(row[0].text.startswith("☑️ 🥛") for row in keyboard.inline_keyboard[:12])
    assert keyboard.inline_keyboard[12][0].callback_data == (
        f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:0:4095:"
        f"{build_delete_page_fingerprint(item_ids)}"
    )


def test_clear_list_confirmation_keyboard_has_confirm_and_cancel_buttons() -> None:
    keyboard = clear_list_confirmation_keyboard()
    confirm_button, cancel_button = keyboard.inline_keyboard[0]

    assert confirm_button.text == ButtonTextEnum.CONFIRM_CLEAR_LIST
    assert confirm_button.callback_data == CallbackPrefixEnum.CONFIRM_CLEAR_LIST
    assert cancel_button.text == ButtonTextEnum.CANCEL
    assert cancel_button.callback_data == CallbackPrefixEnum.CANCEL_CLEAR_LIST
