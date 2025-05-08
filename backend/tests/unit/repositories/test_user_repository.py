import uuid

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user import User
from isp_compare.repositories.user import UserRepository


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


async def test_create_user(
    session: AsyncSession, user_repository: UserRepository, faker: Faker
) -> None:
    user = User(
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=faker.boolean(),
    )

    await user_repository.create(user)
    await session.flush()

    stmt = select(User).where(User.id == user.id)
    result = await session.execute(stmt)
    saved_user = result.scalar_one()

    assert saved_user.id == user.id
    assert saved_user.fullname == user.fullname
    assert saved_user.username == user.username
    assert saved_user.hashed_password == user.hashed_password
    assert saved_user.email == user.email
    assert saved_user.is_admin == user.is_admin


async def test_get_by_id(user_repository: UserRepository, regular_user: User) -> None:
    result = await user_repository.get_by_id(regular_user.id)

    assert result is not None
    assert result.id == regular_user.id
    assert result.fullname == regular_user.fullname
    assert result.username == regular_user.username


async def test_get_by_id_not_found(
    user_repository: UserRepository, regular_user: User
) -> None:
    non_existent_id = uuid.uuid4()
    result = await user_repository.get_by_id(non_existent_id)

    assert result is None


async def test_get_by_username(
    user_repository: UserRepository, regular_user: User
) -> None:
    result = await user_repository.get_by_username(regular_user.username)

    assert result is not None
    assert result.id == regular_user.id
    assert result.username == regular_user.username


async def test_get_by_username_not_found(
    user_repository: UserRepository, faker: Faker
) -> None:
    non_existent_username = f"non_existent_{faker.user_name()}"
    result = await user_repository.get_by_username(non_existent_username)

    assert result is None


async def test_get_by_email(
    user_repository: UserRepository, regular_user: User
) -> None:
    result = await user_repository.get_by_email(regular_user.email)

    assert result is not None
    assert result.id == regular_user.id
    assert result.email == regular_user.email


async def test_get_by_email_not_found(
    user_repository: UserRepository, faker: Faker
) -> None:
    non_existent_email = f"non_existent_{faker.email()}"
    result = await user_repository.get_by_email(non_existent_email)

    assert result is None


async def test_update_password(
    session: AsyncSession,
    user_repository: UserRepository,
    regular_user: User,
    faker: Faker,
) -> None:
    new_password = faker.sha256()
    await user_repository.update_password(regular_user.id, new_password)
    await session.commit()

    stmt = select(User).where(User.id == regular_user.id)
    result = await session.execute(stmt)
    updated_user = result.scalar_one()

    assert updated_user.hashed_password == new_password


async def test_update_profile(
    session: AsyncSession,
    user_repository: UserRepository,
    regular_user: User,
    faker: Faker,
) -> None:
    new_fullname = faker.name()
    new_username = faker.user_name()
    update_data = {"fullname": new_fullname, "username": new_username}

    await user_repository.update_profile(regular_user.id, update_data)
    await session.commit()

    stmt = select(User).where(User.id == regular_user.id)
    result = await session.execute(stmt)
    updated_user = result.scalar_one()

    assert updated_user.fullname == new_fullname
    assert updated_user.username == new_username
    assert updated_user.email == regular_user.email


async def test_update_profile_partial(
    session: AsyncSession,
    user_repository: UserRepository,
    regular_user: User,
    faker: Faker,
) -> None:
    new_fullname = faker.name()
    update_data = {"fullname": new_fullname}

    await user_repository.update_profile(regular_user.id, update_data)
    await session.commit()

    stmt = select(User).where(User.id == regular_user.id)
    result = await session.execute(stmt)
    updated_user = result.scalar_one()

    assert updated_user.fullname == new_fullname
    assert updated_user.username == regular_user.username
    assert updated_user.email == regular_user.email
