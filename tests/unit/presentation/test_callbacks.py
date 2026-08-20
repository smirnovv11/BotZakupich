from app.core.constants import CallbackPrefixEnum
from app.presentation.bot.callbacks import (
    build_open_archived_list_callback,
    build_restore_archived_item_callback,
    build_restore_archived_list_callback,
    build_toggle_item_callback,
    is_open_archived_list_callback,
    is_restore_archived_item_callback,
    is_restore_archived_list_callback,
    is_toggle_item_callback,
    parse_open_archived_list_callback,
    parse_restore_archived_item_callback,
    parse_restore_archived_list_callback,
    parse_toggle_item_callback,
)


def test_build_toggle_item_callback_uses_constant_prefix() -> None:
    assert build_toggle_item_callback(42) == f"{CallbackPrefixEnum.TOGGLE_ITEM}:42"


def test_parse_toggle_item_callback_returns_item_id() -> None:
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42") == 42


def test_parse_toggle_item_callback_rejects_invalid_values() -> None:
    assert parse_toggle_item_callback(None) is None
    assert parse_toggle_item_callback(CallbackPrefixEnum.TOGGLE_ITEM) is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:") is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:abc") is None
    assert parse_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:0") is None
    assert parse_toggle_item_callback("other:42") is None


def test_is_toggle_item_callback() -> None:
    assert is_toggle_item_callback(f"{CallbackPrefixEnum.TOGGLE_ITEM}:42") is True
    assert is_toggle_item_callback("other:42") is False


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


def test_parse_archive_callbacks_reject_invalid_values() -> None:
    zero_open_callback = f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:0"
    invalid_open_callback = f"{CallbackPrefixEnum.OPEN_ARCHIVED_LIST}:abc"
    negative_restore_list_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_LIST}:-1"
    missing_item_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7"
    zero_item_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:7:0"
    invalid_list_callback = f"{CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM}:abc:42"

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
