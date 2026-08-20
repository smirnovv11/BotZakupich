import pytest
from app.infrastructure.db.models import User
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from sqlalchemy import select


@pytest.mark.asyncio
async def test_unit_of_work_commits_successful_writes(db_session_factory) -> None:
    async with SqlAlchemyUnitOfWork(db_session_factory) as uow:
        await uow.users.create_or_update_from_telegram(telegram_user_id=4001)

    async with db_session_factory() as session:
        user = await session.scalar(
            select(User).where(User.telegram_user_id == 4001),
        )

    assert user is not None


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_on_exception(db_session_factory) -> None:
    with pytest.raises(RuntimeError):
        async with SqlAlchemyUnitOfWork(db_session_factory) as uow:
            await uow.users.create_or_update_from_telegram(telegram_user_id=4002)
            raise RuntimeError("boom")

    async with db_session_factory() as session:
        user = await session.scalar(
            select(User).where(User.telegram_user_id == 4002),
        )

    assert user is None


@pytest.mark.asyncio
async def test_repositories_do_not_commit_independently(db_session_factory) -> None:
    async with SqlAlchemyUnitOfWork(db_session_factory) as uow:
        await uow.users.create_or_update_from_telegram(telegram_user_id=4003)
        await uow.rollback()

    async with db_session_factory() as session:
        user = await session.scalar(
            select(User).where(User.telegram_user_id == 4003),
        )

    assert user is None
