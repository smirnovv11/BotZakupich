from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.application.dto import AddItemsCommand, TelegramUserDTO
from app.application.use_cases.add_items import AddItemsUseCase
from app.domain.enums import (
    CategoryCodeEnum,
    ParserSourceEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.models import Category, InputMessage, ShoppingItem, User
from app.infrastructure.db.repositories import (
    SqlAlchemyShoppingListRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import func, select

RECEIVED_AT = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)


def make_command(
    raw_text: str,
    *,
    telegram_user_id: int = 7001,
    telegram_chat_id: int = 8001,
    telegram_message_id: int = 9001,
) -> AddItemsCommand:
    return AddItemsCommand(
        user=TelegramUserDTO(
            telegram_user_id=telegram_user_id,
            telegram_username="buyer",
            first_name="Test",
            language_code="ru",
        ),
        telegram_chat_id=telegram_chat_id,
        telegram_message_id=telegram_message_id,
        raw_text=raw_text,
        received_at=RECEIVED_AT,
    )


def make_use_case(db_session_factory) -> AddItemsUseCase:
    return AddItemsUseCase(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(db_session_factory),
        parser_version="test-v1",
    )


async def get_item_categories(db_session, list_id: int) -> list[str]:
    result = await db_session.execute(
        select(Category.code)
        .join(ShoppingItem, ShoppingItem.category_id == Category.id)
        .where(ShoppingItem.list_id == list_id)
        .order_by(ShoppingItem.position),
    )
    return list(result.scalars())


@pytest.mark.asyncio
async def test_first_message_creates_user_draft_input_message_and_item(
    db_session,
    db_session_factory,
) -> None:
    result = await make_use_case(db_session_factory).execute(make_command("молоко"))

    user = await db_session.scalar(
        select(User).where(User.telegram_user_id == 7001),
    )
    input_message = await db_session.get(InputMessage, result.input_message_id)
    item = await db_session.get(ShoppingItem, result.added_items[0].item_id)

    assert user is not None
    assert result.user_id == user.id
    assert result.list_status == ShoppingListStatusEnum.DRAFT
    assert result.is_duplicate_message is False
    assert input_message is not None
    assert input_message.raw_text == "молоко"
    assert input_message.parser_source == ParserSourceEnum.LOCAL
    assert input_message.parser_version == "test-v1"
    assert item is not None
    assert item.display_text == "молоко"
    assert item.product_key == "молоко"
    assert item.position == 1
    assert result.added_items[0].category_code == CategoryCodeEnum.DAIRY


@pytest.mark.asyncio
async def test_comma_separated_message_creates_multiple_categorized_items(
    db_session,
    db_session_factory,
) -> None:
    result = await make_use_case(db_session_factory).execute(
        make_command("молоко, хлеб, яйца"),
    )

    items = (
        await db_session.scalars(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == result.list_id)
            .order_by(ShoppingItem.position),
        )
    ).all()

    assert [item.display_text for item in items] == ["молоко", "хлеб", "яйца"]
    assert [item.position for item in items] == [1, 2, 3]
    assert await get_item_categories(db_session, result.list_id) == [
        CategoryCodeEnum.DAIRY,
        CategoryCodeEnum.BAKERY,
        CategoryCodeEnum.EGGS,
    ]


@pytest.mark.asyncio
async def test_quantity_fields_are_persisted(db_session, db_session_factory) -> None:
    result = await make_use_case(db_session_factory).execute(
        make_command("2 литра молока"),
    )

    item = await db_session.get(ShoppingItem, result.added_items[0].item_id)

    assert item is not None
    assert item.display_text == "2 литра молока"
    assert item.product_key == "молоко"
    assert item.quantity_amount == Decimal("2")
    assert item.quantity_unit == "литра"


@pytest.mark.asyncio
async def test_unknown_item_uses_default_other_category(
    db_session,
    db_session_factory,
) -> None:
    result = await make_use_case(db_session_factory).execute(
        make_command("манго сушеное"),
    )

    item_result = result.added_items[0]
    item_categories = await get_item_categories(db_session, result.list_id)

    assert item_result.category_code == CategoryCodeEnum.OTHER
    assert item_result.category_name_ru == "Прочие"
    assert item_result.is_category_fallback is True
    assert item_categories == [CategoryCodeEnum.OTHER]


@pytest.mark.asyncio
async def test_message_while_shopping_adds_item_to_active_checklist(
    db_session,
    db_session_factory,
) -> None:
    users = SqlAlchemyUserRepository(db_session)
    lists = SqlAlchemyShoppingListRepository(db_session)
    user = await users.create_or_update_from_telegram(telegram_user_id=7002)
    shopping_list = await lists.create_draft(owner_user_id=user.id)
    await lists.set_status(
        list_id=shopping_list.id,
        status=ShoppingListStatusEnum.SHOPPING,
        shopping_started_at=RECEIVED_AT,
    )
    await db_session.commit()

    result = await make_use_case(db_session_factory).execute(
        make_command(
            "хлеб",
            telegram_user_id=7002,
            telegram_chat_id=8002,
            telegram_message_id=9002,
        ),
    )

    assert result.list_id == shopping_list.id
    assert result.list_status == ShoppingListStatusEnum.SHOPPING
    assert result.added_items[0].display_text == "хлеб"


@pytest.mark.asyncio
async def test_duplicate_telegram_message_does_not_duplicate_items_or_input_messages(
    db_session,
    db_session_factory,
) -> None:
    use_case = make_use_case(db_session_factory)
    command = make_command("молоко")

    first_result = await use_case.execute(command)
    duplicate_result = await use_case.execute(command)

    input_message_count = await db_session.scalar(
        select(func.count()).select_from(InputMessage),
    )
    item_count = await db_session.scalar(select(func.count()).select_from(ShoppingItem))

    assert first_result.is_duplicate_message is False
    assert duplicate_result.is_duplicate_message is True
    assert duplicate_result.input_message_id == first_result.input_message_id
    assert duplicate_result.list_id == first_result.list_id
    assert duplicate_result.added_items == ()
    assert input_message_count == 1
    assert item_count == 1


@pytest.mark.asyncio
async def test_empty_message_creates_no_items_and_does_not_fail(
    db_session,
    db_session_factory,
) -> None:
    result = await make_use_case(db_session_factory).execute(make_command(" \n\t "))

    item_count = await db_session.scalar(select(func.count()).select_from(ShoppingItem))
    input_message_count = await db_session.scalar(
        select(func.count()).select_from(InputMessage),
    )

    assert result.list_id is not None
    assert result.list_status == ShoppingListStatusEnum.DRAFT
    assert result.added_items == ()
    assert input_message_count == 1
    assert item_count == 0
