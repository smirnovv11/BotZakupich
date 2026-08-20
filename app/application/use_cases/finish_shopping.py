"""Use case for archiving a finished shopping checklist."""

from collections.abc import Callable

from app.application.dto import FinishShoppingCommand, FinishShoppingResult
from app.application.errors import ApplicationError, ApplicationErrorCodeEnum
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.enums import ShoppingListStatusEnum


class FinishShoppingUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(self, command: FinishShoppingCommand) -> FinishShoppingResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ACTIVE_LIST_NOT_FOUND,
                    "user does not have an active shopping list",
                )

            shopping_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if (
                shopping_list is None
                or shopping_list.status != ShoppingListStatusEnum.SHOPPING
            ):
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ACTIVE_LIST_NOT_FOUND,
                    "user does not have an active shopping list",
                )

            shopping_list = await unit_of_work.shopping_lists.set_status(
                list_id=shopping_list.id,
                status=ShoppingListStatusEnum.ARCHIVED,
                shopping_started_at=shopping_list.shopping_started_at,
                archived_at=command.finished_at,
                archived_by_user_id=user.id,
            )

            return FinishShoppingResult(
                list_id=shopping_list.id,
                list_status=shopping_list.status,
                archived_at=shopping_list.archived_at,
                archived_by_user_id=shopping_list.archived_by_user_id,
            )
