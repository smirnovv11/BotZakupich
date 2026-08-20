"""Handlers for starting and interacting with a shopping checklist."""

from datetime import UTC, datetime

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.dto import (
    CurrentListDTO,
    GetCurrentListQuery,
    StartShoppingCommand,
    ToggleItemCommand,
)
from app.core.constants import ButtonTextEnum
from app.presentation.bot.callbacks import (
    is_toggle_item_callback,
    parse_toggle_item_callback,
)
from app.presentation.bot.dependencies import (
    make_get_current_list_use_case,
    make_start_shopping_use_case,
    make_toggle_item_use_case,
)
from app.presentation.bot.formatters import (
    INVALID_CHECKLIST_ACTION_MESSAGE,
    format_checklist,
    format_shopping_error,
    format_shopping_started,
)
from app.presentation.bot.handlers.items import telegram_user_from_aiogram_user
from app.presentation.bot.keyboards.checklist import checklist_keyboard
from app.presentation.bot.keyboards.main import main_menu_keyboard

shopping_router = Router(name="shopping")


@shopping_router.message(lambda message: message.text == ButtonTextEnum.START_SHOPPING)
async def handle_start_shopping_button(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    start_use_case = make_start_shopping_use_case(session_factory)
    user = telegram_user_from_aiogram_user(message.from_user)

    try:
        result = await start_use_case.execute(
            StartShoppingCommand(
                telegram_user_id=user.telegram_user_id,
                started_at=message.date,
            ),
        )
    except ValueError as error:
        await message.answer(
            format_shopping_error(error),
            reply_markup=main_menu_keyboard(),
        )
        return

    current_list = await _get_current_list(session_factory, user.telegram_user_id)
    await message.answer(
        format_shopping_started(result),
        reply_markup=main_menu_keyboard(),
    )
    await message.answer(
        format_checklist(current_list),
        reply_markup=checklist_keyboard(current_list),
    )


@shopping_router.callback_query(
    lambda callback: is_toggle_item_callback(callback.data),
)
async def handle_toggle_item_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    item_id = parse_toggle_item_callback(callback.data)
    if item_id is None:
        await callback.answer(INVALID_CHECKLIST_ACTION_MESSAGE, show_alert=True)
        return

    toggle_use_case = make_toggle_item_use_case(session_factory)
    try:
        await toggle_use_case.execute(
            ToggleItemCommand(
                telegram_user_id=callback.from_user.id,
                item_id=item_id,
                toggled_at=_callback_datetime(callback),
            ),
        )
    except ValueError as error:
        await callback.answer(format_shopping_error(error), show_alert=True)
        return

    current_list = await _get_current_list(session_factory, callback.from_user.id)
    await callback.answer("✅ Обновил.")
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_checklist(current_list),
            reply_markup=checklist_keyboard(current_list),
        )


async def _get_current_list(
    session_factory: async_sessionmaker[AsyncSession],
    telegram_user_id: int,
) -> CurrentListDTO:
    get_current_list_use_case = make_get_current_list_use_case(session_factory)
    return await get_current_list_use_case.execute(
        GetCurrentListQuery(telegram_user_id=telegram_user_id),
    )


def _callback_datetime(callback: CallbackQuery) -> datetime:
    if isinstance(callback.message, Message):
        return callback.message.date

    return datetime.now(UTC)
