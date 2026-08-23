"""Handlers for finishing shopping trips and restoring archived items."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.dto import (
    FinishShoppingCommand,
    GetArchivedListQuery,
    ListArchivesQuery,
    RestoreArchivedItemsCommand,
)
from app.core.constants import BotCommandEnum, ButtonTextEnum
from app.presentation.bot.callbacks import (
    is_archived_restore_page_callback,
    is_open_archived_list_callback,
    is_restore_archived_item_callback,
    is_restore_archived_list_callback,
    parse_archived_restore_page_callback,
    parse_open_archived_list_callback,
    parse_restore_archived_item_callback,
    parse_restore_archived_list_callback,
)
from app.presentation.bot.dependencies import (
    make_finish_shopping_use_case,
    make_get_archived_list_use_case,
    make_list_archives_use_case,
    make_restore_archived_items_use_case,
)
from app.presentation.bot.formatters import (
    INVALID_ARCHIVE_ACTION_MESSAGE,
    format_archive_error,
    format_archive_list,
    format_archived_list_page,
    format_finish_shopping_result,
    format_restore_result,
)
from app.presentation.bot.handlers.items import telegram_user_from_aiogram_user
from app.presentation.bot.keyboards.archive import (
    archive_list_keyboard,
    archived_list_keyboard,
)
from app.presentation.bot.keyboards.main import main_menu_keyboard

archive_router = Router(name="archive")


@archive_router.message(lambda message: message.text == ButtonTextEnum.FINISH_SHOPPING)
async def handle_finish_shopping_button(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    use_case = make_finish_shopping_use_case(session_factory)
    user = telegram_user_from_aiogram_user(message.from_user)

    try:
        result = await use_case.execute(
            FinishShoppingCommand(
                telegram_user_id=user.telegram_user_id,
                finished_at=message.date,
            ),
        )
    except ValueError as error:
        await message.answer(
            format_archive_error(error),
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        format_finish_shopping_result(result),
        reply_markup=main_menu_keyboard(),
    )


@archive_router.message(Command(BotCommandEnum.ARCHIVE))
async def handle_archive_command(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _answer_archives(message, session_factory)


@archive_router.message(lambda message: message.text == ButtonTextEnum.ARCHIVE)
async def handle_archive_button(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _answer_archives(message, session_factory)


@archive_router.callback_query(
    lambda callback: is_open_archived_list_callback(callback.data),
)
async def handle_open_archived_list_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    archived_list_id = parse_open_archived_list_callback(callback.data)
    if archived_list_id is None:
        await callback.answer(INVALID_ARCHIVE_ACTION_MESSAGE, show_alert=True)
        return

    use_case = make_get_archived_list_use_case(session_factory)
    try:
        archived_list = await use_case.execute(
            GetArchivedListQuery(
                telegram_user_id=callback.from_user.id,
                archived_list_id=archived_list_id,
            ),
        )
    except ValueError as error:
        await callback.answer(format_archive_error(error), show_alert=True)
        return

    await callback.answer("📦 Открыл архив.")
    if isinstance(callback.message, Message):
        await callback.message.answer(
            format_archived_list_page(archived_list),
            reply_markup=archived_list_keyboard(archived_list),
        )


@archive_router.callback_query(
    lambda callback: is_archived_restore_page_callback(callback.data),
)
async def handle_archived_restore_page_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    parsed_callback = parse_archived_restore_page_callback(callback.data)
    if parsed_callback is None:
        await callback.answer(INVALID_ARCHIVE_ACTION_MESSAGE, show_alert=True)
        return

    archived_list_id, page_index = parsed_callback
    await callback.answer()
    use_case = make_get_archived_list_use_case(session_factory)
    try:
        archived_list = await use_case.execute(
            GetArchivedListQuery(
                telegram_user_id=callback.from_user.id,
                archived_list_id=archived_list_id,
            ),
        )
    except ValueError as error:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                format_archive_error(error),
                reply_markup=None,
            )
        return

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_archived_list_page(archived_list, page_index),
            reply_markup=archived_list_keyboard(archived_list, page_index),
        )


@archive_router.callback_query(
    lambda callback: is_restore_archived_list_callback(callback.data),
)
async def handle_restore_archived_list_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    archived_list_id = parse_restore_archived_list_callback(callback.data)
    if archived_list_id is None:
        await callback.answer(INVALID_ARCHIVE_ACTION_MESSAGE, show_alert=True)
        return

    await _restore_archived_items(
        callback,
        session_factory,
        archived_list_id=archived_list_id,
        item_ids=None,
    )


@archive_router.callback_query(
    lambda callback: is_restore_archived_item_callback(callback.data),
)
async def handle_restore_archived_item_callback(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    parsed_callback = parse_restore_archived_item_callback(callback.data)
    if parsed_callback is None:
        await callback.answer(INVALID_ARCHIVE_ACTION_MESSAGE, show_alert=True)
        return

    archived_list_id, item_id = parsed_callback
    await _restore_archived_items(
        callback,
        session_factory,
        archived_list_id=archived_list_id,
        item_ids=(item_id,),
    )


async def _answer_archives(
    message: Message,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    use_case = make_list_archives_use_case(session_factory)
    user = telegram_user_from_aiogram_user(message.from_user)
    archives = await use_case.execute(
        ListArchivesQuery(telegram_user_id=user.telegram_user_id),
    )

    await message.answer(
        format_archive_list(archives),
        reply_markup=(
            main_menu_keyboard()
            if not archives.archives
            else archive_list_keyboard(archives)
        ),
    )


async def _restore_archived_items(
    callback: CallbackQuery,
    session_factory: async_sessionmaker[AsyncSession],
    *,
    archived_list_id: int,
    item_ids: tuple[int, ...] | None,
) -> None:
    use_case = make_restore_archived_items_use_case(session_factory)
    try:
        result = await use_case.execute(
            RestoreArchivedItemsCommand(
                telegram_user_id=callback.from_user.id,
                archived_list_id=archived_list_id,
                item_ids=item_ids,
            ),
        )
    except ValueError as error:
        await callback.answer(format_archive_error(error), show_alert=True)
        return

    await callback.answer("♻️ Добавил.")
    if isinstance(callback.message, Message):
        await callback.message.answer(
            format_restore_result(result),
            reply_markup=main_menu_keyboard(),
        )
