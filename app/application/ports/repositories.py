"""Repository protocols used by application use cases."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol


class UserRepository(Protocol):
    async def get_by_telegram_id(self, telegram_user_id: int) -> Any | None: ...

    async def create_or_update_from_telegram(
        self,
        *,
        telegram_user_id: int,
        telegram_username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
        last_seen_at: datetime | None = None,
    ) -> Any: ...


class ShoppingListRepository(Protocol):
    async def get_by_id(self, list_id: int) -> Any | None: ...

    async def get_current_by_owner(self, owner_user_id: int) -> Any | None: ...

    async def delete_current_by_owner(self, owner_user_id: int) -> Any | None: ...

    async def list_archived_by_owner(self, owner_user_id: int) -> list[Any]: ...

    async def get_archived_by_owner(
        self,
        *,
        list_id: int,
        owner_user_id: int,
    ) -> Any | None: ...

    async def create_draft(
        self,
        *,
        owner_user_id: int,
        title: str | None = None,
    ) -> Any: ...

    async def set_status(
        self,
        *,
        list_id: int,
        status: str,
        shopping_started_at: datetime | None = None,
        archived_at: datetime | None = None,
        archived_by_user_id: int | None = None,
    ) -> Any: ...


class CategoryRepository(Protocol):
    async def get_by_code(self, code: str) -> Any | None: ...

    async def get_default(self) -> Any | None: ...

    async def list_all(self) -> list[Any]: ...


class InputMessageRepository(Protocol):
    async def get_by_telegram_message(
        self,
        *,
        telegram_chat_id: int,
        telegram_message_id: int,
    ) -> Any | None: ...

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
    ) -> Any: ...

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
    ) -> tuple[Any, bool]: ...


class ShoppingItemRepository(Protocol):
    async def get_by_id(self, item_id: int) -> Any | None: ...

    async def list_by_list_id(self, list_id: int) -> list[Any]: ...

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
    ) -> Any: ...

    async def update_status(
        self,
        *,
        item_id: int,
        status: str,
        bought_at: datetime | None = None,
        bought_by_user_id: int | None = None,
    ) -> Any: ...

    async def delete_by_list_id_and_ids(
        self,
        *,
        list_id: int,
        item_ids: tuple[int, ...],
    ) -> int: ...
