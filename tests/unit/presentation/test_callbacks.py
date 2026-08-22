from app.core.constants import CallbackPrefixEnum
from app.presentation.bot.callbacks import (
    build_archived_restore_page_callback,
    build_confirm_delete_selected_items_callback,
    build_edit_delete_page_callback,
    build_open_archived_list_callback,
    build_restore_archived_item_callback,
    build_restore_archived_list_callback,
    build_shopping_checklist_page_callback,
    build_toggle_delete_item_callback,
    build_toggle_item_callback,
    is_archived_restore_page_callback,
    is_confirm_delete_selected_items_callback,
    is_edit_delete_page_callback,
    is_open_archived_list_callback,
    is_restore_archived_item_callback,
    is_restore_archived_list_callback,
    is_shopping_checklist_page_callback,
    is_toggle_delete_item_callback,
    is_toggle_item_callback,
    parse_archived_restore_page_callback,
    parse_confirm_delete_selected_items_callback,
    parse_edit_delete_page_callback,
    parse_open_archived_list_callback,
    parse_restore_archived_item_callback,
    parse_restore_archived_list_callback,
    parse_shopping_checklist_page_callback,
    parse_toggle_delete_item_callback,
    parse_toggle_item_callback,
)


def test_build_toggle_item_callback_uses_constant_prefix() -> None:
    assert build_toggle_item_callback(42, 3) == f"{CallbackPrefixEnum.TOGGLE_ITEM}:42:3"


def test_parse_toggle_item_callback_returns_item_id_and_page() -> None:
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42") == (
        42,
        0,
    )
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42:3") == (
        42,
        3,
    )


def test_parse_toggle_item_callback_rejects_invalid_values() -> None:
    assert parse_toggle_item_callback(None) is None
    assert parse_toggle_item_callback(CallbackPrefixEnum.TOGGLE_ITEM) is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:") is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:abc") is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:0") is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42:-1") is None
    assert parse_toggle_item_callback("other:42") is None


def test_is_toggle_item_callback() -> None:
    assert is_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42") is True
    assert is_toggle_item_callback("other:42") is False


def test_build_and_parse_shopping_page_callback() -> None:
    callback_data = build_shopping_checklist_page_callback(2)

    assert callback_data == f"{CallbackPrefixEnum.SHOPPING_CHECKLIST_PAGE}:2"
    assert parse_shopping_checklist_page_callback(callback_data) == 2
    assert is_shopping_checklist_page_callback(callback_data) is True
    assert (
        parse_shopping_checklist_page_callback(
            f"{CallbackPrefixEnum.SHOPPING_CHECKLIST_PAGE}:-1",
        )
        is None
    )


def test_build_archive_callbacks_use_constant_prefixes() -> None:
    assert (
        build_open_archived_list_callback(7)
        == f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:7"
    )
    assert (
        build_restore_archived_list_callback(7)
        == f"{CallbackPrefixEnum.RESTORE_ARCHIVED_LIST}:7"
    )
    assert (
        build_restore_archived_item_callback(7, 42)
        == f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7:42"
    )
    assert (
        build_archived_restore_page_callback(7, 2)
        == f"{CallbackPrefixEnum.ARCHIVED_RESTORE_PAGE}:7:2"
    )


def test_parse_open_archived_list_callback_returns_list_id() -> None:
    callback_data = f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:7"

    assert parse_open_archived_list_callback(callback_data) == 7
    assert is_open_archived_list_callback(callback_data) is True


def test_parse_restore_archived_list_callback_returns_list_id() -> None:
    callback_data = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_LIST}:7"

    assert parse_restore_archived_list_callback(callback_data) == 7
    assert is_restore_archived_list_callback(callback_data) is True


def test_parse_restore_archived_item_callback_returns_list_and_item_ids() -> None:
    callback_data = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7:42"

    assert parse_restore_archived_item_callback(callback_data) == (7, 42)
    assert is_restore_archived_item_callback(callback_data) is True


def test_parse_archived_restore_page_callback_returns_list_and_page() -> None:
    callback_data = f"{CallbackPrefixEnum.ARCHIVED_RESTORE_PAGE}:7:2"

    assert parse_archived_restore_page_callback(callback_data) == (7, 2)
    assert is_archived_restore_page_callback(callback_data) is True


def test_parse_archive_callbacks_reject_invalid_values() -> None:
    zero_open_callback = f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:0"
    invalid_open_callback = f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:abc"
    negative_restore_list_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_LIST}:-1"
    missing_item_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7"
    zero_item_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7:0"
    invalid_list_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:abc:42"
    invalid_page_callback = f"{CallbackPrefixEnum.ARCHIVED_RESTORE_PAGE}:7:-1"

    assert parse_open_archived_list_callback(None) is None
    assert parse_open_archived_list_callback("other:7") is None
    assert parse_open_archived_list_callback(zero_open_callback) is None
    assert parse_open_archived_list_callback(invalid_open_callback) is None
    assert (
        parse_restore_archived_list_callback(
            negative_restore_list_callback,
        )
        is None
    )
    assert parse_restore_archived_item_callback(missing_item_callback) is None
    assert parse_restore_archived_item_callback(zero_item_callback) is None
    assert parse_restore_archived_item_callback(invalid_list_callback) is None
    assert parse_archived_restore_page_callback(invalid_page_callback) is None


def test_build_delete_selection_callbacks_use_constant_prefixes() -> None:
    assert (
        build_toggle_delete_item_callback(42, 3, 5)
        == f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:42:3:5"
    )
    assert (
        build_confirm_delete_selected_items_callback(3, 5)
        == f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:3:5"
    )
    assert (
        build_confirm_delete_selected_items_callback(3)
        == f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:3:0"
    )
    expected_edit_page_callback = f"{CallbackPrefixEnum.EDIT_DELETE_PAGE}:3"

    assert build_edit_delete_page_callback(3) == expected_edit_page_callback


def test_parse_toggle_delete_item_callback_returns_item_page_and_mask() -> None:
    callback_data = f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:42:3:5"

    assert parse_toggle_delete_item_callback(callback_data) == (42, 3, 5)
    assert is_toggle_delete_item_callback(callback_data) is True


def test_parse_confirm_delete_selected_items_callback_returns_page_and_mask() -> None:
    callback_data = f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:3:5"

    assert parse_confirm_delete_selected_items_callback(callback_data) == (3, 5)
    assert is_confirm_delete_selected_items_callback(callback_data) is True


def test_parse_edit_delete_page_callback_returns_page() -> None:
    callback_data = f"{CallbackPrefixEnum.EDIT_DELETE_PAGE}:3"

    assert parse_edit_delete_page_callback(callback_data) == 3
    assert is_edit_delete_page_callback(callback_data) is True


def test_parse_delete_selection_callbacks_reject_invalid_values() -> None:
    assert parse_toggle_delete_item_callback(None) is None
    assert parse_toggle_delete_item_callback("other:42:7") is None
    assert (
        parse_toggle_delete_item_callback(
            f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:0:3:7",
        )
        is None
    )
    assert (
        parse_toggle_delete_item_callback(
            f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:42:-1:7",
        )
        is None
    )
    assert (
        parse_toggle_delete_item_callback(
            f"{CallbackPrefixEnum.TOGGLE_DELETE_ITEM}:42:3:abc",
        )
        is None
    )
    assert (
        parse_confirm_delete_selected_items_callback(
            f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:-1:7",
        )
        is None
    )
    assert (
        parse_confirm_delete_selected_items_callback(
            f"{CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS}:7:abc",
        )
        is None
    )
    assert (
        parse_edit_delete_page_callback(
            f"{CallbackPrefixEnum.EDIT_DELETE_PAGE}:-1:7",
        )
        is None
    )
    assert (
        parse_edit_delete_page_callback(
            f"{CallbackPrefixEnum.EDIT_DELETE_PAGE}:7:3",
        )
        is None
    )


def test_delete_selection_callbacks_stay_within_telegram_limit() -> None:
    telegram_callback_data_limit = 64
    large_item_id = 9_223_372_036_854_775_807
    large_page_index = 999_999
    all_page_items_selected_mask = 1023

    callbacks = (
        build_toggle_delete_item_callback(
            large_item_id,
            large_page_index,
            all_page_items_selected_mask,
        ),
        build_confirm_delete_selected_items_callback(
            large_page_index,
            all_page_items_selected_mask,
        ),
        build_edit_delete_page_callback(large_page_index),
    )

    assert all(
        len(callback_data.encode("utf-8")) <= telegram_callback_data_limit
        for callback_data in callbacks
    )
