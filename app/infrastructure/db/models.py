"""SQLAlchemy ORM models for the shopping bot MVP schema."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import (
    ParserSourceEnum,
    ShoppingItemStatusEnum,
    ShoppingListStatusEnum,
)
from app.infrastructure.db.base import Base

SHOPPING_LIST_STATUS_ENUM_NAME = "shopping_list_status_enum"
SHOPPING_ITEM_STATUS_ENUM_NAME = "shopping_item_status_enum"

shopping_list_status_type = ENUM(
    ShoppingListStatusEnum.DRAFT,
    ShoppingListStatusEnum.SHOPPING,
    ShoppingListStatusEnum.ARCHIVED,
    name=SHOPPING_LIST_STATUS_ENUM_NAME,
    create_type=False,
)

shopping_item_status_type = ENUM(
    ShoppingItemStatusEnum.PENDING,
    ShoppingItemStatusEnum.BOUGHT,
    name=SHOPPING_ITEM_STATUS_ENUM_NAME,
    create_type=False,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
    )
    telegram_username: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    language_code: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str | None] = mapped_column(Text)
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    __table_args__ = (
        Index(
            "shopping_lists_one_current_per_owner_uidx",
            "owner_user_id",
            unique=True,
            postgresql_where=text("status in ('draft', 'shopping')"),
        ),
        Index(
            "shopping_lists_owner_status_created_idx",
            "owner_user_id",
            "status",
            text("created_at DESC"),
        ),
        Index(
            "shopping_lists_owner_archived_idx",
            "owner_user_id",
            text("archived_at DESC"),
            postgresql_where=text("status = 'archived'"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(shopping_list_status_type, nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    shopping_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index(
            "categories_one_default_uidx",
            "is_default",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name_ru: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1000"),
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class InputMessage(Base):
    __tablename__ = "input_messages"
    __table_args__ = (
        CheckConstraint(
            "parser_source in ('local', 'fallback')",
            name="input_messages_parser_source_check",
        ),
        UniqueConstraint(
            "telegram_chat_id",
            "telegram_message_id",
            name="input_messages_telegram_chat_message_uq",
        ),
        Index("input_messages_user_received_idx", "user_id", text("received_at DESC")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parser_source: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=ParserSourceEnum.LOCAL,
    )
    parser_version: Mapped[str | None] = mapped_column(Text)
    parser_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(display_text)) > 0",
            name="shopping_items_display_text_not_blank_check",
        ),
        CheckConstraint(
            "length(btrim(product_key)) > 0",
            name="shopping_items_product_key_not_blank_check",
        ),
        CheckConstraint(
            "("
            "status = 'pending' and bought_at is null and bought_by_user_id is null"
            ") or ("
            "status = 'bought' "
            "and bought_at is not null "
            "and bought_by_user_id is not null"
            ")",
            name="shopping_items_status_bought_fields_check",
        ),
        Index(
            "shopping_items_list_category_position_idx",
            "list_id",
            "category_id",
            "position",
        ),
        Index("shopping_items_list_status_idx", "list_id", "status"),
        Index("shopping_items_source_input_message_id_idx", "source_input_message_id"),
        Index("shopping_items_restored_from_item_id_idx", "restored_from_item_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    list_id: Mapped[int] = mapped_column(
        ForeignKey("shopping_lists.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    source_input_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("input_messages.id"),
    )
    restored_from_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("shopping_items.id"),
    )
    display_text: Mapped[str] = mapped_column(Text, nullable=False)
    product_key: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )
    quantity_amount: Mapped[Decimal | None] = mapped_column(Numeric)
    quantity_unit: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        shopping_item_status_type,
        nullable=False,
        server_default=text(f"'{ShoppingItemStatusEnum.PENDING}'"),
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    bought_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bought_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
