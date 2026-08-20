"""Async SQLAlchemy engine and session helpers."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


@dataclass(frozen=True)
class Database:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


def create_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    return create_async_engine(database_url, echo=echo)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


def create_database(settings: Settings, *, echo: bool = False) -> Database:
    database_url = settings.database_url.get_secret_value()
    engine = create_engine(database_url, echo=echo)
    session_factory = create_session_factory(engine)
    return Database(engine=engine, session_factory=session_factory)
