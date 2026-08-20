"""Application entry point for Telegram polling."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.core.config import Settings
from app.core.logging import configure_logging
from app.infrastructure.db.seeds import seed_categories
from app.infrastructure.db.session import create_database
from app.presentation.bot.router import bot_router

logger = logging.getLogger(__name__)


async def run_polling() -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    database = create_database(settings)
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    dispatcher = Dispatcher()
    dispatcher.include_router(bot_router)

    try:
        async with database.session_factory() as session:
            await seed_categories(session)
            await session.commit()

        logger.info("Starting Telegram bot polling")
        await dispatcher.start_polling(
            bot,
            session_factory=database.session_factory,
            settings=settings,
        )
    finally:
        await bot.session.close()
        await database.engine.dispose()


def main() -> None:
    asyncio.run(run_polling())


if __name__ == "__main__":
    main()
