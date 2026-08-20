"""Database seed helpers."""

import asyncio

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.domain.categories import CATEGORY_DEFINITIONS, CategoryDefinition
from app.infrastructure.db.models import Category
from app.infrastructure.db.session import create_database


def validate_category_definitions(
    category_definitions: tuple[CategoryDefinition, ...] = CATEGORY_DEFINITIONS,
) -> None:
    default_categories = [
        category for category in category_definitions if category.is_default
    ]
    if len(default_categories) != 1:
        raise ValueError("category catalog must define exactly one default category")

    codes = [category.code for category in category_definitions]
    if len(codes) != len(set(codes)):
        raise ValueError("category catalog must not contain duplicate codes")

    names = [category.name_ru for category in category_definitions]
    if len(names) != len(set(names)):
        raise ValueError("category catalog must not contain duplicate Russian names")


async def seed_categories(
    session: AsyncSession,
    category_definitions: tuple[CategoryDefinition, ...] = CATEGORY_DEFINITIONS,
) -> None:
    validate_category_definitions(category_definitions)

    await session.execute(update(Category).values(is_default=False))

    for category in category_definitions:
        statement = (
            insert(Category)
            .values(
                code=category.code,
                name_ru=category.name_ru,
                sort_order=category.sort_order,
                is_default=category.is_default,
            )
            .on_conflict_do_update(
                index_elements=[Category.code],
                set_={
                    "name_ru": category.name_ru,
                    "sort_order": category.sort_order,
                    "is_default": category.is_default,
                },
            )
        )
        await session.execute(statement)


async def seed_database_from_settings() -> None:
    database = create_database(Settings())
    try:
        async with database.session_factory() as session:
            await seed_categories(session)
            await session.commit()
    finally:
        await database.engine.dispose()


def main() -> None:
    asyncio.run(seed_database_from_settings())


if __name__ == "__main__":
    main()
