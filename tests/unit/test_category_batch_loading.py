from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from app.application.dto import GetArchivedListQuery, GetCurrentListQuery
from app.application.use_cases.archive import GetArchivedListUseCase
from app.application.use_cases.get_current_list import GetCurrentListUseCase
from app.domain.enums import ShoppingItemStatusEnum, ShoppingListStatusEnum


class FakeCategoryRepository:
    def __init__(self, categories: list[object]) -> None:
        self.categories = categories
        self.list_all_calls = 0

    async def list_all(self) -> list[object]:
        self.list_all_calls += 1
        return self.categories

    async def get_by_code(self, code: str) -> object:
        raise AssertionError(f"unexpected per-category lookup: {code}")


class FakeUnitOfWork:
    def __init__(self, *, archived: bool = False) -> None:
        user = SimpleNamespace(id=1)
        shopping_list = SimpleNamespace(
            id=10,
            status=(
                ShoppingListStatusEnum.ARCHIVED
                if archived
                else ShoppingListStatusEnum.SHOPPING
            ),
            title=None,
            archived_at=datetime(2026, 8, 23, tzinfo=UTC),
        )
        category = SimpleNamespace(
            id=5,
            code="dairy",
            name_ru="Молочные продукты",
            sort_order=10,
        )
        item = SimpleNamespace(
            id=100,
            category_id=category.id,
            display_text="молоко",
            status=ShoppingItemStatusEnum.PENDING,
            position=1,
            quantity_amount=None,
            quantity_unit=None,
        )

        self.categories = FakeCategoryRepository([category])
        self.users = SimpleNamespace(get_by_telegram_id=self._returning(user))
        self.shopping_lists = SimpleNamespace(
            get_current_by_owner=self._returning(shopping_list),
            get_archived_by_owner=self._returning(shopping_list),
        )
        self.shopping_items = SimpleNamespace(
            list_by_list_id=self._returning([item]),
        )

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    @staticmethod
    def _returning(value):
        async def method(*args, **kwargs):
            return value

        return method


@pytest.mark.asyncio
async def test_current_list_loads_categories_in_one_batch() -> None:
    unit_of_work = FakeUnitOfWork()
    use_case = GetCurrentListUseCase(lambda: unit_of_work)

    result = await use_case.execute(GetCurrentListQuery(telegram_user_id=123))

    assert result.categories[0].items[0].display_text == "молоко"
    assert unit_of_work.categories.list_all_calls == 1


@pytest.mark.asyncio
async def test_archived_list_loads_categories_in_one_batch() -> None:
    unit_of_work = FakeUnitOfWork(archived=True)
    use_case = GetArchivedListUseCase(lambda: unit_of_work)

    result = await use_case.execute(
        GetArchivedListQuery(telegram_user_id=123, archived_list_id=10),
    )

    assert result.categories[0].items[0].display_text == "молоко"
    assert unit_of_work.categories.list_all_calls == 1
