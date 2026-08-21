"""Text formatters for Telegram bot responses."""

from app.application.dto import (
    AddItemsResult,
    ArchivedListDTO,
    CurrentListDTO,
    FinishShoppingResult,
    ListArchivesResult,
    ListItemDTO,
    RestoreArchivedItemsResult,
    StartShoppingResult,
)
from app.application.errors import ApplicationError, ApplicationErrorCodeEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum

EMPTY_ADD_MESSAGE = (
    "🤔 Не нашел товаров для добавления. "
    "Отправьте название продукта обычным сообщением."
)
DUPLICATE_MESSAGE = "👌 Это сообщение уже обработано, ничего не добавил."
EMPTY_LIST_MESSAGE = "🧺 Список пока пуст. Отправьте товар обычным сообщением."
CLEAR_CONFIRMATION_MESSAGE = (
    "🗑️ Очистить текущий список? Это удалит товары навсегда, без архива."
)
CLEAR_CANCELLED_MESSAGE = "↩️ Очистку отменил."
CLEAR_EMPTY_MESSAGE = "🧺 Текущего списка уже нет."
DELETE_SELECTION_EMPTY_MESSAGE = "Выберите хотя бы один товар."
DELETE_SELECTION_ITEM_MISSING_MESSAGE = "Этот товар уже не в текущем списке."
INVALID_CHECKLIST_ACTION_MESSAGE = "Не получилось понять, какой товар отметить."
INVALID_ARCHIVE_ACTION_MESSAGE = "Не получилось понять действие с архивом."
SHOPPING_CHECKLIST_EMPTY_MESSAGE = "🧺 В чеклисте пока нет товаров."
EMPTY_ARCHIVE_MESSAGE = "📦 Архив пока пуст."
EMPTY_ARCHIVED_LIST_MESSAGE = "📦 В этом архивном походе нет товаров."

CATEGORY_EMOJI_BY_CODE = {
    CategoryCodeEnum.DAIRY: "🥛",
    CategoryCodeEnum.BAKERY: "🥖",
    CategoryCodeEnum.VEGETABLES_GREENS: "🥬",
    CategoryCodeEnum.FRUITS_BERRIES: "🍎",
    CategoryCodeEnum.MEAT_POULTRY: "🥩",
    CategoryCodeEnum.FISH_SEAFOOD: "🐟",
    CategoryCodeEnum.SAUSAGES_DELI: "🥓",
    CategoryCodeEnum.EGGS: "🥚",
    CategoryCodeEnum.GRAINS_PASTA_FLOUR: "🍝",
    CategoryCodeEnum.CANNED: "🥫",
    CategoryCodeEnum.FROZEN: "❄️",
    CategoryCodeEnum.SWEETS_SNACKS: "🍫",
    CategoryCodeEnum.DRINKS: "🥤",
    CategoryCodeEnum.TEA_COFFEE: "☕",
    CategoryCodeEnum.SAUCES_SPICES: "🧂",
    CategoryCodeEnum.HOUSEHOLD_CHEMICALS: "🧽",
    CategoryCodeEnum.HYGIENE: "🧼",
    CategoryCodeEnum.HOME_GOODS: "🏠",
    CategoryCodeEnum.OTHER: "🧩",
}


def format_clear_result(deleted_item_count: int) -> str:
    if deleted_item_count == 0:
        return "✨ Список очищен. Товаров в нем не было."

    return f"✨ Список очищен. Удалено товаров: {deleted_item_count}."


def format_delete_selection(current_list: CurrentListDTO, selected_count: int) -> str:
    if current_list.is_empty:
        return EMPTY_LIST_MESSAGE

    lines = [
        "✏️ Выберите товары для удаления",
        "Нажимайте на товары, затем подтвердите удаление.",
    ]
    if selected_count:
        lines.append(f"Выбрано: {selected_count}.")

    return "\n".join(lines)


def format_delete_selected_result(deleted_item_count: int) -> str:
    if deleted_item_count == 0:
        return "🗑️ Ничего не удалил."

    return f"🗑️ Удалил товаров: {deleted_item_count}."


def format_added_items(result: AddItemsResult) -> str:
    if result.is_duplicate_message:
        return DUPLICATE_MESSAGE

    if not result.added_items:
        return EMPTY_ADD_MESSAGE

    lines = ["✅ Добавил:"]
    fallback_items = []
    for item in result.added_items:
        lines.append(
            f"• {item.display_text} — "
            f"{_category_title(item.category_code, item.category_name_ru)}",
        )
        if item.is_category_fallback:
            fallback_items.append(item.display_text)

    if fallback_items:
        lines.append("")
        lines.append(
            "🧩 Пока не удалось распознать категорию, "
            'положил в "Прочие": ' + ", ".join(fallback_items),
        )

    return "\n".join(lines)


def format_current_list(current_list: CurrentListDTO) -> str:
    if current_list.is_empty:
        return EMPTY_LIST_MESSAGE

    lines = ["🧾 Текущий список:"]
    for category in current_list.categories:
        lines.append("")
        lines.append(
            f"{_category_title(category.category_code, category.category_name_ru)}:",
        )
        for item in category.items:
            lines.append(f"{_status_marker(item)} {item.display_text}")

    return "\n".join(lines)


def format_shopping_started(result: StartShoppingResult) -> str:
    return f"🛒 Начали покупки. В чеклисте товаров: {result.item_count}."


def format_checklist(current_list: CurrentListDTO) -> str:
    if current_list.is_empty:
        return SHOPPING_CHECKLIST_EMPTY_MESSAGE

    lines = ["🛒 Чеклист покупок:"]
    for category in current_list.categories:
        lines.append("")
        lines.append(
            f"{_category_title(category.category_code, category.category_name_ru)}:",
        )
        for item in category.items:
            lines.append(f"{_status_marker(item)} {item.display_text}")

    return "\n".join(lines)


def format_shopping_error(error: ValueError) -> str:
    if isinstance(error, ApplicationError):
        if error.code == ApplicationErrorCodeEnum.EMPTY_DRAFT_LIST:
            return "🧺 Список пуст. Сначала отправьте товары обычным сообщением."
        if error.code == ApplicationErrorCodeEnum.DRAFT_LIST_NOT_FOUND:
            return "🧺 Нет списка для покупок. Отправьте товары обычным сообщением."
        if error.code == ApplicationErrorCodeEnum.LIST_NOT_DRAFT:
            return "🛒 Покупки уже начаты. Откройте чеклист и отмечайте товары."
        if error.code == ApplicationErrorCodeEnum.ACTIVE_LIST_NOT_FOUND:
            return "🧺 Сейчас нет активного чеклиста покупок."

    return "Не получилось выполнить действие. Попробуйте открыть список еще раз."


def format_finish_shopping_result(result: FinishShoppingResult) -> str:
    archived_at = _format_datetime(result.archived_at)
    return f"🏁 Покупки завершены. Поход сохранен в архив: {archived_at}."


def format_archive_list(result: ListArchivesResult) -> str:
    if not result.archives:
        return EMPTY_ARCHIVE_MESSAGE

    lines = ["📦 Архив покупок:"]
    for index, archive in enumerate(result.archives, start=1):
        archived_at = _format_datetime(archive.archived_at)
        lines.append(
            f"{index}. {archived_at} — товаров: {archive.item_count}",
        )

    return "\n".join(lines)


def format_archived_list(archived_list: ArchivedListDTO) -> str:
    if archived_list.is_empty:
        return EMPTY_ARCHIVED_LIST_MESSAGE

    archived_at = _format_datetime(archived_list.archived_at)
    lines = [f"📦 Архивный поход от {archived_at}:"]
    for category in archived_list.categories:
        lines.append("")
        lines.append(
            f"{_category_title(category.category_code, category.category_name_ru)}:",
        )
        for item in category.items:
            lines.append(f"{_status_marker(item)} {item.display_text}")

    return "\n".join(lines)


def format_restore_result(result: RestoreArchivedItemsResult) -> str:
    restored_count = len(result.restored_items)
    if restored_count == 0:
        return "♻️ В архиве не нашел товаров для добавления."
    if restored_count == 1:
        item = result.restored_items[0]
        return f"♻️ Добавил из архива: {item.display_text}."

    return f"♻️ Добавил из архива товаров: {restored_count}."


def format_archive_error(error: ValueError) -> str:
    if isinstance(error, ApplicationError):
        if error.code == ApplicationErrorCodeEnum.ACTIVE_LIST_NOT_FOUND:
            return "🧺 Сейчас нет активного чеклиста покупок."
        if error.code == ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND:
            return "📦 Не нашел этот архивный поход."
        if error.code == ApplicationErrorCodeEnum.SELECTED_ARCHIVED_ITEM_NOT_IN_LIST:
            return "📦 Этот товар не относится к выбранному архивному походу."

    return (
        "Не получилось выполнить действие с архивом. Попробуйте открыть архив еще раз."
    )


def _status_marker(item: ListItemDTO) -> str:
    if item.status == ShoppingItemStatusEnum.BOUGHT:
        return "✅"
    return "☐"


def _category_title(category_code: str, category_name_ru: str) -> str:
    emoji = CATEGORY_EMOJI_BY_CODE.get(
        category_code,
        CATEGORY_EMOJI_BY_CODE[CategoryCodeEnum.OTHER],
    )
    return f"{emoji} {category_name_ru}"


def _format_datetime(value) -> str:
    return value.strftime("%d.%m.%Y %H:%M")
