"""Presentation-layer factories for application use cases."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.get_current_list import GetCurrentListUseCase
from app.core.config import Settings
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def make_add_items_use_case(
    session_factory: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
        parser_version=settings.parser_version,
    )


def make_get_current_list_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> GetCurrentListUseCase:
    return GetCurrentListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )
