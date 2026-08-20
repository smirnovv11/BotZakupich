"""Use case for reading the current shopping list."""

from collections.abc import Callable

from app.application.dto import CurrentListDTO, GetCurrentListQuery
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services.list_presenter import (
    ListPresenter,
    empty_current_list,
)
from app.domain.categories import CATEGORY_DEFINITIONS


class GetCurrentListUseCase:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        presenter: ListPresenter | None = None,
    ) -> None:
        self.unit_of_work_factory = unit_of_work_factory
        self.presenter = presenter or ListPresenter()

    async def execute(self, query: GetCurrentListQuery) -> CurrentListDTO:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(query.telegram_user_id)
            if user is None:
                return empty_current_list()

            shopping_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if shopping_list is None:
                return empty_current_list()

            items = await unit_of_work.shopping_items.list_by_list_id(shopping_list.id)
            categories = []
            for category_definition in CATEGORY_DEFINITIONS:
                category = await unit_of_work.categories.get_by_code(
                    category_definition.code,
                )
                if category is not None:
                    categories.append(category)

            return self.presenter.present(shopping_list, items, categories)
