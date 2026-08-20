import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from app.infrastructure.db.models import (
    Category,
    InputMessage,
    ShoppingItem,
    ShoppingList,
    User,
)
from app.infrastructure.db.seeds import seed_categories
from app.infrastructure.db.session import create_engine, create_session_factory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

DATABASE_URL = (
    "postgresql+asyncpg://shopping_user:shopping_password@localhost:5432/shopping_bot"
)
TELEGRAM_TOKEN = "123456:test-token"


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    os.environ.setdefault("DATABASE_URL", DATABASE_URL)
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", TELEGRAM_TOKEN)

    config = Config("alembic.ini")
    command.upgrade(config, "head")


@pytest_asyncio.fixture
async def db_session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine(DATABASE_URL)
    session_factory = create_session_factory(engine)

    yield session_factory

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with db_session_factory() as session:
        await session.rollback()
        await clean_database(session)
        await seed_categories(session)
        await session.commit()

        yield session

        await session.rollback()
        await clean_database(session)
        await session.commit()


async def clean_database(session: AsyncSession) -> None:
    for model in (
        ShoppingItem,
        InputMessage,
        ShoppingList,
        Category,
        User,
    ):
        await session.execute(delete(model))
