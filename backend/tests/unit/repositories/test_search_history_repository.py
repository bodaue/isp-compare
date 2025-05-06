import uuid

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.search_history import SearchHistory
from isp_compare.models.user import User
from isp_compare.repositories.search_history import SearchHistoryRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def search_history_repository(session: AsyncSession) -> SearchHistoryRepository:
    return SearchHistoryRepository(session=session)


@pytest.fixture
async def test_user(session: AsyncSession, faker: Faker) -> User:
    user = User(
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=faker.boolean(),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def test_search_history(
    session: AsyncSession, test_user: User, faker: Faker
) -> SearchHistory:
    search_history = SearchHistory(
        user_id=test_user.id,
        search_params={
            "min_price": str(
                faker.pydecimal(min_value=10, max_value=50, right_digits=2)
            ),
            "max_price": str(
                faker.pydecimal(min_value=51, max_value=100, right_digits=2)
            ),
            "min_speed": faker.pyint(min_value=50, max_value=100),
            "connection_type": "FTTH",
            "has_tv": faker.pybool(),
        },
    )
    session.add(search_history)
    await session.commit()
    return search_history


@pytest.fixture
async def test_search_histories(
    session: AsyncSession, test_user: User, faker: Faker
) -> list[SearchHistory]:
    search_histories = []

    for _ in range(3):
        search_history = SearchHistory(
            user_id=test_user.id,
            search_params={
                "min_price": str(
                    faker.pydecimal(min_value=10, max_value=50, right_digits=2)
                ),
                "max_price": str(
                    faker.pydecimal(min_value=51, max_value=100, right_digits=2)
                ),
                "min_speed": faker.pyint(min_value=50, max_value=100),
                "connection_type": faker.random_element(["FTTH", "ADSL", "ETHERNET"]),
                "has_tv": faker.pybool(),
            },
        )
        search_histories.append(search_history)
        session.add(search_history)

    await session.commit()
    return search_histories


async def test_create(
    session: AsyncSession,
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    faker: Faker,
) -> None:
    search_params = {
        "min_price": str(faker.pydecimal(min_value=10, max_value=50, right_digits=2)),
        "max_price": str(faker.pydecimal(min_value=51, max_value=100, right_digits=2)),
        "min_speed": faker.pyint(min_value=50, max_value=100),
        "connection_type": "FTTH",
    }

    search_history = SearchHistory(
        user_id=test_user.id,
        search_params=search_params,
    )

    await search_history_repository.create(search_history)
    await session.flush()

    stmt = select(SearchHistory).where(SearchHistory.id == search_history.id)
    result = await session.execute(stmt)
    saved_search_history = result.scalar_one()

    assert saved_search_history.id == search_history.id
    assert saved_search_history.user_id == test_user.id
    assert saved_search_history.search_params == search_params


async def test_get_by_id(
    search_history_repository: SearchHistoryRepository,
    test_search_history: SearchHistory,
) -> None:
    result = await search_history_repository.get_by_id(test_search_history.id)

    assert result is not None
    assert result.id == test_search_history.id
    assert result.user_id == test_search_history.user_id
    assert result.search_params == test_search_history.search_params


async def test_get_by_id_for_update(
    search_history_repository: SearchHistoryRepository,
    test_search_history: SearchHistory,
) -> None:
    result = await search_history_repository.get_by_id(
        test_search_history.id, for_update=True
    )

    assert result is not None
    assert result.id == test_search_history.id
    assert result.user_id == test_search_history.user_id


async def test_get_by_id_not_found(
    search_history_repository: SearchHistoryRepository,
) -> None:
    non_existent_id = uuid.uuid4()
    result = await search_history_repository.get_by_id(non_existent_id)

    assert result is None


async def test_get_by_user(
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    test_search_histories: list[SearchHistory],
) -> None:
    limit = 10
    offset = 0
    result = await search_history_repository.get_by_user(test_user.id, limit, offset)

    assert len(result) == len(test_search_histories)

    for search_history in result:
        assert search_history.user_id == test_user.id


async def test_get_by_user_with_limit(
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    test_search_histories: list[SearchHistory],
) -> None:
    limit = 2
    offset = 0
    result = await search_history_repository.get_by_user(test_user.id, limit, offset)

    assert len(result) == limit

    for search_history in result:
        assert search_history.user_id == test_user.id


async def test_get_by_user_with_offset(
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    test_search_histories: list[SearchHistory],
) -> None:
    limit = 10
    offset = 1
    result = await search_history_repository.get_by_user(test_user.id, limit, offset)

    assert len(result) == len(test_search_histories) - offset

    for search_history in result:
        assert search_history.user_id == test_user.id


async def test_get_by_user_ordered_by_date(
    session: AsyncSession,
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    faker: Faker,
) -> None:
    search_histories = []

    for i in range(3):
        search_history = SearchHistory(
            user_id=test_user.id,
            search_params={"param": f"value_{i}"},
        )
        search_histories.append(search_history)
        session.add(search_history)
        await session.flush()

    await session.commit()

    result = await search_history_repository.get_by_user(test_user.id, 10, 0)

    assert len(result) == 3

    for i in range(1, len(result)):
        assert result[i - 1].created_at >= result[i].created_at


async def test_delete(
    session: AsyncSession,
    search_history_repository: SearchHistoryRepository,
    test_search_history: SearchHistory,
) -> None:
    await search_history_repository.delete(test_search_history)
    await session.commit()

    stmt = select(SearchHistory).where(SearchHistory.id == test_search_history.id)
    result = await session.execute(stmt)
    deleted_search_history = result.scalar_one_or_none()

    assert deleted_search_history is None


async def test_delete_all_for_user(
    session: AsyncSession,
    search_history_repository: SearchHistoryRepository,
    test_user: User,
    test_search_histories: list[SearchHistory],
) -> None:
    other_user = User(
        fullname=Faker().name(),
        username=Faker().user_name(),
        hashed_password=Faker().sha256(),
        email=Faker().email(),
    )
    session.add(other_user)
    await session.flush()

    other_search_history = SearchHistory(
        user_id=other_user.id,
        search_params={"param": "value"},
    )
    session.add(other_search_history)
    await session.commit()

    await search_history_repository.delete_all_for_user(test_user.id)
    await session.commit()

    stmt = select(SearchHistory).where(SearchHistory.user_id == test_user.id)
    result = await session.execute(stmt)
    remaining_histories = list(result.scalars())

    assert len(remaining_histories) == 0

    stmt = select(SearchHistory).where(SearchHistory.user_id == other_user.id)
    result = await session.execute(stmt)
    other_user_histories = list(result.scalars())

    assert len(other_user_histories) == 1
    assert other_user_histories[0].id == other_search_history.id
