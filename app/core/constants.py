"""Bot-facing command, button, and callback constants."""


class BotCommandEnum:
    START = "start"
    LIST = "list"
    ARCHIVE = "archive"


class ButtonTextEnum:
    SHOW_LIST = "🧾 Список"
    EDIT_LIST = "✏️ Изменить"
    CLEAR_LIST = "🧹 Очистить всё"
    CONFIRM_CLEAR_LIST = "✅ Да, очистить"
    DELETE_SELECTED = "🗑️ Удалить выбранное"
    CANCEL = "↩️ Отмена"
    BACK = "⬅️ Назад"
    BACK_TO_LIST = "↩️ К списку"
    START_SHOPPING = "🛒 Начать покупки"
    FINISH_SHOPPING = "🏁 Завершить"
    ARCHIVE = "📦 Архив"
    RESTORE_ALL = "♻️ Добавить все"
    RESTORE_SELECTED = "☑️ Добавить выбранные"
    NEXT_PAGE = "Вперед ➡️"


class CallbackPrefixEnum:
    START_SHOPPING = "shopping_start"
    FINISH_SHOPPING = "shopping_finish"
    TOGGLE_ITEM = "item_toggle"
    SHOPPING_CHECKLIST_PAGE = "scp"
    EDIT_LIST = "le"
    TOGGLE_DELETE_ITEM = "ldi2"
    CONFIRM_DELETE_SELECTED_ITEMS = "ldc2"
    LEGACY_TOGGLE_DELETE_ITEM = "ldi"
    LEGACY_CONFIRM_DELETE_SELECTED_ITEMS = "ldc"
    EDIT_DELETE_PAGE = "edp"
    CANCEL_EDIT_LIST = "lec"
    CLEAR_LIST = "list_clear"
    CONFIRM_CLEAR_LIST = "list_clear_confirm"
    CANCEL_CLEAR_LIST = "list_clear_cancel"
    OPEN_ARCHIVE = "archive_open"
    OPEN_ARCHIVED_LIST = "archive_list_open"
    ARCHIVED_RESTORE_PAGE = "arp"
    RESTORE_ARCHIVED_ITEM = "archive_item_restore"
    RESTORE_ARCHIVED_LIST = "archive_list_restore"
