from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    FinishShoppingCommand,
    StartShoppingCommand,
    TelegramUserDTO,
    ToggleItemCommand,
)
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.application.use_cases.toggle_item import ToggleItemUseCase
from app.domain.enums import ShoppingItemStatusEnum, ShoppingListStatusEnum
from app.infrastructure.db.models import ShoppingItem, ShoppingList
from app.infrastructure.db.repositories import (
    SqlAlchemyShoppingListRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import select

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
STARTED_AT = datetime(2026, 8, 20, 12, 5, tzinfo=UTC)
TOGGLED_AT = datetime(2026, 8, 20, 12, 10, tzinfo=UTC)
FINISHED_AT = datetime(2026, 8, 20, 12, 30, tzinfo=UTC)


def make_add_command(
    raw_text: str,
    *,
    telegram_user_id: int = 7201,
    telegram_chat_id: int = 8201,
    telegram_message_id: int = 9201,
) -> AddItemsCommand:
    return AddItemsCommand(
        user=TelegramUserDTO(telegram_user_id=telegram_user_id),
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
        raw_text=raw_text,
        received_at=RECEIVED_AT,
    )


def make_add_items_use_case(db_session_factory) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
        parser_version="test-v1",
    )


def make_start_shopping_use_case(db_session_factory) -> StartShoppingUseCase:
    return StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


def make_toggle_item_use_case(db_session_factory) -> ToggleItemUseCase:
    return ToggleItemUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


def make_finish_shopping_use_case(db_session_factory) -> FinishShoppingUseCase:
    return FinishShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


async def add_items(
    db_session_factory,
    raw_text: str,
    *,
    telegram_user_id: int = 7201,
    telegram_chat_id: int = 8201,
    telegram_message_id: int = 9201,
):
    return await make_add_items_use_case(db_session_factory).execute(
        make_add_command(
            raw_text,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
        ),
    )


async def start_shopping(
    db_session_factory,
    *,
    telegram_user_id: int = 7201,
):
    return await make_start_shopping_use_case(db_session_factory).execute(
        StartShoppingCommand(
            telegram_user_id=telegram_user_id,
            started_at=STARTED_AT,
        ),
    )


@pytest.mark.asyncio
async def test_start_shopping_transitions_draft_to_shopping(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко, хлеб")

    result = await start_shopping(db_session_factory)

    shopping_list = await db_session.get(ShoppingList, add_result.list_id)

    assert result.list_id == add_result.list_id
    assert result.list_status == ShoppingListStatusEnum.SHOPPING
    assert result.shopping_started_at == STARTED_AT
    assert result.item_count == 2
    assert shopping_list is not None
    assert shopping_list.status == ShoppingListStatusEnum.SHOPPING
    assert shopping_list.shopping_started_at == STARTED_AT


@pytest.mark.asyncio
async def test_start_shopping_rejects_empty_draft_and_preserves_status(
    db_session,
    db_session_factory,
) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    user = await users.create_or_update_from_telegram(telegram_user_id=7202)
    shopping_list = await lists.create_draft(owner_user_id=user.id)
    await db_session.commit()

    with pytest.raises(ValueError, match="empty list"):
        await start_shopping(db_session_factory, telegram_user_id=7202)

    await db_session.refresh(shopping_list)

    assert shopping_list.status == ShoppingListStatusEnum.DRAFT
    assert shopping_list.shopping_started_at is None


@pytest.mark.asyncio
async def test_toggle_pending_item_marks_it_bought(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко")
    item_id = add_result.added_items[0].item_id
    await start_shopping(db_session_factory)

    result = await make_toggle_item_use_case(db_session_factory).execute(
        ToggleItemCommand(
            telegram_user_id=7201,
            item_id=item_id,
            toggled_at=TOGGLED_AT,
        ),
    )

    item = await db_session.get(ShoppingItem, item_id)

    assert result.item_id == item_id
    assert result.list_id == add_result.list_id
    assert result.status == ShoppingItemStatusEnum.BOUGHT
    assert result.bought_at == TOGGLED_AT
    assert result.bought_by_user_id == add_result.user_id
    assert item is not None
    assert item.status == ShoppingItemStatusEnum.BOUGHT
    assert item.bought_at == TOGGLED_AT
    assert item.bought_by_user_id == add_result.user_id


@pytest.mark.asyncio
async def test_toggle_bought_item_marks_it_pending_and_clears_bought_fields(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко")
    item_id = add_result.added_items[0].item_id
    await start_shopping(db_session_factory)
    await make_toggle_item_use_case(db_session_factory).execute(
        ToggleItemCommand(
            telegram_user_id=7201,
            item_id=item_id,
            toggled_at=TOGGLED_AT,
        ),
    )

    result = await make_toggle_item_use_case(db_session_factory).execute(
        ToggleItemCommand(
            telegram_user_id=7201,
            item_id=item_id,
            toggled_at=FINISHED_AT,
        ),
    )

    item = await db_session.get(ShoppingItem, item_id)

    assert result.status == ShoppingItemStatusEnum.PENDING
    assert result.bought_at is None
    assert result.bought_by_user_id is None
    assert item is not None
    assert item.status == ShoppingItemStatusEnum.PENDING
    assert item.bought_at is None
    assert item.bought_by_user_id is None


@pytest.mark.asyncio
async def test_toggle_rejects_item_outside_user_current_shopping_list(
    db_session,
    db_session_factory,
) -> None:
    owner_result = await add_items(
        db_session_factory,
        "молоко",
        telegram_user_id=7203,
        telegram_chat_id=8203,
        telegram_message_id=9203,
    )
    await start_shopping(db_session_factory, telegram_user_id=7203)
    foreign_result = await add_items(
        db_session_factory,
        "хлеб",
        telegram_user_id=7204,
        telegram_chat_id=8204,
        telegram_message_id=9204,
    )
    await start_shopping(db_session_factory, telegram_user_id=7204)

    with pytest.raises(ValueError, match="does not belong to active list"):
        await make_toggle_item_use_case(db_session_factory).execute(
            ToggleItemCommand(
                telegram_user_id=7203,
                item_id=foreign_result.added_items[0].item_id,
                toggled_at=TOGGLED_AT,
            ),
        )

    owner_item = await db_session.get(ShoppingItem, owner_result.added_items[0].item_id)
    foreign_item = await db_session.get(
        ShoppingItem,
        foreign_result.added_items[0].item_id,
    )

    assert owner_item is not None
    assert owner_item.status == ShoppingItemStatusEnum.PENDING
    assert foreign_item is not None
    assert foreign_item.status == ShoppingItemStatusEnum.PENDING


@pytest.mark.asyncio
async def test_finish_shopping_archives_active_list(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(db_session_factory, "молоко")
    await start_shopping(db_session_factory)

    result = await make_finish_shopping_use_case(db_session_factory).execute(
        FinishShoppingCommand(
            telegram_user_id=7201,
            finished_at=FINISHED_AT,
        ),
    )

    shopping_list = await db_session.get(ShoppingList, add_result.list_id)

    assert result.list_id == add_result.list_id
    assert result.list_status == ShoppingListStatusEnum.ARCHIVED
    assert result.archived_at == FINISHED_AT
    assert result.archived_by_user_id == add_result.user_id
    assert shopping_list is not None
    assert shopping_list.status == ShoppingListStatusEnum.ARCHIVED
    assert shopping_list.archived_at == FINISHED_AT
    assert shopping_list.archived_by_user_id == add_result.user_id


@pytest.mark.asyncio
async def test_after_finish_new_message_creates_new_draft(
    db_session,
    db_session_factory,
) -> None:
    first_result = await add_items(db_session_factory, "молоко")
    await start_shopping(db_session_factory)
    await make_finish_shopping_use_case(db_session_factory).execute(
        FinishShoppingCommand(
            telegram_user_id=7201,
            finished_at=FINISHED_AT,
        ),
    )

    second_result = await add_items(
        db_session_factory,
        "хлеб",
        telegram_chat_id=8202,
        telegram_message_id=9202,
    )
    lists = (
        await db_session.scalars(
            select(ShoppingList).order_by(ShoppingList.id),
        )
    ).all()

    assert second_result.list_id != first_result.list_id
    assert second_result.list_status == ShoppingListStatusEnum.DRAFT
    assert [shopping_list.status for shopping_list in lists] == [
        ShoppingListStatusEnum.ARCHIVED,
        ShoppingListStatusEnum.DRAFT,
    ]
