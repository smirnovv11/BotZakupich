from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from app.application.dto import (
    ArchivedListDTO,
    CurrentListDTO,
    ListCategoryDTO,
    ListItemDTO,
)
from app.application.errors import ApplicationError, ApplicationErrorCodeEnum
from app.domain.enums import CategoryCodeEnum, ShoppingItemStatusEnum
from app.presentation.bot.callbacks import (
    build_confirm_delete_selected_items_callback,
    build_delete_page_fingerprint,
    build_toggle_delete_item_callback,
)
from app.presentation.bot.formatters import DELETE_SELECTION_STALE_MESSAGE
from app.presentation.bot.handlers import archive, items, shopping
from app.presentation.bot.pagination import get_checklist_page


class FakeMessage:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.edits: list[tuple[str, object]] = []

    async def edit_text(self, text: str, reply_markup=None) -> None:
        self.events.append("edit")
        self.edits.append((text, reply_markup))


class FakeCallback:
    def __init__(self, data: str, events: list[str]) -> None:
        self.data = data
        self.events = events
        self.from_user = SimpleNamespace(id=123)
        self.message = FakeMessage(events)
        self.answers: list[tuple[tuple[object, ...], dict[str, object]]] = []

    async def answer(self, *args, **kwargs) -> None:
        self.events.append("answer")
        self.answers.append((args, kwargs))


def make_current_list(item_count: int = 13) -> CurrentListDTO:
    return CurrentListDTO(
        list_id=1,
        list_status="shopping",
        title=None,
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=tuple(
                    ListItemDTO(
                        item_id=item_id,
                        display_text=f"товар {item_id}",
                        status=ShoppingItemStatusEnum.PENDING,
                        position=item_id,
                    )
                    for item_id in range(1, item_count + 1)
                ),
            ),
        ),
    )


def make_archived_list(item_count: int = 13) -> ArchivedListDTO:
    current_list = make_current_list(item_count)
    return ArchivedListDTO(
        list_id=11,
        list_status="archived",
        title=None,
        archived_at=datetime(2026, 8, 23, tzinfo=UTC),
        categories=current_list.categories,
    )


def make_delete_reflow_lists() -> tuple[CurrentListDTO, CurrentListDTO]:
    dairy_item = ListItemDTO(
        item_id=1,
        display_text="молоко",
        status=ShoppingItemStatusEnum.PENDING,
        position=1,
    )
    bakery_items = tuple(
        ListItemDTO(
            item_id=item_id,
            display_text=f"товар {item_id}",
            status=ShoppingItemStatusEnum.PENDING,
            position=item_id,
        )
        for item_id in range(2, 13)
    )
    initial = CurrentListDTO(
        list_id=1,
        list_status="shopping",
        title=None,
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=(dairy_item,),
            ),
            ListCategoryDTO(
                category_code=CategoryCodeEnum.BAKERY,
                category_name_ru="Хлеб и выпечка",
                sort_order=20,
                items=bakery_items,
            ),
        ),
    )
    added_early_category_item = ListItemDTO(
        item_id=13,
        display_text="сыр",
        status=ShoppingItemStatusEnum.PENDING,
        position=13,
    )
    changed = CurrentListDTO(
        list_id=initial.list_id,
        list_status=initial.list_status,
        title=initial.title,
        categories=(
            ListCategoryDTO(
                category_code=CategoryCodeEnum.DAIRY,
                category_name_ru="Молочные продукты",
                sort_order=10,
                items=(dairy_item, added_early_category_item),
            ),
            initial.categories[1],
        ),
    )
    return initial, changed


@pytest.mark.asyncio
async def test_shopping_page_acknowledges_before_loading(monkeypatch) -> None:
    events: list[str] = []
    callback = FakeCallback("scp:1", events)

    async def load_current_list(*args) -> CurrentListDTO:
        events.append("load")
        return make_current_list()

    monkeypatch.setattr(shopping, "Message", FakeMessage)
    monkeypatch.setattr(shopping, "_get_current_list", load_current_list)

    await shopping.handle_shopping_checklist_page_callback(callback, object())

    assert events == ["answer", "load", "edit"]
    assert "🛒 Чеклист покупок · 2/2" in callback.message.edits[0][0]
    assert "товар 13" in callback.message.edits[0][0]


@pytest.mark.asyncio
async def test_delete_page_acknowledges_before_loading(monkeypatch) -> None:
    events: list[str] = []
    callback = FakeCallback("edp:1", events)

    async def load_current_list(*args) -> CurrentListDTO:
        events.append("load")
        return make_current_list()

    monkeypatch.setattr(items, "Message", FakeMessage)
    monkeypatch.setattr(items, "_get_current_list", load_current_list)

    await items.handle_edit_delete_page_callback(callback, object())

    assert events == ["answer", "load", "edit"]
    assert "✏️ Выберите товары для удаления · 2/2" in callback.message.edits[0][0]


@pytest.mark.asyncio
async def test_archive_page_acknowledges_before_loading(monkeypatch) -> None:
    events: list[str] = []
    callback = FakeCallback("arp:11:1", events)

    class FakeUseCase:
        async def execute(self, query) -> ArchivedListDTO:
            events.append("load")
            return make_archived_list()

    monkeypatch.setattr(archive, "Message", FakeMessage)
    monkeypatch.setattr(
        archive,
        "make_get_archived_list_use_case",
        lambda session_factory: FakeUseCase(),
    )

    await archive.handle_archived_restore_page_callback(callback, object())

    assert events == ["answer", "load", "edit"]
    assert "· 2/2" in callback.message.edits[0][0]


@pytest.mark.asyncio
async def test_missing_archive_replaces_stale_keyboard_after_ack(monkeypatch) -> None:
    events: list[str] = []
    callback = FakeCallback("arp:11:1", events)

    class MissingArchiveUseCase:
        async def execute(self, query) -> ArchivedListDTO:
            events.append("load")
            raise ApplicationError(
                ApplicationErrorCodeEnum.ARCHIVED_LIST_NOT_FOUND,
                "archive missing",
            )

    monkeypatch.setattr(archive, "Message", FakeMessage)
    monkeypatch.setattr(
        archive,
        "make_get_archived_list_use_case",
        lambda session_factory: MissingArchiveUseCase(),
    )

    await archive.handle_archived_restore_page_callback(callback, object())

    assert events == ["answer", "load", "edit"]
    assert callback.message.edits[0][0] == "📦 Не нашел этот архивный поход."
    assert callback.message.edits[0][1] is None


@pytest.mark.asyncio
async def test_delete_confirm_rejects_page_reflow_without_deleting(monkeypatch) -> None:
    initial, changed = make_delete_reflow_lists()
    initial_page = get_checklist_page(initial.categories, 0)
    assert initial_page is not None
    fingerprint = build_delete_page_fingerprint(
        tuple(item.item_id for item in initial_page.items),
    )
    callback = FakeCallback(
        build_confirm_delete_selected_items_callback(0, 1 << 11, fingerprint),
        [],
    )

    async def load_changed_list(*args) -> CurrentListDTO:
        return changed

    monkeypatch.setattr(items, "Message", FakeMessage)
    monkeypatch.setattr(items, "_get_current_list", load_changed_list)
    monkeypatch.setattr(
        items,
        "make_delete_current_list_items_use_case",
        lambda session_factory: pytest.fail("stale selection must not delete items"),
    )

    await items.handle_delete_selected_items_confirm(callback, object())

    assert callback.answers == [
        ((DELETE_SELECTION_STALE_MESSAGE,), {"show_alert": True}),
    ]
    assert callback.message.edits
    assert "Выбрано:" not in callback.message.edits[0][0]


@pytest.mark.asyncio
async def test_delete_toggle_rejects_page_reflow_and_resets_selection(
    monkeypatch,
) -> None:
    initial, changed = make_delete_reflow_lists()
    initial_page = get_checklist_page(initial.categories, 0)
    assert initial_page is not None
    fingerprint = build_delete_page_fingerprint(
        tuple(item.item_id for item in initial_page.items),
    )
    callback = FakeCallback(
        build_toggle_delete_item_callback(12, 0, 0, fingerprint),
        [],
    )

    async def load_changed_list(*args) -> CurrentListDTO:
        return changed

    monkeypatch.setattr(items, "Message", FakeMessage)
    monkeypatch.setattr(items, "_get_current_list", load_changed_list)

    await items.handle_toggle_delete_item_callback(callback, object())

    assert callback.answers == [
        ((DELETE_SELECTION_STALE_MESSAGE,), {"show_alert": True}),
    ]
    assert callback.message.edits


@pytest.mark.asyncio
async def test_legacy_delete_callback_is_rejected_and_redrawn(monkeypatch) -> None:
    events: list[str] = []
    callback = FakeCallback("ldc:0:1", events)

    async def load_current_list(*args) -> CurrentListDTO:
        events.append("load")
        return make_current_list()

    monkeypatch.setattr(items, "Message", FakeMessage)
    monkeypatch.setattr(items, "_get_current_list", load_current_list)

    await items.handle_legacy_delete_selection_callback(callback, object())

    assert events == ["answer", "load", "edit"]
    assert callback.answers == [
        ((DELETE_SELECTION_STALE_MESSAGE,), {"show_alert": True}),
    ]
    assert callback.message.edits
