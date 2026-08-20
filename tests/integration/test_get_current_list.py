from datetime import UTC, datetime

import pytest
from app.application.dto import (
    AddItemsCommand,
    GetCurrentListQuery,
    TelegramUserDTO,
)
from app.application.use_cases.add_items import AddItemsUseCase
from app.application.use_cases.get_current_list import GetCurrentListUseCase
from app.domain.enums import (
    CategoryCodeEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyShoppingItemRepository,
    SqlAlchemyShoppingListRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)


def make_add_command(
    raw_text: str,
    *,
    telegram_user_id: int = 7101,
    telegram_chat_id: int = 8101,
    telegram_message_id: int = 9101,
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


def make_get_current_list_use_case(db_session_factory) -> GetCurrentListUseCase:
    return GetCurrentListUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
    )


@pytest.mark.asyncio
async def test_unknown_telegram_user_returns_empty_current_list(
    db_session,
    db_session_factory,
) -> None:
    result = await make_get_current_list_use_case(db_session_factory).execute(
        GetCurrentListQuery(telegram_user_id=710404),
    )

    assert result.list_id is None
    assert result.list_status is None
    assert result.title is None
    assert result.categories == ()
    assert result.is_empty is True


@pytest.mark.asyncio
async def test_user_without_current_list_returns_empty_current_list(
    db_session,
    db_session_factory,
) -> None:
    users = SqlAlchemyUserRepository(db_session)
    await users.create_or_update_from_telegram(telegram_user_id=7102)
    await db_session.commit()

    result = await make_get_current_list_use_case(db_session_factory).execute(
        GetCurrentListQuery(telegram_user_id=7102),
    )

    assert result.list_id is None
    assert result.list_status is None
    assert result.categories == ()
    assert result.is_empty is True


@pytest.mark.asyncio
async def test_current_draft_list_is_grouped_by_category(
    db_session,
    db_session_factory,
) -> None:
    add_result = await make_add_items_use_case(db_session_factory).execute(
        make_add_command("молоко, хлеб, яйца"),
    )

    result = await make_get_current_list_use_case(db_session_factory).execute(
        GetCurrentListQuery(telegram_user_id=7101),
    )

    assert result.list_id == add_result.list_id
    assert result.list_status == ShoppingListStatusEnum.DRAFT
    assert result.is_empty is False
    assert [category.category_code for category in result.categories] == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
        CategoryCodeEnum.EGGS,
    ]
    assert [category.items[0].display_text for category in result.categories] == [
        "молоко",
        "хлеб",
        "яйца",
    ]


@pytest.mark.asyncio
async def test_bought_item_status_is_visible_in_current_list(
    db_session,
    db_session_factory,
) -> None:
    add_result = await make_add_items_use_case(db_session_factory).execute(
        make_add_command("молоко", telegram_user_id=7103),
    )
    item_id = add_result.added_items[0].item_id
    items = SqlAlchemyShoppingItemRepository(db_session)
    await items.update_status(
        item_id=item_id,
        status=ShoppingItemStatusEnum.BOUGHT,
        bought_at=RECEIVED_AT,
        bought_by_user_id=add_result.user_id,
    )
    await db_session.commit()

    result = await make_get_current_list_use_case(db_session_factory).execute(
        GetCurrentListQuery(telegram_user_id=7103),
    )

    item = result.categories[0].items[0]

    assert item.item_id == item_id
    assert item.status == ShoppingItemStatusEnum.BOUGHT


@pytest.mark.asyncio
async def test_current_shopping_list_is_returned_with_shopping_status(
    db_session,
    db_session_factory,
) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    categories = SqlAlchemyCategoryRepository(db_session)
    items = SqlAlchemyShoppingItemRepository(db_session)

    user = await users.create_or_update_from_telegram(telegram_user_id=7104)
    category = await categories.get_by_code(CategoryCodeEnum.BAKERY)
    shopping_list = await lists.create_draft(owner_user_id=user.id)
    await lists.set_status(
        list_id=shopping_list.id,
        status=ShoppingListStatusEnum.SHOPPING,
        shopping_started_at=RECEIVED_AT,
    )
    await items.create(
        list_id=shopping_list.id,
        created_by_user_id=user.id,
        display_text="хлеб",
        product_key="хлеб",
        category_id=category.id,
        position=1,
    )
    await db_session.commit()

    result = await make_get_current_list_use_case(db_session_factory).execute(
        GetCurrentListQuery(telegram_user_id=7104),
    )

    assert result.list_id == shopping_list.id
    assert result.list_status == ShoppingListStatusEnum.SHOPPING
    assert result.categories[0].items[0].display_text == "хлеб"
