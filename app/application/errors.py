"""Stable application-layer errors for use-case failures."""


class ApplicationErrorCodeEnum:
    DRAFT_LIST_NOT_FOUND = "draft_list_not_found"
    LIST_NOT_DRAFT = "list_not_draft"
    EMPTY_DRAFT_LIST = "empty_draft_list"
    ACTIVE_LIST_NOT_FOUND = "active_list_not_found"
    ITEM_NOT_FOUND = "item_not_found"
    ITEM_OUTSIDE_ACTIVE_LIST = "item_outside_active_list"
    UNSUPPORTED_ITEM_STATUS = "unsupported_item_status"
    ARCHIVED_LIST_NOT_FOUND = "archived_list_not_found"
    SELECTED_ARCHIVED_ITEM_NOT_IN_LIST = "selected_archived_item_not_in_list"


class ApplicationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
