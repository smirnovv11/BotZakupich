"""Presentation-layer factories for application use cases."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.archive import (
    GetArchivedListUseCase,
    ListArchivesUseCase,
    RestoreArchivedItemsUseCase,
)
from app.application.use_cases.clear_current_list import ClearCurrentListUseCase
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.get_current_list import GetCurrentListUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.application.use_cases.toggle_item import ToggleItemUseCase
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


def make_clear_current_list_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> ClearCurrentListUseCase:
    return ClearCurrentListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_start_shopping_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> StartShoppingUseCase:
    return StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_toggle_item_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> ToggleItemUseCase:
    return ToggleItemUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_finish_shopping_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> FinishShoppingUseCase:
    return FinishShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_list_archives_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> ListArchivesUseCase:
    return ListArchivesUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_get_archived_list_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> GetArchivedListUseCase:
    return GetArchivedListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )


def make_restore_archived_items_use_case(
    session_factory: async_sessionmaker[AsyncSession],
) -> RestoreArchivedItemsUseCase:
    return RestoreArchivedItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
    )
