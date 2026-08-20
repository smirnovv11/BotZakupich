"""Reusable helpers for Alembic migrations."""

from collections.abc import Sequence

from alembic.operations import Operations
from sqlalchemy.dialects import postgresql


def create_enum_type(op: Operations, name: str, values: Sequence[str]) -> None:
    enum_type = postgresql.ENUM(*values, name=name, create_type=False)
    enum_type.create(op.get_bind(), checkfirst=False)


def drop_enum_type(op: Operations, name: str, values: Sequence[str]) -> None:
    enum_type = postgresql.ENUM(*values, name=name, create_type=False)
    enum_type.drop(op.get_bind(), checkfirst=False)
