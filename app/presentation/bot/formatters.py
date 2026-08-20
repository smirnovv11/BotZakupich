"""Text formatters for Telegram bot responses."""

from app.application.dto import (
    AddItemsResult,
    CurrentListDTO,
    ListItemDTO,
)
from app.domain.enums import ShoppingItemStatusEnum

EMPTY_ADD_MESSAGE = (
    "Не нашел товаров для добавления. Отправьте название продукта обычным сообщением."
)
DUPLICATE_MESSAGE = "Это сообщение уже обработано, ничего не добавил."
EMPTY_LIST_MESSAGE = "Список пока пуст. Отправьте товар обычным сообщением."


def format_added_items(result: AddItemsResult) -> str:
    if result.is_duplicate_message:
        return DUPLICATE_MESSAGE

    if not result.added_items:
        return EMPTY_ADD_MESSAGE

    lines = ["Добавил:"]
    fallback_items = []
    for item in result.added_items:
        lines.append(f"- {item.display_text} — {item.category_name_ru}")
        if item.is_category_fallback:
            fallback_items.append(item.display_text)

    if fallback_items:
        lines.append("")
        lines.append(
            "Пока не удалось распознать категорию, "
            'положил в "Прочие": ' + ", ".join(fallback_items),
        )

    return "\n".join(lines)


def format_current_list(current_list: CurrentListDTO) -> str:
    if current_list.is_empty:
        return EMPTY_LIST_MESSAGE

    lines = ["Текущий список:"]
    for category in current_list.categories:
        lines.append("")
        lines.append(f"{category.category_name_ru}:")
        for item in category.items:
            lines.append(f"{_status_marker(item)} {item.display_text}")

    return "\n".join(lines)


def _status_marker(item: ListItemDTO) -> str:
    if item.status == ShoppingItemStatusEnum.BOUGHT:
        return "[x]"
    return "[ ]"
