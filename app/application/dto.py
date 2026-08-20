"""Application data transfer objects."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TelegramUserDTO:
    telegram_user_id: int
    telegram_username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None


@dataclass(frozen=True, slots=True)
class AddItemsCommand:
    user: TelegramUserDTO
    telegram_chat_id: int
    telegram_message_id: int
    raw_text: str
    received_at: datetime


@dataclass(frozen=True, slots=True)
class AddedItemDTO:
    item_id: int
    display_text: str
    product_key: str
    category_code: str
    category_name_ru: str
    is_category_fallback: bool
    position: int
    quantity_amount: Decimal | None = None
    quantity_unit: str | None = None


@dataclass(frozen=True, slots=True)
class AddItemsResult:
    user_id: int
    list_id: int | None
    list_status: str | None
    input_message_id: int | None
    added_items: tuple[AddedItemDTO, ...]
    is_duplicate_message: bool = False


@dataclass(frozen=True, slots=True)
class GetCurrentListQuery:
    telegram_user_id: int


@dataclass(frozen=True, slots=True)
class StartShoppingCommand:
    telegram_user_id: int
    started_at: datetime


@dataclass(frozen=True, slots=True)
class StartShoppingResult:
    list_id: int
    list_status: str
    shopping_started_at: datetime
    item_count: int


@dataclass(frozen=True, slots=True)
class ToggleItemCommand:
    telegram_user_id: int
    item_id: int
    toggled_at: datetime


@dataclass(frozen=True, slots=True)
class ToggleItemResult:
    item_id: int
    list_id: int
    status: str
    bought_at: datetime | None
    bought_by_user_id: int | None


@dataclass(frozen=True, slots=True)
class FinishShoppingCommand:
    telegram_user_id: int
    finished_at: datetime


@dataclass(frozen=True, slots=True)
class FinishShoppingResult:
    list_id: int
    list_status: str
    archived_at: datetime
    archived_by_user_id: int


@dataclass(frozen=True, slots=True)
class ListArchivesQuery:
    telegram_user_id: int


@dataclass(frozen=True, slots=True)
class ArchivedListSummaryDTO:
    list_id: int
    list_status: str
    title: str | None
    archived_at: datetime
    item_count: int


@dataclass(frozen=True, slots=True)
class ListArchivesResult:
    archives: tuple[ArchivedListSummaryDTO, ...]


@dataclass(frozen=True, slots=True)
class GetArchivedListQuery:
    telegram_user_id: int
    archived_list_id: int


@dataclass(frozen=True, slots=True)
class RestoreArchivedItemsCommand:
    telegram_user_id: int
    archived_list_id: int
    item_ids: tuple[int, ...] | None = None


@dataclass(frozen=True, slots=True)
class RestoredItemDTO:
    item_id: int
    restored_from_item_id: int
    display_text: str
    position: int


@dataclass(frozen=True, slots=True)
class RestoreArchivedItemsResult:
    list_id: int
    list_status: str
    restored_items: tuple[RestoredItemDTO, ...]


@dataclass(frozen=True, slots=True)
class ListItemDTO:
    item_id: int
    display_text: str
    status: str
    position: int
    quantity_amount: Decimal | None = None
    quantity_unit: str | None = None


@dataclass(frozen=True, slots=True)
class ListCategoryDTO:
    category_code: str
    category_name_ru: str
    sort_order: int
    items: tuple[ListItemDTO, ...]


@dataclass(frozen=True, slots=True)
class CurrentListDTO:
    list_id: int | None
    list_status: str | None
    title: str | None
    categories: tuple[ListCategoryDTO, ...]

    @property
    def is_empty(self) -> bool:
        return not any(category.items for category in self.categories)


@dataclass(frozen=True, slots=True)
class ArchivedListDTO:
    list_id: int
    list_status: str
    title: str | None
    archived_at: datetime
    categories: tuple[ListCategoryDTO, ...]

    @property
    def is_empty(self) -> bool:
        return not any(category.items for category in self.categories)
