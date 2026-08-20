"""Initial MVP schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from migrations.utils import create_enum_type, drop_enum_type
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SHOPPING_LIST_STATUS_ENUM_NAME = "shopping_list_status_enum"
SHOPPING_LIST_STATUS_VALUES = ("draft", "shopping", "archived")
SHOPPING_ITEM_STATUS_ENUM_NAME = "shopping_item_status_enum"
SHOPPING_ITEM_STATUS_VALUES = ("pending", "bought")
PARSER_SOURCE_VALUES = ("local", "fallback")

shopping_list_status_enum = postgresql.ENUM(
    *SHOPPING_LIST_STATUS_VALUES,
    name=SHOPPING_LIST_STATUS_ENUM_NAME,
    create_type=False,
)
shopping_item_status_enum = postgresql.ENUM(
    *SHOPPING_ITEM_STATUS_VALUES,
    name=SHOPPING_ITEM_STATUS_ENUM_NAME,
    create_type=False,
)


def upgrade() -> None:
    create_enum_type(
        op,
        SHOPPING_LIST_STATUS_ENUM_NAME,
        SHOPPING_LIST_STATUS_VALUES,
    )
    create_enum_type(
        op,
        SHOPPING_ITEM_STATUS_ENUM_NAME,
        SHOPPING_ITEM_STATUS_VALUES,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("language_code", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=True),
        sa.Column(
            "is_blocked",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("telegram_user_id", name="users_telegram_user_id_key"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name_ru", sa.Text(), nullable=False),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default=sa.text("1000"),
            nullable=False,
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("code", name="categories_code_key"),
        sa.UniqueConstraint("name_ru", name="categories_name_ru_key"),
    )

    op.create_table(
        "shopping_lists",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", shopping_list_status_enum, nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("shopping_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["archived_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )

    op.create_table(
        "input_messages",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parser_source", sa.Text(), nullable=False),
        sa.Column("parser_version", sa.Text(), nullable=True),
        sa.Column("parser_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "parser_source in ('local', 'fallback')",
            name="input_messages_parser_source_check",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint(
            "telegram_chat_id",
            "telegram_message_id",
            name="input_messages_telegram_chat_message_uq",
        ),
    )

    op.create_table(
        "shopping_items",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("list_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("source_input_message_id", sa.BigInteger(), nullable=True),
        sa.Column("restored_from_item_id", sa.BigInteger(), nullable=True),
        sa.Column("display_text", sa.Text(), nullable=False),
        sa.Column("product_key", sa.Text(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity_amount", sa.Numeric(), nullable=True),
        sa.Column("quantity_unit", sa.Text(), nullable=True),
        sa.Column(
            "status",
            shopping_item_status_enum,
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("bought_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bought_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(btrim(display_text)) > 0",
            name="shopping_items_display_text_not_blank_check",
        ),
        sa.CheckConstraint(
            "length(btrim(product_key)) > 0",
            name="shopping_items_product_key_not_blank_check",
        ),
        sa.CheckConstraint(
            "("
            "status = 'pending' and bought_at is null and bought_by_user_id is null"
            ") or ("
            "status = 'bought' "
            "and bought_at is not null "
            "and bought_by_user_id is not null"
            ")",
            name="shopping_items_status_bought_fields_check",
        ),
        sa.ForeignKeyConstraint(["bought_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["list_id"], ["shopping_lists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["restored_from_item_id"], ["shopping_items.id"]),
        sa.ForeignKeyConstraint(["source_input_message_id"], ["input_messages.id"]),
    )

    op.create_index(
        "categories_one_default_uidx",
        "categories",
        ["is_default"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )
    op.create_index(
        "shopping_lists_one_current_per_owner_uidx",
        "shopping_lists",
        ["owner_user_id"],
        unique=True,
        postgresql_where=sa.text("status in ('draft', 'shopping')"),
    )
    op.create_index(
        "shopping_lists_owner_status_created_idx",
        "shopping_lists",
        ["owner_user_id", "status", sa.text("created_at DESC")],
    )
    op.create_index(
        "shopping_lists_owner_archived_idx",
        "shopping_lists",
        ["owner_user_id", sa.text("archived_at DESC")],
        postgresql_where=sa.text("status = 'archived'"),
    )
    op.create_index(
        "input_messages_user_received_idx",
        "input_messages",
        ["user_id", sa.text("received_at DESC")],
    )
    op.create_index(
        "shopping_items_list_category_position_idx",
        "shopping_items",
        ["list_id", "category_id", "position"],
    )
    op.create_index(
        "shopping_items_list_status_idx",
        "shopping_items",
        ["list_id", "status"],
    )
    op.create_index(
        "shopping_items_source_input_message_id_idx",
        "shopping_items",
        ["source_input_message_id"],
    )
    op.create_index(
        "shopping_items_restored_from_item_id_idx",
        "shopping_items",
        ["restored_from_item_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "shopping_items_restored_from_item_id_idx",
        table_name="shopping_items",
    )
    op.drop_index(
        "shopping_items_source_input_message_id_idx",
        table_name="shopping_items",
    )
    op.drop_index("shopping_items_list_status_idx", table_name="shopping_items")
    op.drop_index(
        "shopping_items_list_category_position_idx",
        table_name="shopping_items",
    )
    op.drop_index("input_messages_user_received_idx", table_name="input_messages")
    op.drop_index("shopping_lists_owner_archived_idx", table_name="shopping_lists")
    op.drop_index(
        "shopping_lists_owner_status_created_idx",
        table_name="shopping_lists",
    )
    op.drop_index(
        "shopping_lists_one_current_per_owner_uidx",
        table_name="shopping_lists",
    )
    op.drop_index("categories_one_default_uidx", table_name="categories")

    op.drop_table("shopping_items")
    op.drop_table("input_messages")
    op.drop_table("shopping_lists")
    op.drop_table("categories")
    op.drop_table("users")

    drop_enum_type(op, SHOPPING_ITEM_STATUS_ENUM_NAME, SHOPPING_ITEM_STATUS_VALUES)
    drop_enum_type(op, SHOPPING_LIST_STATUS_ENUM_NAME, SHOPPING_LIST_STATUS_VALUES)
