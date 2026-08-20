"""Bot-facing command, button, and callback constants."""


class BotCommandEnum:
    START = "start"
    LIST = "list"
    ARCHIVE = "archive"


class ButtonTextEnum:
    SHOW_LIST = "Список"
    START_SHOPPING = "Начать покупки"
    FINISH_SHOPPING = "Завершить"
    ARCHIVE = "Архив"
    RESTORE_ALL = "Добавить все"
    RESTORE_SELECTED = "Добавить выбранные"
    BACK = "Назад"


class CallbackPrefixEnum:
    START_SHOPPING = "shopping_start"
    FINISH_SHOPPING = "shopping_finish"
    TOGGLE_ITEM = "item_toggle"
    OPEN_ARCHIVE = "archive_open"
    OPEN_ARCHIVED_LIST = "archive_list_open"
    RESTORE_ARCHIVED_ITEM = "archive_item_restore"
    RESTORE_ARCHIVED_LIST = "archive_list_restore"
