"""Use case for toggling an item in the active shopping checklist."""

from collections.abc import Callable

from app.application.dto import ToggleItemCommand, ToggleItemResult
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.enums import ShoppingItemStatusEnum, ShoppingListStatusEnum


class ToggleItemUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(self, command: ToggleItemCommand) -> ToggleItemResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                raise ValueError("user does not have an active shopping list")

            shopping_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if (
                shopping_list is None
                or shopping_list.status != ShoppingListStatusEnum.SHOPPING
            ):
                raise ValueError("user does not have an active shopping list")

            item = await unit_of_work.shopping_items.get_by_id(command.item_id)
            if item is None:
                raise ValueError(f"shopping item not found: {command.item_id}")

            if item.list_id != shopping_list.id:
                raise ValueError("shopping item does not belong to active list")

            if item.status == ShoppingItemStatusEnum.PENDING:
                item = await unit_of_work.shopping_items.update_status(
                    item_id=item.id,
                    status=ShoppingItemStatusEnum.BOUGHT,
                    bought_at=command.toggled_at,
                    bought_by_user_id=user.id,
                )
            elif item.status == ShoppingItemStatusEnum.BOUGHT:
                item = await unit_of_work.shopping_items.update_status(
                    item_id=item.id,
                    status=ShoppingItemStatusEnum.PENDING,
                    bought_at=None,
                    bought_by_user_id=None,
                )
            else:
                raise ValueError(f"unsupported shopping item status: {item.status}")

            return ToggleItemResult(
                item_id=item.id,
                list_id=item.list_id,
                status=item.status,
                bought_at=item.bought_at,
                bought_by_user_id=item.bought_by_user_id,
            )
