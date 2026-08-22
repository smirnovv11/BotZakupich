"""Use case for deleting selected items from the current shopping list."""

from collections.abc import Callable

from app.application.dto import (
    DeleteCurrentListItemsCommand,
    DeleteCurrentListItemsResult,
)
from app.application.ports.unit_of_work import UnitOfWork


class DeleteCurrentListItemsUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(
        self,
        command: DeleteCurrentListItemsCommand,
    ) -> DeleteCurrentListItemsResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                return DeleteCurrentListItemsResult(
                    list_id=None,
                    deleted_item_count=0,
                )

            current_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if current_list is None:
                return DeleteCurrentListItemsResult(
                    list_id=None,
                    deleted_item_count=0,
                )

            unique_item_ids = tuple(dict.fromkeys(command.item_ids))
            deleted_item_count = (
                await unit_of_work.shopping_items.delete_by_list_id_and_ids(
                    list_id=current_list.id,
                    item_ids=unique_item_ids,
                )
            )

            return DeleteCurrentListItemsResult(
                list_id=current_list.id,
                deleted_item_count=deleted_item_count,
            )
