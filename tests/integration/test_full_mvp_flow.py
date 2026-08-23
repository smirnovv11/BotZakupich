from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    FinishShoppingCommand,
    GetArchivedListQuery,
    GetCurrentListQuery,
    ListArchivesQuery,
    ListCategoryDTO,
    ListItemDTO,
    RestoreArchivedItemsCommand,
    StartShoppingCommand,
    TelegramUserDTO,
    ToggleItemCommand,
)
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.archive import (
    GetArchivedListUseCase,
    ListArchivesUseCase,
    RestoreArchivedItemsUseCase,
)
from app.application.use_cases.finish_shopping import FinishShoppingUseCase
from app.application.use_cases.get_current_list import GetCurrentListUseCase
from app.application.use_cases.start_shopping import StartShoppingUseCase
from app.application.use_cases.toggle_item import ToggleItemUseCase
from app.domain.enums import (
    CategoryCodeEnum,
    ParserSourceEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.models import InputMessage, ShoppingItem
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

TELEGRAM_USER_ID = 7501
TELEGRAM_CHAT_ID = 8501
FIRST_MESSAGE_ID = 9501
SECOND_MESSAGE_ID = 9502
RECEIVED_AT = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
STARTED_AT = datetime(2026, 8, 22, 12, 5, tzinfo=UTC)
TOGGLED_AT = datetime(2026, 8, 22, 12, 10, tzinfo=UTC)
FINISHED_AT = datetime(2026, 8, 22, 12, 30, tzinfo=UTC)


def make_unit_of_work_factory(db_session_factory) -> Callable[[], UnitOfWork]:
    return lambda: SqlAlchemyUnitOfWork(db_session_factory)


def make_add_command(
    raw_text: str,
    *,
    telegram_message_id: int,
    received_at: datetime = RECEIVED_AT,
) -> AddItemsCommand:
    return AddItemsCommand(
        user=TelegramUserDTO(telegram_user_id=TELEGRAM_USER_ID),
        telegram_chat_id=TELEGRAM_CHAT_ID,
        telegram_message_id=telegram_message_id,
        raw_text=raw_text,
        received_at=received_at,
    )


def flatten_items(categories: tuple[ListCategoryDTO, ...]) -> tuple[ListItemDTO, ...]:
    return tuple(item for category in categories for item in category.items)


def items_by_display_text(
    categories: tuple[ListCategoryDTO, ...],
) -> dict[str, ListItemDTO]:
    return {item.display_text: item for item in flatten_items(categories)}


@pytest.mark.asyncio
async def test_complete_shopping_archive_and_selected_restore_flow(
    db_session,
    db_session_factory,
) -> None:
    unit_of_work_factory = make_unit_of_work_factory(db_session_factory)
    add_items = AddItemsUseCase(unit_of_work_factory, parser_version="smoke-v1")
    get_current_list = GetCurrentListUseCase(unit_of_work_factory)
    start_shopping = StartShoppingUseCase(unit_of_work_factory)
    toggle_item = ToggleItemUseCase(unit_of_work_factory)
    finish_shopping = FinishShoppingUseCase(unit_of_work_factory)
    list_archives = ListArchivesUseCase(unit_of_work_factory)
    get_archived_list = GetArchivedListUseCase(unit_of_work_factory)
    restore_archived_items = RestoreArchivedItemsUseCase(unit_of_work_factory)

    initial_result = await add_items.execute(
        make_add_command(
            "молоко, хлеб, яйца",
            telegram_message_id=FIRST_MESSAGE_ID,
        ),
    )
    initial_list_id = initial_result.list_id

    assert initial_list_id is not None
    assert initial_result.list_status == ShoppingListStatusEnum.DRAFT
    assert [item.display_text for item in initial_result.added_items] == [
        "молоко",
        "хлеб",
        "яйца",
    ]

    draft = await get_current_list.execute(
        GetCurrentListQuery(telegram_user_id=TELEGRAM_USER_ID),
    )

    assert draft.list_id == initial_list_id
    assert draft.list_status == ShoppingListStatusEnum.DRAFT
    assert set(items_by_display_text(draft.categories)) == {"молоко", "хлеб", "яйца"}

    start_result = await start_shopping.execute(
        StartShoppingCommand(
            telegram_user_id=TELEGRAM_USER_ID,
            started_at=STARTED_AT,
        ),
    )
    bread_item_id = initial_result.added_items[1].item_id
    toggle_result = await toggle_item.execute(
        ToggleItemCommand(
            telegram_user_id=TELEGRAM_USER_ID,
            item_id=bread_item_id,
            toggled_at=TOGGLED_AT,
        ),
    )

    assert start_result.list_id == initial_list_id
    assert start_result.list_status == ShoppingListStatusEnum.SHOPPING
    assert toggle_result.status == ShoppingItemStatusEnum.BOUGHT

    cheese_result = await add_items.execute(
        make_add_command(
            "сыр",
            telegram_message_id=SECOND_MESSAGE_ID,
            received_at=TOGGLED_AT,
        ),
    )
    shopping = await get_current_list.execute(
        GetCurrentListQuery(telegram_user_id=TELEGRAM_USER_ID),
    )
    shopping_items = items_by_display_text(shopping.categories)

    assert cheese_result.list_id == initial_list_id
    assert cheese_result.list_status == ShoppingListStatusEnum.SHOPPING
    assert shopping.list_id == initial_list_id
    assert shopping.list_status == ShoppingListStatusEnum.SHOPPING
    assert set(shopping_items) == {"молоко", "хлеб", "яйца", "сыр"}
    assert shopping_items["хлеб"].status == ShoppingItemStatusEnum.BOUGHT
    assert shopping_items["сыр"].status == ShoppingItemStatusEnum.PENDING

    finish_result = await finish_shopping.execute(
        FinishShoppingCommand(
            telegram_user_id=TELEGRAM_USER_ID,
            finished_at=FINISHED_AT,
        ),
    )
    empty_current = await get_current_list.execute(
        GetCurrentListQuery(telegram_user_id=TELEGRAM_USER_ID),
    )
    archives = await list_archives.execute(
        ListArchivesQuery(telegram_user_id=TELEGRAM_USER_ID),
    )
    archived = await get_archived_list.execute(
        GetArchivedListQuery(
            telegram_user_id=TELEGRAM_USER_ID,
            archived_list_id=finish_result.list_id,
        ),
    )
    archived_items_before_restore = items_by_display_text(archived.categories)

    assert finish_result.list_id == initial_list_id
    assert finish_result.list_status == ShoppingListStatusEnum.ARCHIVED
    assert empty_current.is_empty
    assert empty_current.list_id is None
    assert len(archives.archives) == 1
    assert archives.archives[0].list_id == initial_list_id
    assert archives.archives[0].item_count == 4
    assert archived.list_status == ShoppingListStatusEnum.ARCHIVED
    assert set(archived_items_before_restore) == {"молоко", "хлеб", "яйца", "сыр"}
    assert archived_items_before_restore["хлеб"].status == ShoppingItemStatusEnum.BOUGHT

    eggs_source_item_id = archived_items_before_restore["яйца"].item_id
    restore_result = await restore_archived_items.execute(
        RestoreArchivedItemsCommand(
            telegram_user_id=TELEGRAM_USER_ID,
            archived_list_id=initial_list_id,
            item_ids=(eggs_source_item_id,),
        ),
    )
    restored_current = await get_current_list.execute(
        GetCurrentListQuery(telegram_user_id=TELEGRAM_USER_ID),
    )
    archived_after_restore = await get_archived_list.execute(
        GetArchivedListQuery(
            telegram_user_id=TELEGRAM_USER_ID,
            archived_list_id=initial_list_id,
        ),
    )
    restored_items = flatten_items(restored_current.categories)
    archived_items_after_restore = items_by_display_text(
        archived_after_restore.categories,
    )
    restored_item = await db_session.get(
        ShoppingItem,
        restore_result.restored_items[0].item_id,
    )
    source_item = await db_session.get(ShoppingItem, eggs_source_item_id)

    assert restore_result.list_id != initial_list_id
    assert restore_result.list_status == ShoppingListStatusEnum.DRAFT
    assert len(restore_result.restored_items) == 1
    assert restore_result.restored_items[0].restored_from_item_id == eggs_source_item_id
    assert restored_current.list_id == restore_result.list_id
    assert restored_current.list_status == ShoppingListStatusEnum.DRAFT
    assert len(restored_items) == 1
    assert restored_items[0].display_text == "яйца"
    assert restored_items[0].status == ShoppingItemStatusEnum.PENDING
    assert restored_item is not None
    assert restored_item.restored_from_item_id == eggs_source_item_id
    assert source_item is not None
    assert source_item.list_id == initial_list_id
    assert source_item.restored_from_item_id is None
    assert {
        display_text: item.status
        for display_text, item in archived_items_after_restore.items()
    } == {
        display_text: item.status
        for display_text, item in archived_items_before_restore.items()
    }


@pytest.mark.asyncio
async def test_unknown_item_uses_local_fallback_without_openai_key(
    db_session,
    db_session_factory,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    unit_of_work_factory = make_unit_of_work_factory(db_session_factory)
    add_items = AddItemsUseCase(unit_of_work_factory, parser_version="smoke-v1")
    get_current_list = GetCurrentListUseCase(unit_of_work_factory)
    unknown_text = "кварцевый стабилизатор телепорта"

    result = await add_items.execute(
        make_add_command(
            unknown_text,
            telegram_message_id=FIRST_MESSAGE_ID,
        ),
    )
    current = await get_current_list.execute(
        GetCurrentListQuery(telegram_user_id=TELEGRAM_USER_ID),
    )
    saved_input = await db_session.get(InputMessage, result.input_message_id)

    assert len(result.added_items) == 1
    assert result.added_items[0].display_text == unknown_text
    assert result.added_items[0].category_code == CategoryCodeEnum.OTHER
    assert result.added_items[0].category_name_ru == "Прочие"
    assert result.added_items[0].is_category_fallback is True
    assert [item.display_text for item in flatten_items(current.categories)] == [
        unknown_text,
    ]
    assert saved_input is not None
    assert saved_input.parser_source == ParserSourceEnum.LOCAL
