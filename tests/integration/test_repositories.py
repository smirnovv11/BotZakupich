from datetime import UTC, datetime

import pytest
from app.domain.enums import (
    CategoryCodeEnum,
    ParserSourceEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyInputMessageRepository,
    SqlAlchemyShoppingItemRepository,
    SqlAlchemyShoppingListRepository,
    SqlAlchemyUserRepository,
)
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_repositories_create_and_read_basic_entities(db_session) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    categories = SqlAlchemyCategoryRepository(db_session)
    input_messages = SqlAlchemyInputMessageRepository(db_session)
    items = SqlAlchemyShoppingItemRepository(db_session)

    user = await users.create_or_update_from_telegram(
        telegram_user_id=1001,
        telegram_username="buyer",
        first_name="Test",
        language_code="ru",
        last_seen_at=datetime(2026, 8, 20, tzinfo=UTC),
    )
    category = await categories.get_by_code(CategoryCodeEnum.DAIRY)
    shopping_list = await lists.create_draft(owner_user_id=user.id, title="Покупки")
    input_message = await input_messages.create(
        user_id=user.id,
        telegram_chat_id=2001,
        telegram_message_id=3001,
        raw_text="молоко",
        parser_source=ParserSourceEnum.LOCAL,
        parser_version="test-v1",
        received_at=datetime(2026, 8, 20, tzinfo=UTC),
    )
    item = await items.create(
        list_id=shopping_list.id,
        created_by_user_id=user.id,
        source_input_message_id=input_message.id,
        display_text="молоко",
        product_key="молоко",
        category_id=category.id,
        position=1,
    )

    assert await users.get_by_telegram_id(1001) == user
    assert await categories.get_default() is not None
    assert await lists.get_current_by_owner(user.id) == shopping_list
    assert (
        await input_messages.get_by_telegram_message(
            telegram_chat_id=2001,
            telegram_message_id=3001,
        )
        == input_message
    )
    assert await items.get_by_id(item.id) == item
    assert await items.list_by_list_id(shopping_list.id) == [item]


@pytest.mark.asyncio
async def test_input_message_unique_constraint_is_enforced(db_session) -> None:
    users = SqlAlchemyUserRepository(db_session)
    input_messages = SqlAlchemyInputMessageRepository(db_session)
    user = await users.create_or_update_from_telegram(telegram_user_id=1002)

    await input_messages.create(
        user_id=user.id,
        telegram_chat_id=2002,
        telegram_message_id=3002,
        raw_text="молоко",
        parser_source=ParserSourceEnum.LOCAL,
        received_at=datetime(2026, 8, 20, tzinfo=UTC),
    )

    with pytest.raises(IntegrityError):
        await input_messages.create(
            user_id=user.id,
            telegram_chat_id=2002,
            telegram_message_id=3002,
            raw_text="хлеб",
            parser_source=ParserSourceEnum.LOCAL,
            received_at=datetime(2026, 8, 20, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_input_message_get_or_create_is_idempotent(db_session) -> None:
    users = SqlAlchemyUserRepository(db_session)
    input_messages = SqlAlchemyInputMessageRepository(db_session)
    user = await users.create_or_update_from_telegram(telegram_user_id=1005)

    (
        created_message,
        was_created,
    ) = await input_messages.get_or_create_by_telegram_message(
        user_id=user.id,
        telegram_chat_id=2005,
        telegram_message_id=3005,
        raw_text="молоко",
        parser_source=ParserSourceEnum.LOCAL,
        parser_version="test-v1",
        received_at=datetime(2026, 8, 20, tzinfo=UTC),
    )
    (
        existing_message,
        was_created_again,
    ) = await input_messages.get_or_create_by_telegram_message(
        user_id=user.id,
        telegram_chat_id=2005,
        telegram_message_id=3005,
        raw_text="хлеб",
        parser_source=ParserSourceEnum.LOCAL,
        parser_version="test-v2",
        received_at=datetime(2026, 8, 20, tzinfo=UTC),
    )

    assert was_created is True
    assert was_created_again is False
    assert existing_message.id == created_message.id
    assert existing_message.raw_text == "молоко"
    assert existing_message.parser_version == "test-v1"


@pytest.mark.asyncio
async def test_current_list_lookup_ignores_archived_lists(db_session) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    user = await users.create_or_update_from_telegram(telegram_user_id=1003)

    archived_list = await lists.create_draft(owner_user_id=user.id)
    await lists.set_status(
        list_id=archived_list.id,
        status=ShoppingListStatusEnum.ARCHIVED,
        archived_at=datetime(2026, 8, 20, tzinfo=UTC),
        archived_by_user_id=user.id,
    )
    active_list = await lists.create_draft(owner_user_id=user.id)

    assert await lists.get_current_by_owner(user.id) == active_list


@pytest.mark.asyncio
async def test_item_status_update_sets_and_clears_bought_fields(db_session) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    categories = SqlAlchemyCategoryRepository(db_session)
    items = SqlAlchemyShoppingItemRepository(db_session)

    user = await users.create_or_update_from_telegram(telegram_user_id=1004)
    category = await categories.get_by_code(CategoryCodeEnum.BAKERY)
    shopping_list = await lists.create_draft(owner_user_id=user.id)
    item = await items.create(
        list_id=shopping_list.id,
        created_by_user_id=user.id,
        display_text="хлеб",
        product_key="хлеб",
        category_id=category.id,
        position=1,
    )

    bought_at = datetime(2026, 8, 20, tzinfo=UTC)
    bought_item = await items.update_status(
        item_id=item.id,
        status=ShoppingItemStatusEnum.BOUGHT,
        bought_at=bought_at,
        bought_by_user_id=user.id,
    )

    assert bought_item.status == ShoppingItemStatusEnum.BOUGHT
    assert bought_item.bought_at == bought_at
    assert bought_item.bought_by_user_id == user.id

    pending_item = await items.update_status(
        item_id=item.id,
        status=ShoppingItemStatusEnum.PENDING,
    )

    assert pending_item.status == ShoppingItemStatusEnum.PENDING
    assert pending_item.bought_at is None
    assert pending_item.bought_by_user_id is None
