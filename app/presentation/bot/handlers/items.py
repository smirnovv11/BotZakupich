"""Handlers for adding items and viewing the current shopping list."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.dto import (
    AddItemsCommand,
    ClearCurrentListCommand,
    GetCurrentListQuery,
    TelegramUserDTO,
)
from app.core.config import Settings
from app.core.constants import BotCommandEnum, ButtonTextEnum, CallbackPrefixEnum
from app.presentation.bot.dependencies import (
    make_add_items_use_case,
    make_clear_current_list_use_case,
    make_get_current_list_use_case,
)
from app.presentation.bot.formatters import (
    CLEAR_CANCELLED_MESSAGE,
    CLEAR_CONFIRMATION_MESSAGE,
    CLEAR_EMPTY_MESSAGE,
    format_added_items,
    format_clear_result,
    format_current_list,
)
from app.presentation.bot.keyboards.list_actions import (
    clear_list_confirmation_keyboard,
    current_list_actions_keyboard,
)
from app.presentation.bot.keyboards.main import main_menu_keyboard

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
