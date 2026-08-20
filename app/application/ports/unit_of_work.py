"""UnitOfWork protocol for application use cases."""

from types import TracebackType
from typing import Protocol

from app.application.ports.repositories import (
    CategoryRepository,
    InputMessageRepository,
    ShoppingItemRepository,
    ShoppingListRepository,
    UserRepository,
)


class UnitOfWork(Protocol):
    users: UserRepository
    shopping_lists: ShoppingListRepository
    categories: CategoryRepository
    input_messages: InputMessageRepository
    shopping_items: ShoppingItemRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
