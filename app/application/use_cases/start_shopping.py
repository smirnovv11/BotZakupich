"""Use case for starting the active shopping checklist."""

from collections.abc import Callable

from app.application.dto import StartShoppingCommand, StartShoppingResult
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.enums import ShoppingListStatusEnum


class StartShoppingUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(self, command: StartShoppingCommand) -> StartShoppingResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                raise ValueError("user does not have a draft shopping list")

            shopping_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if shopping_list is None:
                raise ValueError("user does not have a draft shopping list")

            if shopping_list.status != ShoppingListStatusEnum.DRAFT:
                raise ValueError("current shopping list is not in draft status")

            items = await unit_of_work.shopping_items.list_by_list_id(shopping_list.id)
            if not items:
                raise ValueError("cannot start shopping with an empty list")

            shopping_list = await unit_of_work.shopping_lists.set_status(
                list_id=shopping_list.id,
                status=ShoppingListStatusEnum.SHOPPING,
                shopping_started_at=command.started_at,
            )

            return StartShoppingResult(
                list_id=shopping_list.id,
                list_status=shopping_list.status,
                shopping_started_at=shopping_list.shopping_started_at,
                item_count=len(items),
            )
