"""Use cases for archived shopping trips and item restore."""

from collections.abc import Callable, Iterable

from app.application.dto import (
    ArchivedListDTO,
    ArchivedListSummaryDTO,
    GetArchivedListQuery,
    ListArchivesQuery,
    ListArchivesResult,
    RestoreArchivedItemsCommand,
    RestoreArchivedItemsResult,
    RestoredItemDTO,
)
from app.application.errors import ApplicationError, ApplicationErrorCodeEnum
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services.list_presenter import ListPresenter
from app.domain.categories import CATEGORY_DEFINITIONS


class ListArchivesUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(self, query: ListArchivesQuery) -> ListArchivesResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(query.telegram_user_id)
            if user is None:
                return ListArchivesResult(archives=())

            archived_lists = await unit_of_work.shopping_lists.list_archived_by_owner(
                user.id,
            )

            summaries: list[ArchivedListSummaryDTO] = []
            for archived_list in archived_lists:
                items = await unit_of_work.shopping_items.list_by_list_id(
                    archived_list.id,
                )
                summaries.append(
                    ArchivedListSummaryDTO(
                        list_id=archived_list.id,
                        list_status=archived_list.status,
                        title=archived_list.title,
                        archived_at=archived_list.archived_at,
                        item_count=len(items),
                    ),
                )

            return ListArchivesResult(archives=tuple(summaries))


class GetArchivedListUseCase:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        presenter: ListPresenter | None = None,
    ) -> None:
        self.unit_of_work_factory = unit_of_work_factory
        self.presenter = presenter or ListPresenter()

    async def execute(self, query: GetArchivedListQuery) -> ArchivedListDTO:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(query.telegram_user_id)
            if user is None:
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
                    "archived shopping list was not found",
                )

            archived_list = await unit_of_work.shopping_lists.get_archived_by_owner(
                list_id=query.archived_list_id,
                owner_user_id=user.id,
            )
            if archived_list is None:
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
                    "archived shopping list was not found",
                )

            items = await unit_of_work.shopping_items.list_by_list_id(archived_list.id)
            categories = await _load_categories(unit_of_work)
            presented = self.presenter.present(archived_list, items, categories)

            return ArchivedListDTO(
                list_id=presented.list_id,
                list_status=presented.list_status,
                title=presented.title,
                archived_at=archived_list.archived_at,
                categories=presented.categories,
            )


class RestoreArchivedItemsUseCase:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work_factory = unit_of_work_factory

    async def execute(
        self,
        command: RestoreArchivedItemsCommand,
    ) -> RestoreArchivedItemsResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.get_by_telegram_id(
                command.telegram_user_id,
            )
            if user is None:
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
                    "archived shopping list was not found",
                )

            archived_list = await unit_of_work.shopping_lists.get_archived_by_owner(
                list_id=command.archived_list_id,
                owner_user_id=user.id,
            )
            if archived_list is None:
                raise ApplicationError(
                    ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
                    "archived shopping list was not found",
                )

            source_items = await unit_of_work.shopping_items.list_by_list_id(
                archived_list.id,
            )
            items_to_restore = _select_items_to_restore(
                source_items,
                command.item_ids,
            )

            current_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if current_list is None:
                current_list = await unit_of_work.shopping_lists.create_draft(
                    owner_user_id=user.id,
                )

            current_items = await unit_of_work.shopping_items.list_by_list_id(
                current_list.id,
            )
            next_position = (
                max((item.position for item in current_items), default=0) + 1
            )

            restored_items: list[RestoredItemDTO] = []
            for source_item in items_to_restore:
                restored_item = await unit_of_work.shopping_items.create(
                    list_id=current_list.id,
                    created_by_user_id=user.id,
                    restored_from_item_id=source_item.id,
                    display_text=source_item.display_text,
                    product_key=source_item.product_key,
                    category_id=source_item.category_id,
                    quantity_amount=source_item.quantity_amount,
                    quantity_unit=source_item.quantity_unit,
                    position=next_position,
                )
                restored_items.append(
                    RestoredItemDTO(
                        item_id=restored_item.id,
                        restored_from_item_id=source_item.id,
                        display_text=restored_item.display_text,
                        position=restored_item.position,
                    ),
                )
                next_position += 1

            return RestoreArchivedItemsResult(
                list_id=current_list.id,
                list_status=current_list.status,
                restored_items=tuple(restored_items),
            )


async def _load_categories(unit_of_work: UnitOfWork) -> list[object]:
    categories = []
    for category_definition in CATEGORY_DEFINITIONS:
        category = await unit_of_work.categories.get_by_code(category_definition.code)
        if category is not None:
            categories.append(category)
    return categories


def _select_items_to_restore(
    source_items: Iterable[object],
    selected_item_ids: tuple[int, ...] | None,
) -> list[object]:
    ordered_items = sorted(source_items, key=lambda item: item.position)
    if selected_item_ids is None:
        return ordered_items

    items_by_id = {item.id: item for item in ordered_items}
    missing_item_ids = [
        item_id for item_id in selected_item_ids if item_id not in items_by_id
    ]
    if missing_item_ids:
        raise ApplicationError(
            ApplicationErrorCodeEnum.SELECTED_ARCHIVED_ITEM_NOT_IN_LIST,
            "selected archived item does not belong to archived list",
        )

    selected_item_id_set = set(selected_item_ids)
    return [item for item in ordered_items if item.id in selected_item_id_set]
