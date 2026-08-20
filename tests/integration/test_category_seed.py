import pytest
from app.domain.enums import CategoryCodeEnum
from app.infrastructure.db.models import Category
from app.infrastructure.db.seeds import seed_categories
from sqlalchemy import delete, func, select, update


async def category_count(db_session) -> int:
    return await db_session.scalar(select(func.count()).select_from(Category))


@pytest.mark.asyncio
async def test_seed_categories_is_idempotent(db_session) -> None:
    await db_session.execute(delete(Category))
    await db_session.commit()

    await seed_categories(db_session)
    await db_session.commit()

    assert await category_count(db_session) == 19
    await db_session.commit()

    await seed_categories(db_session)
    await db_session.commit()

    assert await category_count(db_session) == 19


@pytest.mark.asyncio
async def test_seed_categories_creates_single_default_other_category(
    db_session,
) -> None:
    await seed_categories(db_session)
    await db_session.commit()

    default_categories = (
        (
            await db_session.execute(
                select(Category).where(Category.is_default.is_(True))
            )
        )
        .scalars()
        .all()
    )

    assert len(default_categories) == 1
    assert default_categories[0].code == CategoryCodeEnum.OTHER
    assert default_categories[0].name_ru == "Прочие"


@pytest.mark.asyncio
async def test_seed_categories_restores_canonical_existing_values(db_session) -> None:
    await seed_categories(db_session)
    await db_session.commit()

    await db_session.execute(
        update(Category)
        .where(Category.code == CategoryCodeEnum.OTHER)
        .values(name_ru="Другое", sort_order=1, is_default=False),
    )
    await db_session.commit()

    await db_session.execute(
        update(Category)
        .where(Category.code == CategoryCodeEnum.DAIRY)
        .values(is_default=True),
    )
    await db_session.commit()

    await seed_categories(db_session)
    await db_session.commit()

    other_category = await db_session.scalar(
        select(Category).where(Category.code == CategoryCodeEnum.OTHER),
    )
    default_count = await db_session.scalar(
        select(func.count()).select_from(Category).where(Category.is_default.is_(True)),
    )

    assert other_category is not None
    assert other_category.name_ru == "Прочие"
    assert other_category.sort_order == 1000
    assert other_category.is_default is True
    assert default_count == 1
