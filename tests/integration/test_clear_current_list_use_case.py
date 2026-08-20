from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    ClearCurrentListCommand,
    FinishShoppingCommand,
    StartShoppingCommand,
    TelegramUserDTO,
)
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.clear_current_list import ClearCurrentListUseCase
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.domain.enums import ShoppingListStatusEnum
from app.infrastructure.db.models import ShoppingItem, ShoppingList
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import func, select

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)


def make_add_items_use_case(db_session_factory) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
        parser_version="test-v1",
    )


def make_clear_current_list_use_case(db_session_factory) -> ClearCurrentListUseCase:
    return ClearCurrentListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


async def add_items(
    db_session_factory,
    raw_text: str,
    *,
    telegram_user_id: int = 7401,
    telegram_message_id: int = 9401,
):
    return await make_add_items_use_case(db_session_factory).execute(
        AddItemsCommand(
            user=TelegramUserDTO(telegram_user_id=telegram_user_id),
            telegram_chat_id=8401,
            telegram_message_id=telegram_message_id,
            raw_text=raw_text,
            received_at=RECEIVED_AT,
        ),
    )


@pytest.mark.asyncio
async def test_clear_current_list_permanently_deletes_current_list_and_items(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко, хлеб")

    result = await make_clear_current_list_use_case(db_session_factory).execute(
        ClearCurrentListCommand(telegram_user_id=7401),
    )
    list_count = await db_session.scalar(select(func.count()).select_from(ShoppingList))
    item_count = await db_session.scalar(select(func.count()).select_from(ShoppingItem))

    assert result.list_id == add_result.list_id
    assert result.deleted_item_count == 2
    assert list_count == 0
    assert item_count == 0


@pytest.mark.asyncio
async def test_clear_current_list_does_not_delete_archived_lists(
    db_session,
    db_session_factory,
) -> None:
    first_result = await add_items(db_session_factory, "молоко")
    await StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        StartShoppingCommand(
            telegram_user_id=7401,
            started_at=RECEIVED_AT,
        ),
    )
    await FinishShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        FinishShoppingCommand(
            telegram_user_id=7401,
            finished_at=RECEIVED_AT,
        ),
    )
    second_result = await add_items(
        db_session_factory,
        "хлеб",
        telegram_message_id=9402,
    )

    result = await make_clear_current_list_use_case(db_session_factory).execute(
        ClearCurrentListCommand(telegram_user_id=7401),
    )
    lists = (
        await db_session.scalars(
            select(ShoppingList).order_by(ShoppingList.id),
        )
    ).all()

    assert result.list_id == second_result.list_id
    assert [shopping_list.id for shopping_list in lists] == [first_result.list_id]
    assert lists[0].status == ShoppingListStatusEnum.ARCHIVED


@pytest.mark.asyncio
async def test_clear_current_list_returns_empty_result_when_current_list_absent(
    db_session,
    db_session_factory,
) -> None:
    result = await make_clear_current_list_use_case(db_session_factory).execute(
        ClearCurrentListCommand(telegram_user_id=740404),
    )

    assert result.list_id is None
    assert result.deleted_item_count == 0
