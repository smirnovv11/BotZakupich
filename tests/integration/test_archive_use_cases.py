from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    FinishShoppingCommand,
    GetArchivedListQuery,
    ListArchivesQuery,
    RestoreArchivedItemsCommand,
    StartShoppingCommand,
    TelegramUserDTO,
    ToggleItemCommand,
)
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.archive import (
    GetArchivedListUseCase,
    ListArchivesUseCase,
    RestoreArchivedItemsUseCase,
)
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.application.use_cases.toggle_item import ToggleItemUseCase
from app.domain.enums import (
    CategoryCodeEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.models import Category, ShoppingItem
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import select

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
STARTED_AT = datetime(2026, 8, 20, 12, 5, tzinfo=UTC)
TOGGLED_AT = datetime(2026, 8, 20, 12, 10, tzinfo=UTC)


def make_add_items_use_case(db_session_factory) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
        parser_version="test-v1",
    )


def make_list_archives_use_case(db_session_factory) -> ListArchivesUseCase:
    return ListArchivesUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


def make_get_archived_list_use_case(db_session_factory) -> GetArchivedListUseCase:
    return GetArchivedListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


def make_restore_archived_items_use_case(
    db_session_factory,
) -> RestoreArchivedItemsUseCase:
    return RestoreArchivedItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


def make_add_command(
    raw_text: str,
    *,
    telegram_user_id: int,
    telegram_chat_id: int,
    telegram_message_id: int,
) -> AddItemsCommand:
    return AddItemsCommand(
        user=TelegramUserDTO(telegram_user_id=telegram_user_id),
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
        raw_text=raw_text,
        received_at=RECEIVED_AT,
    )


async def add_items(
    db_session_factory,
    raw_text: str,
    *,
    telegram_user_id: int = 7301,
    telegram_chat_id: int = 8301,
    telegram_message_id: int = 9301,
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
    telegram_user_id: int = 7301,
):
    return await StartShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        StartShoppingCommand(
            telegram_user_id=telegram_user_id,
            started_at=STARTED_AT,
        ),
    )


async def finish_shopping(
    db_session_factory,
    *,
    telegram_user_id: int = 7301,
    finished_at: datetime,
):
    return await FinishShoppingUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        FinishShoppingCommand(
            telegram_user_id=telegram_user_id,
            finished_at=finished_at,
        ),
    )


async def toggle_item(
    db_session_factory,
    *,
    telegram_user_id: int = 7301,
    item_id: int,
):
    return await ToggleItemUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    ).execute(
        ToggleItemCommand(
            telegram_user_id=telegram_user_id,
            item_id=item_id,
            toggled_at=TOGGLED_AT,
        ),
    )


async def create_archive(
    db_session_factory,
    *,
    raw_text: str,
    telegram_user_id: int = 7301,
    telegram_chat_id: int = 8301,
    telegram_message_id: int = 9301,
    finished_at: datetime,
):
    add_result = await add_items(
        db_session_factory,
        raw_text,
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
    )
    await start_shopping(db_session_factory, telegram_user_id=telegram_user_id)
    finish_result = await finish_shopping(
        db_session_factory,
        telegram_user_id=telegram_user_id,
        finished_at=finished_at,
    )
    return add_result, finish_result


def flatten_items(categories):
    return [item for category in categories for item in category.items]


@pytest.mark.asyncio
async def test_list_archives_returns_only_user_archives_sorted_by_archived_at_desc(
    db_session,
    db_session_factory,
) -> None:
    older_finished_at = datetime(2026, 8, 20, 13, 0, tzinfo=UTC)
    newer_finished_at = datetime(2026, 8, 20, 14, 0, tzinfo=UTC)
    older_archive = await create_archive(
        db_session_factory,
        raw_text="молоко",
        telegram_message_id=9301,
        finished_at=older_finished_at,
    )
    newer_archive = await create_archive(
        db_session_factory,
        raw_text="хлеб, яйца",
        telegram_message_id=9302,
        finished_at=newer_finished_at,
    )
    await create_archive(
        db_session_factory,
        raw_text="сыр",
        telegram_user_id=7302,
        telegram_chat_id=8302,
        telegram_message_id=9303,
        finished_at=datetime(2026, 8, 20, 15, 0, tzinfo=UTC),
    )

    result = await make_list_archives_use_case(db_session_factory).execute(
        ListArchivesQuery(telegram_user_id=7301),
    )

    assert [archive.list_id for archive in result.archives] == [
        newer_archive[1].list_id,
        older_archive[1].list_id,
    ]
    assert [archive.archived_at for archive in result.archives] == [
        newer_finished_at,
        older_finished_at,
    ]
    assert [archive.item_count for archive in result.archives] == [2, 1]
    assert all(
        archive.list_status == ShoppingListStatusEnum.ARCHIVED
        for archive in result.archives
    )


@pytest.mark.asyncio
async def test_get_archived_list_returns_final_item_statuses(
    db_session,
    db_session_factory,
) -> None:
    add_result = await add_items(
        db_session_factory,
        "молоко, хлеб",
    )
    await start_shopping(db_session_factory)
    await toggle_item(
        db_session_factory,
        item_id=add_result.added_items[0].item_id,
    )
    finish_result = await finish_shopping(
        db_session_factory,
        finished_at=datetime(2026, 8, 20, 13, 30, tzinfo=UTC),
    )

    result = await make_get_archived_list_use_case(db_session_factory).execute(
        GetArchivedListQuery(
            telegram_user_id=7301,
            archived_list_id=finish_result.list_id,
        ),
    )
    items = flatten_items(result.categories)

    assert result.list_status == ShoppingListStatusEnum.ARCHIVED
    assert [(item.display_text, item.status) for item in items] == [
        ("молоко", ShoppingItemStatusEnum.BOUGHT),
        ("хлеб", ShoppingItemStatusEnum.PENDING),
    ]


@pytest.mark.asyncio
async def test_restore_all_creates_new_draft_and_keeps_archived_items_unchanged(
    db_session,
    db_session_factory,
) -> None:
    add_result, finish_result = await create_archive(
        db_session_factory,
        raw_text="2 литра молока, хлеб",
        finished_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
    )
    source_item_id = add_result.added_items[0].item_id

    result = await make_restore_archived_items_use_case(db_session_factory).execute(
        RestoreArchivedItemsCommand(
            telegram_user_id=7301,
            archived_list_id=finish_result.list_id,
        ),
    )
    restored_items = (
        await db_session.scalars(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == result.list_id)
            .order_by(ShoppingItem.position),
        )
    ).all()
    source_item = await db_session.get(ShoppingItem, source_item_id)
    expected_quantity_amount = add_result.added_items[0].quantity_amount

    assert result.list_id != finish_result.list_id
    assert result.list_status == ShoppingListStatusEnum.DRAFT
    assert [item.restored_from_item_id for item in restored_items] == [
        item.item_id for item in add_result.added_items
    ]
    assert [item.status for item in restored_items] == [
        ShoppingItemStatusEnum.PENDING,
        ShoppingItemStatusEnum.PENDING,
    ]
    assert [item.position for item in restored_items] == [1, 2]
    assert restored_items[0].display_text == "2 литра молока"
    assert restored_items[0].product_key == "молоко"
    assert restored_items[0].quantity_amount == expected_quantity_amount
    assert restored_items[0].quantity_unit == "литра"
    assert source_item is not None
    assert source_item.list_id == finish_result.list_id
    assert source_item.restored_from_item_id is None


@pytest.mark.asyncio
async def test_restore_selected_appends_to_existing_shopping_list(
    db_session,
    db_session_factory,
) -> None:
    archived_add_result, finish_result = await create_archive(
        db_session_factory,
        raw_text="молоко, хлеб, яйца",
        finished_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
    )
    current_add_result = await add_items(
        db_session_factory,
        "сыр",
        telegram_message_id=9302,
    )
    await start_shopping(db_session_factory)
    selected_item_ids = (
        archived_add_result.added_items[1].item_id,
        archived_add_result.added_items[2].item_id,
    )

    result = await make_restore_archived_items_use_case(db_session_factory).execute(
        RestoreArchivedItemsCommand(
            telegram_user_id=7301,
            archived_list_id=finish_result.list_id,
            item_ids=selected_item_ids,
        ),
    )
    current_items = (
        await db_session.scalars(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == current_add_result.list_id)
            .order_by(ShoppingItem.position),
        )
    ).all()

    assert result.list_id == current_add_result.list_id
    assert result.list_status == ShoppingListStatusEnum.SHOPPING
    assert [item.display_text for item in current_items] == ["сыр", "хлеб", "яйца"]
    assert [item.position for item in current_items] == [1, 2, 3]
    assert [item.restored_from_item_id for item in current_items] == [
        None,
        selected_item_ids[0],
        selected_item_ids[1],
    ]


@pytest.mark.asyncio
async def test_restore_preserves_category_from_archived_item(
    db_session,
    db_session_factory,
) -> None:
    add_result, finish_result = await create_archive(
        db_session_factory,
        raw_text="молоко",
        finished_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
    )

    result = await make_restore_archived_items_use_case(db_session_factory).execute(
        RestoreArchivedItemsCommand(
            telegram_user_id=7301,
            archived_list_id=finish_result.list_id,
            item_ids=(add_result.added_items[0].item_id,),
        ),
    )
    category_code = await db_session.scalar(
        select(Category.code)
        .join(ShoppingItem, ShoppingItem.category_id == Category.id)
        .where(ShoppingItem.list_id == result.list_id),
    )

    assert category_code == CategoryCodeEnum.DAIRY


@pytest.mark.asyncio
async def test_restore_rejects_foreign_archive_and_foreign_selected_item(
    db_session,
    db_session_factory,
) -> None:
    owner_add_result, owner_finish_result = await create_archive(
        db_session_factory,
        raw_text="молоко",
        telegram_user_id=7303,
        telegram_chat_id=8303,
        telegram_message_id=9303,
        finished_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC),
    )
    foreign_add_result, foreign_finish_result = await create_archive(
        db_session_factory,
        raw_text="хлеб",
        telegram_user_id=7304,
        telegram_chat_id=8304,
        telegram_message_id=9304,
        finished_at=datetime(2026, 8, 20, 14, 0, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="archived shopping list was not found"):
        await make_restore_archived_items_use_case(db_session_factory).execute(
            RestoreArchivedItemsCommand(
                telegram_user_id=7303,
                archived_list_id=foreign_finish_result.list_id,
            ),
        )

    with pytest.raises(ValueError, match="does not belong to archived list"):
        await make_restore_archived_items_use_case(db_session_factory).execute(
            RestoreArchivedItemsCommand(
                telegram_user_id=7303,
                archived_list_id=owner_finish_result.list_id,
                item_ids=(foreign_add_result.added_items[0].item_id,),
            ),
        )

    owner_source_item = await db_session.get(
        ShoppingItem,
        owner_add_result.added_items[0].item_id,
    )

    assert owner_source_item is not None
    assert owner_source_item.restored_from_item_id is None
