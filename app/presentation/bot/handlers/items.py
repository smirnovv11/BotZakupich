"""Handlers for adding items and viewing the current shopping list."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.dto import (
    AddItemsCommand,
    ClearCurrentListCommand,
    CurrentListDTO,
    DeleteCurrentListItemsCommand,
    GetCurrentListQuery,
    TelegramUserDTO,
)
from app.core.config import Settings
from app.core.constants import BotCommandEnum, ButtonTextEnum, CallbackPrefixEnum
from app.presentation.bot.callbacks import (
    build_delete_page_fingerprint,
    is_confirm_delete_selected_items_callback,
    is_edit_delete_page_callback,
    is_legacy_delete_selection_callback,
    is_toggle_delete_item_callback,
    parse_confirm_delete_selected_items_callback,
    parse_edit_delete_page_callback,
    parse_toggle_delete_item_callback,
)
from app.presentation.bot.dependencies import (
    make_add_items_use_case,
    make_clear_current_list_use_case,
    make_delete_current_list_items_use_case,
    make_get_current_list_use_case,
)
from app.presentation.bot.formatters import (
    CLEAR_CANCELLED_MESSAGE,
    CLEAR_CONFIRMATION_MESSAGE,
    CLEAR_EMPTY_MESSAGE,
    DELETE_SELECTION_EMPTY_MESSAGE,
    DELETE_SELECTION_ITEM_MISSING_MESSAGE,
    DELETE_SELECTION_STALE_MESSAGE,
    format_added_items,
    format_clear_result,
    format_current_list,
    format_delete_selected_result,
    format_delete_selection,
)
from app.presentation.bot.keyboards.list_actions import (
    clear_list_confirmation_keyboard,
    current_list_actions_keyboard,
    delete_items_keyboard,
)
from app.presentation.bot.keyboards.main import main_menu_keyboard
from app.presentation.bot.pagination import (
    build_checklist_pages,
    clamp_page_index,
    get_checklist_page,
)

MENU_BUTTON_TEXTS = (
    ButtonTextEnum.SHOW_LIST,
    ButtonTextEnum.RESTORE_ALL,
    ButtonTextEnum.RESTORE_SELECTED,
    ButtonTextEnum.BACK,
)
NOT_READY_MENU_MESSAGE = "🔜 Эта кнопка будет подключена в следующих шагах."
TEXT_ITEM_HINT_MESSAGE = "✍️ Отправьте название товара обычным сообщением."

items_router = Router(name="items")


@items_router.message(Command(BotCommandEnum.LIST))
async def handle_list_command(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _answer_current_list(message, session_factory)


@items_router.message(lambda message: message.text == ButtonTextEnum.SHOW_LIST)
async def handle_show_list_button(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _answer_current_list(message, session_factory)


@items_router.message(lambda message: message.text is not None)
async def handle_add_items_text(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> None:
    raw_text = message.text or ""
    if is_command_text(raw_text):
        return

    if is_menu_button_text(raw_text):
        await message.answer(
            NOT_READY_MENU_MESSAGE,
            reply_markup=main_menu_keyboard(),
        )
        return

    if not is_add_item_text(raw_text):
        await message.answer(
            TEXT_ITEM_HINT_MESSAGE,
            reply_markup=main_menu_keyboard(),
        )
        return

    use_case = make_add_items_use_case(session_factory, settings)
    result = await use_case.execute(
        AddItemsCommand(
            user=telegram_user_from_aiogram_user(message.from_user),
            telegram_chat_id=message.chat.id,
            telegram_message_id=message.message_id,
            raw_text=raw_text,
            received_at=message.date,
        ),
    )

    await message.answer(
        format_added_items(result),
        reply_markup=main_menu_keyboard(),
    )


@items_router.callback_query(
    lambda callback: callback.data == CallbackPrefixEnum.CLEAR_LIST,
)
async def handle_clear_list_request(callback: CallbackQuery) -> None:
    await callback.answer("🗑️ Подтвердите очистку ниже.")
    if callback.message is not None:
        await callback.message.answer(
            CLEAR_CONFIRMATION_MESSAGE,
            reply_markup=clear_list_confirmation_keyboard(),
        )


@items_router.callback_query(
    lambda callback: callback.data == CallbackPrefixEnum.CONFIRM_CLEAR_LIST,
)
async def handle_clear_list_confirm(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await callback.answer("✨ Готово.")
    if callback.from_user is None or callback.message is None:
        return

    use_case = make_clear_current_list_use_case(session_factory)
    result = await use_case.execute(
        ClearCurrentListCommand(telegram_user_id=callback.from_user.id),
    )
    response_text = (
        CLEAR_EMPTY_MESSAGE
        if result.list_id is None
        else format_clear_result(result.deleted_item_count)
    )

    await callback.message.answer(
        response_text,
        reply_markup=main_menu_keyboard(),
    )


@items_router.callback_query(
    lambda callback: callback.data == CallbackPrefixEnum.CANCEL_CLEAR_LIST,
)
async def handle_clear_list_cancel(callback: CallbackQuery) -> None:
    await callback.answer(CLEAR_CANCELLED_MESSAGE)
    if callback.message is not None:
        await callback.message.answer(
            CLEAR_CANCELLED_MESSAGE,
            reply_markup=main_menu_keyboard(),
        )


async def _answer_current_list(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    use_case = make_get_current_list_use_case(session_factory)
    user = telegram_user_from_aiogram_user(message.from_user)
    current_list = await use_case.execute(
        GetCurrentListQuery(telegram_user_id=user.telegram_user_id),
    )

    await message.answer(
        format_current_list(current_list),
        reply_markup=(
            main_menu_keyboard()
            if current_list.is_empty
            else current_list_actions_keyboard()
        ),
    )


@items_router.callback_query(
    lambda callback: callback.data == CallbackPrefixEnum.EDIT_LIST,
)
async def handle_edit_list_request(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    current_list = await _get_current_list(session_factory, callback.from_user.id)
    if current_list.is_empty:
        await callback.answer(CLEAR_EMPTY_MESSAGE, show_alert=True)
        return

    await callback.answer("✏️ Выберите товары.")
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_delete_selection(current_list, selected_count=0),
            reply_markup=delete_items_keyboard(current_list, ()),
        )


@items_router.callback_query(
    lambda callback: is_toggle_delete_item_callback(callback.data),
)
async def handle_toggle_delete_item_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    parsed_callback = parse_toggle_delete_item_callback(callback.data)
    if parsed_callback is None:
        await callback.answer(
            "Не получилось понять, какой товар выбрать.",
            show_alert=True,
        )
        return

    item_id, page_index, selected_item_mask, page_fingerprint = parsed_callback
    current_list = await _get_current_list(session_factory, callback.from_user.id)
    if not _delete_page_matches_fingerprint(
        current_list,
        page_index,
        page_fingerprint,
    ):
        await _show_stale_delete_selection(callback, current_list, page_index)
        return

    current_item_ids = _current_item_ids(current_list)
    if item_id not in current_item_ids:
        await callback.answer(DELETE_SELECTION_ITEM_MISSING_MESSAGE, show_alert=True)
        return

    selected_ids = set(
        _selected_item_ids_from_page_mask(current_list, page_index, selected_item_mask),
    )
    if item_id in selected_ids:
        selected_ids.remove(item_id)
    else:
        selected_ids.add(item_id)
    updated_selected_ids = tuple(sorted(selected_ids))

    await callback.answer("✅ Обновил выбор.")
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_delete_selection(
                current_list,
                selected_count=len(updated_selected_ids),
                page_index=page_index,
            ),
            reply_markup=delete_items_keyboard(
                current_list,
                updated_selected_ids,
                page_index,
            ),
        )


@items_router.callback_query(
    lambda callback: is_confirm_delete_selected_items_callback(callback.data),
)
async def handle_delete_selected_items_confirm(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    parsed_callback = parse_confirm_delete_selected_items_callback(callback.data)
    if parsed_callback is None:
        await callback.answer("Не получилось понять, что удалить.", show_alert=True)
        return

    page_index, selected_item_mask, page_fingerprint = parsed_callback
    current_list_before_delete = await _get_current_list(
        session_factory,
        callback.from_user.id,
    )
    if not _delete_page_matches_fingerprint(
        current_list_before_delete,
        page_index,
        page_fingerprint,
    ):
        await _show_stale_delete_selection(
            callback,
            current_list_before_delete,
            page_index,
        )
        return

    selected_item_ids = _selected_item_ids_from_page_mask(
        current_list_before_delete,
        page_index,
        selected_item_mask,
    )
    if not selected_item_ids:
        await callback.answer(DELETE_SELECTION_EMPTY_MESSAGE, show_alert=True)
        return

    use_case = make_delete_current_list_items_use_case(session_factory)
    result = await use_case.execute(
        DeleteCurrentListItemsCommand(
            telegram_user_id=callback.from_user.id,
            item_ids=selected_item_ids,
        ),
    )
    current_list = await _get_current_list(session_factory, callback.from_user.id)
    page_count = len(build_checklist_pages(current_list.categories))
    next_page_index = clamp_page_index(page_index, page_count)

    await callback.answer(format_delete_selected_result(result.deleted_item_count))
    if isinstance(callback.message, Message):
        if current_list.is_empty:
            await callback.message.edit_text(
                format_current_list(current_list),
                reply_markup=None,
            )
            return

        await callback.message.edit_text(
            format_delete_selection(
                current_list,
                selected_count=0,
                page_index=next_page_index,
            ),
            reply_markup=delete_items_keyboard(current_list, (), next_page_index),
        )


@items_router.callback_query(
    lambda callback: is_edit_delete_page_callback(callback.data),
)
async def handle_edit_delete_page_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    parsed_callback = parse_edit_delete_page_callback(callback.data)
    if parsed_callback is None:
        await callback.answer("Не получилось открыть страницу.", show_alert=True)
        return

    page_index = parsed_callback
    await callback.answer()
    current_list = await _get_current_list(session_factory, callback.from_user.id)

    if isinstance(callback.message, Message):
        if current_list.is_empty:
            await callback.message.edit_text(
                format_current_list(current_list),
                reply_markup=None,
            )
            return

        await callback.message.edit_text(
            format_delete_selection(
                current_list,
                selected_count=0,
                page_index=page_index,
            ),
            reply_markup=delete_items_keyboard(
                current_list,
                (),
                page_index,
            ),
        )


@items_router.callback_query(
    lambda callback: is_legacy_delete_selection_callback(callback.data),
)
async def handle_legacy_delete_selection_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await callback.answer(DELETE_SELECTION_STALE_MESSAGE, show_alert=True)
    current_list = await _get_current_list(session_factory, callback.from_user.id)
    await _redraw_delete_selection(callback, current_list, page_index=0)


@items_router.callback_query(
    lambda callback: callback.data == CallbackPrefixEnum.CANCEL_EDIT_LIST,
)
async def handle_edit_list_cancel(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    current_list = await _get_current_list(session_factory, callback.from_user.id)

    await callback.answer("↩️ Вернулся к списку.")
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_current_list(current_list),
            reply_markup=(
                None if current_list.is_empty else current_list_actions_keyboard()
            ),
        )


def telegram_user_from_aiogram_user(user: User | None) -> TelegramUserDTO:
    if user is None:
        raise ValueError("telegram user is missing")

    return TelegramUserDTO(
        telegram_user_id=user.id,
        telegram_username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )


async def _get_current_list(
    session_factory: async_sessionmaker[AsyncSession],
    telegram_user_id: int,
) -> CurrentListDTO:
    use_case = make_get_current_list_use_case(session_factory)
    return await use_case.execute(
        GetCurrentListQuery(telegram_user_id=telegram_user_id),
    )


def _current_item_ids(current_list: CurrentListDTO) -> set[int]:
    return {
        item.item_id for category in current_list.categories for item in category.items
    }


def _selected_item_ids_from_page_mask(
    current_list: CurrentListDTO,
    page_index: int,
    selected_item_mask: int,
) -> tuple[int, ...]:
    page = get_checklist_page(current_list.categories, page_index)
    if page is None:
        return ()

    return tuple(
        item.item_id
        for index, item in enumerate(page.items)
        if selected_item_mask & (1 << index)
    )


def _delete_page_matches_fingerprint(
    current_list: CurrentListDTO,
    page_index: int,
    page_fingerprint: str,
) -> bool:
    page = get_checklist_page(current_list.categories, page_index)
    if page is None:
        return False

    current_fingerprint = build_delete_page_fingerprint(
        tuple(item.item_id for item in page.items),
    )
    return current_fingerprint == page_fingerprint


async def _show_stale_delete_selection(
    callback: CallbackQuery,
    current_list: CurrentListDTO,
    page_index: int,
) -> None:
    await callback.answer(DELETE_SELECTION_STALE_MESSAGE, show_alert=True)
    await _redraw_delete_selection(callback, current_list, page_index)


async def _redraw_delete_selection(
    callback: CallbackQuery,
    current_list: CurrentListDTO,
    page_index: int,
) -> None:
    if not isinstance(callback.message, Message):
        return

    if current_list.is_empty:
        await callback.message.edit_text(
            format_current_list(current_list),
            reply_markup=None,
        )
        return

    await callback.message.edit_text(
        format_delete_selection(
            current_list,
            selected_count=0,
            page_index=page_index,
        ),
        reply_markup=delete_items_keyboard(current_list, (), page_index),
    )


def is_command_text(text: str) -> bool:
    return text.strip().startswith("/")


def is_menu_button_text(text: str) -> bool:
    return text.strip() in MENU_BUTTON_TEXTS


def is_add_item_text(text: str) -> bool:
    stripped_text = text.strip()
    return (
        bool(stripped_text)
        and not is_command_text(text)
        and not is_menu_button_text(text)
    )
