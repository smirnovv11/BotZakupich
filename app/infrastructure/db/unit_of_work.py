"""SQLAlchemy UnitOfWork implementation."""

from types import TracebackType

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
)

from app.infrastructure.db.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyInputMessageRepository,
    SqlAlchemyShoppingItemRepository,
    SqlAlchemyShoppingListRepository,
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None
        self.transaction: AsyncSessionTransaction | None = None
        self.users: SqlAlchemyUserRepository | None = None
        self.shopping_lists: SqlAlchemyShoppingListRepository | None = None
        self.categories: SqlAlchemyCategoryRepository | None = None
        self.input_messages: SqlAlchemyInputMessageRepository | None = None
        self.shopping_items: SqlAlchemyShoppingItemRepository | None = None
        self._is_finished = False

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.transaction = await self.session.begin()
        self._is_finished = False

        self.users = SqlAlchemyUserRepository(self.session)
        self.shopping_lists = SqlAlchemyShoppingListRepository(self.session)
        self.categories = SqlAlchemyCategoryRepository(self.session)
        self.input_messages = SqlAlchemyInputMessageRepository(self.session)
        self.shopping_items = SqlAlchemyShoppingItemRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self.session is not None:
                await self.session.close()

    async def commit(self) -> None:
        if self.transaction is not None and not self._is_finished:
            await self.transaction.commit()
            self._is_finished = True

    async def rollback(self) -> None:
        if self.transaction is not None and not self._is_finished:
            await self.transaction.rollback()
            self._is_finished = True
