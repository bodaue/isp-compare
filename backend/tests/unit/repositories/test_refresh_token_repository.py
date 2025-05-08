import uuid
from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.token import RefreshToken
from isp_compare.models.user import User
from isp_compare.repositories.token import RefreshTokenRepository


@pytest.fixture
async def refresh_token_repository(session: AsyncSession) -> RefreshTokenRepository:
    return RefreshTokenRepository(session=session)


@pytest.fixture
async def test_refresh_token(
    session: AsyncSession, regular_user: User, faker: Faker
) -> RefreshToken:
    token = RefreshToken(
        token=faker.uuid4(),
        user_id=regular_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked=False,
    )
    session.add(token)
    await session.commit()
    return token


@pytest.fixture
async def test_refresh_tokens(
    session: AsyncSession, regular_user: User, faker: Faker
) -> list[RefreshToken]:
    tokens = []
    for _ in range(3):
        token = RefreshToken(
            token=faker.uuid4(),
            user_id=regular_user.id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            revoked=False,
        )
        tokens.append(token)
        session.add(token)

    await session.commit()
    return tokens


async def test_create(
    session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
    regular_user: User,
    faker: Faker,
) -> None:
    token_value = faker.uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=7)

    token = RefreshToken(
        token=token_value,
        user_id=regular_user.id,
        expires_at=expires_at,
        revoked=False,
    )

    await refresh_token_repository.create(token)
    await session.flush()

    stmt = select(RefreshToken).where(RefreshToken.id == token.id)
    result = await session.execute(stmt)
    saved_token = result.scalar_one()

    assert saved_token.id == token.id
    assert saved_token.token == token_value
    assert saved_token.user_id == regular_user.id
    assert saved_token.expires_at == expires_at
    assert saved_token.revoked is False


async def test_get_by_token(
    refresh_token_repository: RefreshTokenRepository, test_refresh_token: RefreshToken
) -> None:
    result = await refresh_token_repository.get_by_token(test_refresh_token.token)

    assert result is not None
    assert result.id == test_refresh_token.id
    assert result.token == test_refresh_token.token
    assert result.user_id == test_refresh_token.user_id


async def test_get_by_token_not_found(
    refresh_token_repository: RefreshTokenRepository, faker: Faker
) -> None:
    non_existent_token = faker.uuid4()
    result = await refresh_token_repository.get_by_token(non_existent_token)

    assert result is None


async def test_get_by_user_id(
    refresh_token_repository: RefreshTokenRepository,
    regular_user: User,
    test_refresh_tokens: list[RefreshToken],
) -> None:
    result = await refresh_token_repository.get_by_user_id(regular_user.id)

    assert len(result) == len(test_refresh_tokens)

    for token in result:
        assert token.user_id == regular_user.id


async def test_get_by_user_id_not_found(
    refresh_token_repository: RefreshTokenRepository,
) -> None:
    non_existent_user_id = uuid.uuid4()
    result = await refresh_token_repository.get_by_user_id(non_existent_user_id)

    assert len(result) == 0


async def test_revoke(
    session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
    test_refresh_token: RefreshToken,
) -> None:
    await refresh_token_repository.revoke(test_refresh_token.token)
    await session.commit()

    stmt = select(RefreshToken).where(RefreshToken.id == test_refresh_token.id)
    result = await session.execute(stmt)
    revoked_token = result.scalar_one()

    assert revoked_token.revoked is True
    assert revoked_token.revoked_at is not None


async def test_revoke_all_for_user(
    session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
    regular_user: User,
    test_refresh_tokens: list[RefreshToken],
) -> None:
    other_user = User(
        fullname=Faker().name(),
        username=Faker().user_name(),
        hashed_password=Faker().sha256(),
        email=Faker().email(),
    )
    session.add(other_user)
    await session.flush()

    other_token = RefreshToken(
        token=Faker().uuid4(),
        user_id=other_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked=False,
    )
    session.add(other_token)
    await session.commit()

    await refresh_token_repository.revoke_all_for_user(regular_user.id)
    await session.commit()

    stmt = select(RefreshToken).where(RefreshToken.user_id == regular_user.id)
    result = await session.execute(stmt)
    user_tokens = list(result.scalars())

    assert all(token.revoked for token in user_tokens)
    assert all(token.revoked_at is not None for token in user_tokens)

    stmt = select(RefreshToken).where(RefreshToken.user_id == other_user.id)
    result = await session.execute(stmt)
    other_user_token = result.scalar_one()

    assert other_user_token.revoked is False
    assert other_user_token.revoked_at is None


async def test_delete_expired(
    session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
    regular_user: User,
    faker: Faker,
) -> None:
    expired_tokens = []
    for _ in range(2):
        token = RefreshToken(
            token=faker.uuid4(),
            user_id=regular_user.id,
            expires_at=datetime.now(UTC) - timedelta(days=1),
            revoked=False,
        )
        expired_tokens.append(token)
        session.add(token)

    active_token = RefreshToken(
        token=faker.uuid4(),
        user_id=regular_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked=False,
    )
    session.add(active_token)
    await session.commit()

    await refresh_token_repository.delete_expired()
    await session.commit()

    for token in expired_tokens:
        stmt = select(RefreshToken).where(RefreshToken.id == token.id)
        result = await session.execute(stmt)
        deleted_token = result.scalar_one_or_none()
        assert deleted_token is None

    stmt = select(RefreshToken).where(RefreshToken.id == active_token.id)
    result = await session.execute(stmt)
    not_deleted_token = result.scalar_one_or_none()
    assert not_deleted_token is not None
    assert not_deleted_token.id == active_token.id
