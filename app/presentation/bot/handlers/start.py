"""Handlers for basic bot startup commands."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.constants import BotCommandEnum
from app.presentation.bot.keyboards.main import main_menu_keyboard

START_MESSAGE = (
    "👋 Привет! Я помогу вести список покупок. "
    "Отправьте товары обычным сообщением, а я аккуратно разложу их по категориям."
)

start_router = Router(name="start")


@start_router.message(Command(BotCommandEnum.START))
async def handle_start(message: Message) -> None:
    await message.answer(
        START_MESSAGE,
        reply_markup=main_menu_keyboard(),
    )
