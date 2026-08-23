"""Callback data builders and parsers for Telegram inline keyboards."""

from hashlib import blake2s

from app.core.constants import CallbackPrefixEnum

CALLBACK_SEPARATOR = ":"
DELETE_PAGE_FINGERPRINT_SIZE = 8
DELETE_PAGE_FINGERPRINT_HEX_LENGTH = DELETE_PAGE_FINGERPRINT_SIZE * 2


def build_toggle_item_callback(item_id: int, page_index: int = 0) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.TOGGLE_ITEM,
        str(item_id),
        str(page_index),
    )


def build_shopping_checklist_page_callback(page_index: int) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.SHOPPING_CHECKLIST_PAGE,
        str(page_index),
    )


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


def build_archived_restore_page_callback(list_id: int, page_index: int) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.ARCHIVED_RESTORE_PAGE,
        str(list_id),
        str(page_index),
    )


def build_toggle_delete_item_callback(
    item_id: int,
    page_index: int,
    selected_item_mask: int,
    page_fingerprint: str,
) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.TOGGLE_DELETE_ITEM,
        str(item_id),
        str(page_index),
        str(selected_item_mask),
        page_fingerprint,
    )


def build_confirm_delete_selected_items_callback(
    page_index: int,
    selected_item_mask: int,
    page_fingerprint: str,
) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS,
        str(page_index),
        str(selected_item_mask),
        page_fingerprint,
    )


def build_edit_delete_page_callback(page_index: int) -> str:
    return _join_callback_parts(
        CallbackPrefixEnum.EDIT_DELETE_PAGE,
        str(page_index),
    )


def parse_toggle_item_callback(callback_data: str | None) -> tuple[int, int] | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) not in (2, 3) or parts[0] != CallbackPrefixEnum.TOGGLE_ITEM:
        return None

    item_id = _parse_positive_int(parts[1])
    if item_id is None:
        return None

    if len(parts) == 2:
        return item_id, 0

    page_index = _parse_non_negative_int(parts[2])
    if page_index is None:
        return None

    return item_id, page_index


def parse_shopping_checklist_page_callback(callback_data: str | None) -> int | None:
    return _parse_single_page_callback(
        callback_data,
        CallbackPrefixEnum.SHOPPING_CHECKLIST_PAGE,
    )


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


def parse_archived_restore_page_callback(
    callback_data: str | None,
) -> tuple[int, int] | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 3 or parts[0] != CallbackPrefixEnum.ARCHIVED_RESTORE_PAGE:
        return None

    list_id = _parse_positive_int(parts[1])
    page_index = _parse_non_negative_int(parts[2])
    if list_id is None or page_index is None:
        return None

    return list_id, page_index


def parse_toggle_delete_item_callback(
    callback_data: str | None,
) -> tuple[int, int, int, str] | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 5 or parts[0] != CallbackPrefixEnum.TOGGLE_DELETE_ITEM:
        return None

    item_id = _parse_positive_int(parts[1])
    page_index = _parse_non_negative_int(parts[2])
    selected_item_mask = _parse_non_negative_int(parts[3])
    page_fingerprint = _parse_page_fingerprint(parts[4])
    if (
        item_id is None
        or page_index is None
        or selected_item_mask is None
        or page_fingerprint is None
    ):
        return None

    return item_id, page_index, selected_item_mask, page_fingerprint


def parse_confirm_delete_selected_items_callback(
    callback_data: str | None,
) -> tuple[int, int, str] | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if parts[0] != CallbackPrefixEnum.CONFIRM_DELETE_SELECTED_ITEMS:
        return None

    if len(parts) != 4:
        return None

    page_index = _parse_non_negative_int(parts[1])
    selected_item_mask = _parse_non_negative_int(parts[2])
    page_fingerprint = _parse_page_fingerprint(parts[3])
    if page_index is None or selected_item_mask is None or page_fingerprint is None:
        return None

    return page_index, selected_item_mask, page_fingerprint


def parse_edit_delete_page_callback(callback_data: str | None) -> int | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 2 or parts[0] != CallbackPrefixEnum.EDIT_DELETE_PAGE:
        return None

    return _parse_non_negative_int(parts[1])


def is_toggle_item_callback(callback_data: str | None) -> bool:
    return parse_toggle_item_callback(callback_data) is not None


def is_shopping_checklist_page_callback(callback_data: str | None) -> bool:
    return parse_shopping_checklist_page_callback(callback_data) is not None


def is_open_archived_list_callback(callback_data: str | None) -> bool:
    return parse_open_archived_list_callback(callback_data) is not None


def is_restore_archived_list_callback(callback_data: str | None) -> bool:
    return parse_restore_archived_list_callback(callback_data) is not None


def is_restore_archived_item_callback(callback_data: str | None) -> bool:
    return parse_restore_archived_item_callback(callback_data) is not None


def is_archived_restore_page_callback(callback_data: str | None) -> bool:
    return parse_archived_restore_page_callback(callback_data) is not None


def is_toggle_delete_item_callback(callback_data: str | None) -> bool:
    return parse_toggle_delete_item_callback(callback_data) is not None


def is_confirm_delete_selected_items_callback(callback_data: str | None) -> bool:
    return parse_confirm_delete_selected_items_callback(callback_data) is not None


def is_edit_delete_page_callback(callback_data: str | None) -> bool:
    return parse_edit_delete_page_callback(callback_data) is not None


def is_legacy_delete_selection_callback(callback_data: str | None) -> bool:
    if callback_data is None:
        return False

    prefix = callback_data.split(CALLBACK_SEPARATOR, maxsplit=1)[0]
    return prefix in {
        CallbackPrefixEnum.LEGACY_TOGGLE_DELETE_ITEM,
        CallbackPrefixEnum.LEGACY_CONFIRM_DELETE_SELECTED_ITEMS,
    }


def build_delete_page_fingerprint(item_ids: tuple[int, ...]) -> str:
    payload = CALLBACK_SEPARATOR.join(str(item_id) for item_id in item_ids)
    return blake2s(
        payload.encode("ascii"),
        digest_size=DELETE_PAGE_FINGERPRINT_SIZE,
    ).hexdigest()


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


def _parse_single_page_callback(callback_data: str | None, prefix: str) -> int | None:
    if callback_data is None:
        return None

    parts = _split_callback_data(callback_data)
    if len(parts) != 2 or parts[0] != prefix:
        return None

    return _parse_non_negative_int(parts[1])


def _parse_positive_int(value: str) -> int | None:
    try:
        parsed_value = int(value)
    except ValueError:
        return None

    if parsed_value <= 0:
        return None

    return parsed_value


def _parse_non_negative_int(value: str) -> int | None:
    try:
        parsed_value = int(value)
    except ValueError:
        return None

    if parsed_value < 0:
        return None

    return parsed_value


def _parse_page_fingerprint(value: str) -> str | None:
    if len(value) != DELETE_PAGE_FINGERPRINT_HEX_LENGTH:
        return None

    if any(character not in "0123456789abcdef" for character in value):
        return None

    return value
