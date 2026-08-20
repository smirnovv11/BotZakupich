"""Use case for adding shopping items from a text message."""

from collections.abc import Callable

from app.application.dto import (
    AddedItemDTO,
    AddItemsCommand,
    AddItemsResult,
)
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services.categorizer import LocalCategorizer
from app.application.services.parser import LocalMessageParser
from app.domain.enums import ParserSourceEnum


class AddItemsUseCase:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        parser: LocalMessageParser | None = None,
        categorizer: LocalCategorizer | None = None,
        parser_version: str | None = None,
    ) -> None:
        self.unit_of_work_factory = unit_of_work_factory
        self.parser = parser or LocalMessageParser()
        self.categorizer = categorizer or LocalCategorizer()
        self.parser_version = parser_version

    async def execute(self, command: AddItemsCommand) -> AddItemsResult:
        async with self.unit_of_work_factory() as unit_of_work:
            user = await unit_of_work.users.create_or_update_from_telegram(
                telegram_user_id=command.user.telegram_user_id,
                telegram_username=command.user.telegram_username,
                first_name=command.user.first_name,
                last_name=command.user.last_name,
                language_code=command.user.language_code,
                last_seen_at=command.received_at,
            )

            (
                input_message,
                is_new_input_message,
            ) = await unit_of_work.input_messages.get_or_create_by_telegram_message(
                user_id=user.id,
                telegram_chat_id=command.telegram_chat_id,
                telegram_message_id=command.telegram_message_id,
                raw_text=command.raw_text,
                parser_source=ParserSourceEnum.LOCAL,
                parser_version=self.parser_version,
                received_at=command.received_at,
            )

            if not is_new_input_message:
                current_list = await unit_of_work.shopping_lists.get_current_by_owner(
                    user.id,
                )
                return AddItemsResult(
                    user_id=user.id,
                    list_id=current_list.id if current_list is not None else None,
                    list_status=(
                        current_list.status if current_list is not None else None
                    ),
                    input_message_id=input_message.id,
                    added_items=(),
                    is_duplicate_message=True,
                )

            shopping_list = await unit_of_work.shopping_lists.get_current_by_owner(
                user.id,
            )
            if shopping_list is None:
                shopping_list = await unit_of_work.shopping_lists.create_draft(
                    owner_user_id=user.id,
                )

            candidates = self.parser.split(command.raw_text)
            existing_items = await unit_of_work.shopping_items.list_by_list_id(
                shopping_list.id,
            )
            next_position = (
                max(
                    (item.position for item in existing_items),
                    default=0,
                )
                + 1
            )

            added_items: list[AddedItemDTO] = []
            for candidate in candidates:
                categorization = self.categorizer.categorize(candidate.product_key)
                category = await unit_of_work.categories.get_by_code(
                    categorization.category_code,
                )
                is_category_fallback = categorization.is_fallback

                if category is None:
                    category = await unit_of_work.categories.get_default()
                    is_category_fallback = True

                if category is None:
                    raise ValueError("default category is not seeded")

                item = await unit_of_work.shopping_items.create(
                    list_id=shopping_list.id,
                    created_by_user_id=user.id,
                    source_input_message_id=input_message.id,
                    display_text=candidate.display_text,
                    product_key=candidate.product_key,
                    category_id=category.id,
                    quantity_amount=candidate.quantity_amount,
                    quantity_unit=candidate.quantity_unit,
                    position=next_position,
                )
                added_items.append(
                    AddedItemDTO(
                        item_id=item.id,
                        display_text=item.display_text,
                        product_key=item.product_key,
                        category_code=category.code,
                        category_name_ru=category.name_ru,
                        is_category_fallback=is_category_fallback,
                        quantity_amount=item.quantity_amount,
                        quantity_unit=item.quantity_unit,
                        position=item.position,
                    ),
                )
                next_position += 1

            return AddItemsResult(
                user_id=user.id,
                list_id=shopping_list.id,
                list_status=shopping_list.status,
                input_message_id=input_message.id,
                added_items=tuple(added_items),
            )
