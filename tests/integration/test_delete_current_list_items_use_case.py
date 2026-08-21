from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    DeleteCurrentListItemsCommand,
    FinishShoppingCommand,
    StartShoppingCommand,
    TelegramUserDTO,
)
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.delete_current_list_items import (
    DeleteCurrentListItemsUseCase,
)
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.domain.enums import ShoppingListStatusEnum
from app.infrastructure.db.models import ShoppingItem, ShoppingList
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import select

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)


def make_add_items_use_case(db_session_factory) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
        parser_version="test-v1",
    )


def make_delete_items_use_case(db_session_factory) -> DeleteCurrentListItemsUseCase:
    return DeleteCurrentListItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


async def add_items(
    db_session_factory,
    raw_text: str,
    *,
    telegram_user_id: int = 7601,
    telegram_message_id: int = 9601,
):
    return await make_add_items_use_case(db_session_factory).execute(
        AddItemsCommand(
            user=TelegramUserDTO(telegram_user_id=telegram_user_id),
            telegram_chat_id=8601,
            telegram_message_id=telegram_message_id,
            raw_text=raw_text,
            received_at=RECEIVED_AT,
        ),
    )


@pytest.mark.asyncio
async def test_delete_selected_items_removes_only_chosen_current_items(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко, хлеб, яйца")
    bread_id = next(
        item.item_id for item in add_result.added_items if item.display_text == "хлеб"
    )

    result = await make_delete_items_use_case(db_session_factory).execute(
        DeleteCurrentListItemsCommand(
            telegram_user_id=7601,
            item_ids=(bread_id,),
        ),
    )
    remaining_items = (
        await db_session.scalars(
            select(ShoppingItem).order_by(ShoppingItem.position),
        )
    ).all()

    assert result.list_id == add_result.list_id
    assert result.deleted_item_count == 1
    assert [item.display_text for item in remaining_items] == ["молоко", "яйца"]


@pytest.mark.asyncio
async def test_delete_selected_items_preserves_shopping_list_status(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко, хлеб")
    milk_id = add_result.added_items[0].item_id
    await StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        StartShoppingCommand(
            telegram_user_id=7601,
            started_at=RECEIVED_AT,
        ),
    )

    result = await make_delete_items_use_case(db_session_factory).execute(
        DeleteCurrentListItemsCommand(
            telegram_user_id=7601,
            item_ids=(milk_id,),
        ),
    )
    shopping_list = await db_session.get(ShoppingList, add_result.list_id)

    assert result.deleted_item_count == 1
    assert shopping_list is not None
    assert shopping_list.status == ShoppingListStatusEnum.SHOPPING


@pytest.mark.asyncio
async def test_delete_selected_items_does_not_delete_archived_items(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко")
    archived_item_id = add_result.added_items[0].item_id
    await StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        StartShoppingCommand(
            telegram_user_id=7601,
            started_at=RECEIVED_AT,
        ),
    )
    await FinishShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        FinishShoppingCommand(
            telegram_user_id=7601,
            finished_at=RECEIVED_AT,
        ),
    )
    current_result = await add_items(
        db_session_factory,
        "хлеб",
        telegram_message_id=9602,
    )

    result = await make_delete_items_use_case(db_session_factory).execute(
        DeleteCurrentListItemsCommand(
            telegram_user_id=7601,
            item_ids=(archived_item_id,),
        ),
    )
    archived_item = await db_session.get(ShoppingItem, archived_item_id)

    assert result.list_id == current_result.list_id
    assert result.deleted_item_count == 0
    assert archived_item is not None


@pytest.mark.asyncio
async def test_delete_selected_items_ignores_empty_selection(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко")

    result = await make_delete_items_use_case(db_session_factory).execute(
        DeleteCurrentListItemsCommand(
            telegram_user_id=7601,
            item_ids=(),
        ),
    )

    assert result.list_id == add_result.list_id
    assert result.deleted_item_count == 0
