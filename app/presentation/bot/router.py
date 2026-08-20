"""Root aiogram router for the Telegram bot."""

from aiogram import Router

from app.presentation.bot.handlers.archive import archive_router
from app.presentation.bot.handlers.items import items_router
from app.presentation.bot.handlers.shopping import shopping_router
from app.presentation.bot.handlers.start import start_router

bot_router = Router(name="bot")
bot_router.include_router(start_router)
bot_router.include_router(shopping_router)
bot_router.include_router(archive_router)
bot_router.include_router(items_router)
