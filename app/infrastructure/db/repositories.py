"""SQLAlchemy repository implementations."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ShoppingItemStatusEnum, ShoppingListStatusEnum
from app.infrastructure.db.models import (
    Category,
    InputMessage,
    ShoppingItem,
    ShoppingList,
    User,
)


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_user_id: int) -> User | None:
        return await self.session.scalar(
            select(User).where(User.telegram_user_id == telegram_user_id),
        )

    async def create_or_update_from_telegram(
        self,
        *,
        telegram_user_id: int,
        telegram_username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
        last_seen_at: datetime | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_user_id)
        if user is None:
            user = User(telegram_user_id=telegram_user_id)
            self.session.add(user)

        user.telegram_username = telegram_username
        user.first_name = first_name
        user.last_name = last_name
        user.language_code = language_code
        user.last_seen_at = last_seen_at

        await self.session.flush()
        return user


class SqlAlchemyShoppingListRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, list_id: int) -> ShoppingList | None:
        return await self.session.get(ShoppingList, list_id)

    async def get_current_by_owner(self, owner_user_id: int) -> ShoppingList | None:
        return await self.session.scalar(
            select(ShoppingList)
            .where(
                ShoppingList.owner_user_id == owner_user_id,
                ShoppingList.status.in_(
                    (
                        ShoppingListStatusEnum.DRAFT,
                        ShoppingListStatusEnum.SHOPPING,
                    ),
                ),
            )
            .order_by(ShoppingList.created_at.desc()),
        )

    async def create_draft(
        self,
        *,
        owner_user_id: int,
        title: str | None = None,
    ) -> ShoppingList:
        shopping_list = ShoppingList(
            owner_user_id=owner_user_id,
            status=ShoppingListStatusEnum.DRAFT,
            title=title,
        )
        self.session.add(shopping_list)
        await self.session.flush()
        return shopping_list

    async def set_status(
        self,
        *,
        list_id: int,
        status: str,
        shopping_started_at: datetime | None = None,
        archived_at: datetime | None = None,
        archived_by_user_id: int | None = None,
    ) -> ShoppingList:
        shopping_list = await self.get_by_id(list_id)
        if shopping_list is None:
            raise ValueError(f"shopping list not found: {list_id}")

        shopping_list.status = status
        shopping_list.shopping_started_at = shopping_started_at
        shopping_list.archived_at = archived_at
        shopping_list.archived_by_user_id = archived_by_user_id

        await self.session.flush()
        return shopping_list


class SqlAlchemyCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_code(self, code: str) -> Category | None:
        return await self.session.scalar(select(Category).where(Category.code == code))

    async def get_default(self) -> Category | None:
        return await self.session.scalar(
            select(Category).where(Category.is_default.is_(True)),
        )


class SqlAlchemyInputMessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_message(
        self,
        *,
        telegram_chat_id: int,
        telegram_message_id: int,
    ) -> InputMessage | None:
        return await self.session.scalar(
            select(InputMessage).where(
                InputMessage.telegram_chat_id == telegram_chat_id,
                InputMessage.telegram_message_id == telegram_message_id,
            ),
        )

    async def create(
        self,
        *,
        user_id: int,
        telegram_chat_id: int,
        telegram_message_id: int,
        raw_text: str,
        parser_source: str,
        received_at: datetime,
        parser_version: str | None = None,
        parser_metadata: dict[str, object] | None = None,
    ) -> InputMessage:
        input_message = InputMessage(
            user_id=user_id,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
            raw_text=raw_text,
            parser_source=parser_source,
            parser_version=parser_version,
            parser_metadata=parser_metadata,
            received_at=received_at,
        )
        self.session.add(input_message)
        await self.session.flush()
        return input_message

    async def get_or_create_by_telegram_message(
        self,
        *,
        user_id: int,
        telegram_chat_id: int,
        telegram_message_id: int,
        raw_text: str,
        parser_source: str,
        received_at: datetime,
        parser_version: str | None = None,
        parser_metadata: dict[str, object] | None = None,
    ) -> tuple[InputMessage, bool]:
        statement = (
            insert(InputMessage)
            .values(
                user_id=user_id,
                telegram_chat_id=telegram_chat_id,
                telegram_message_id=telegram_message_id,
                raw_text=raw_text,
                parser_source=parser_source,
                parser_version=parser_version,
                parser_metadata=parser_metadata,
                received_at=received_at,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    InputMessage.telegram_chat_id,
                    InputMessage.telegram_message_id,
                ],
            )
            .returning(InputMessage.id)
        )
        input_message_id = await self.session.scalar(statement)

        if input_message_id is not None:
            input_message = await self.session.get(InputMessage, input_message_id)
            if input_message is None:
                raise ValueError(f"input message not found: {input_message_id}")
            return input_message, True

        input_message = await self.get_by_telegram_message(
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
        )
        if input_message is None:
            raise ValueError("input message conflict row was not found")

        return input_message, False


class SqlAlchemyShoppingItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: int) -> ShoppingItem | None:
        return await self.session.get(ShoppingItem, item_id)

    async def list_by_list_id(self, list_id: int) -> list[ShoppingItem]:
        result = await self.session.scalars(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == list_id)
            .order_by(ShoppingItem.category_id, ShoppingItem.position),
        )
        return list(result)

    async def create(
        self,
        *,
        list_id: int,
        created_by_user_id: int,
        display_text: str,
        product_key: str,
        category_id: int,
        position: int,
        source_input_message_id: int | None = None,
        restored_from_item_id: int | None = None,
        quantity_amount: Decimal | None = None,
        quantity_unit: str | None = None,
    ) -> ShoppingItem:
        shopping_item = ShoppingItem(
            list_id=list_id,
            created_by_user_id=created_by_user_id,
            source_input_message_id=source_input_message_id,
            restored_from_item_id=restored_from_item_id,
            display_text=display_text,
            product_key=product_key,
            category_id=category_id,
            quantity_amount=quantity_amount,
            quantity_unit=quantity_unit,
            status=ShoppingItemStatusEnum.PENDING,
            position=position,
        )
        self.session.add(shopping_item)
        await self.session.flush()
        return shopping_item

    async def update_status(
        self,
        *,
        item_id: int,
        status: str,
        bought_at: datetime | None = None,
        bought_by_user_id: int | None = None,
    ) -> ShoppingItem:
        shopping_item = await self.get_by_id(item_id)
        if shopping_item is None:
            raise ValueError(f"shopping item not found: {item_id}")

        shopping_item.status = status
        shopping_item.bought_at = bought_at
        shopping_item.bought_by_user_id = bought_by_user_id

        await self.session.flush()
        return shopping_item
