"""Callback data builders and parsers for Telegram inline keyboards."""

from app.core.constants import CallbackPrefixEnum

CALLBACK_SEPARATOR = ":"


def build_toggle_item_callback(item_id: int) -> str:
    return _join_callback_parts(CallbackPrefixEnum.TOGGLE_ITEM, str(item_id))


def build_open_archived_list_callback(list_id: int) -> str:
    return _join_callback_parts(CallbackPrefixEnum.OPEN_ARCHIVED_LIST, str(list_id))


def build_restore_archived_list_callback(list_id: int) -> str:
    return _join_callback_parts(CallbackPrefixEnum.RESTORE_ARCHIVED_LIST, str(list_id))


def build_restore_archived_item_callback(list_id: int, item_id: int) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM,
        str(list_id),
        str(item_id),
    )


def parse_toggle_item_callback(callback_data: str | None) -> int | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 2 or parts[0] != CallbackPrefixEnum.TOGGLE_ITEM:
        return None

    return _parse_positive_int(parts[1])


def parse_open_archived_list_callback(callback_data: str | None) -> int | None:
    return _parse_single_id_callback(
        callback_data,
        CallbackPrefixEnum.OPEN_ARCHIVED_LIST,
    )


def parse_restore_archived_list_callback(callback_data: str | None) -> int | None:
    return _parse_single_id_callback(
        callback_data,
        CallbackPrefixEnum.RESTORE_ARCHIVED_LIST,
    )


def parse_restore_archived_item_callback(
    callback_data: str | None,
) -> tuple[int, int] | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 3 or parts[0] != CallbackPrefixEnum.RESTORE_ARCHIVED_ITEM:
        return None

    list_id = _parse_positive_int(parts[1])
    item_id = _parse_positive_int(parts[2])
    if list_id is None or item_id is None:
        return None

    return list_id, item_id


def is_toggle_item_callback(callback_data: str | None) -> bool:
    return parse_toggle_item_callback(callback_data) is not None


def is_open_archived_list_callback(callback_data: str | None) -> bool:
    return parse_open_archived_list_callback(callback_data) is not None


def is_restore_archived_list_callback(callback_data: str | None) -> bool:
    return parse_restore_archived_list_callback(callback_data) is not None


def is_restore_archived_item_callback(callback_data: str | None) -> bool:
    return parse_restore_archived_item_callback(callback_data) is not None


def _join_callback_parts(prefix: str, *values: str) -> str:
    return CALLBACK_SEPARATOR.join((prefix, *values))


def _split_callback_data(callback_data: str) -> tuple[str, ...]:
    return tuple(callback_data.split(CALLBACK_SEPARATOR))


def _parse_single_id_callback(callback_data: str | None, prefix: str) -> int | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 2 or parts[0] != prefix:
        return None

    return _parse_positive_int(parts[1])


def _parse_positive_int(value: str) -> int | None:
    try:
        parsed_value = int(value)
    except ValueError:
        return None

    if parsed_value <= 0:
        return None

    return parsed_value
