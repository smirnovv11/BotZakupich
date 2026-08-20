"""Use case for permanently deleting the current shopping list."""

from collections.abc import Callable

from app.application.dto import ClearCurrentListCommand, ClearCurrentListResult
from app.application.ports.unit_of_work import UnitOfWork


class ClearCurrentListUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(
        self,
        command: ClearCurrentListCommand,
    ) -> ClearCurrentListResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                return ClearCurrentListResult(
                    list_id=None,
                    deleted_item_count=0,
                )

            current_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if current_list is None:
                return ClearCurrentListResult(
                    list_id=None,
                    deleted_item_count=0,
                )

            items = await unit_of_work.shopping_items.list_by_list_id(current_list.id)
            deleted_list = await unit_of_work.shopping_lists.delete_current_by_owner(
                user.id,
            )

            return ClearCurrentListResult(
                list_id=deleted_list.id if deleted_list is not None else None,
                deleted_item_count=len(items),
            )
