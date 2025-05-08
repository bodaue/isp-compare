import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker

from isp_compare.core.exceptions import SearchHistoryNotFoundException
from isp_compare.models import User
from isp_compare.models.search_history import SearchHistory
from isp_compare.repositories.search_history import SearchHistoryRepository
from isp_compare.schemas.search_history import SearchHistoryResponse
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.search_history import SearchHistoryService
from isp_compare.services.transaction_manager import TransactionManager


@pytest.fixture
def search_history_repository_mock() -> AsyncMock:
    return AsyncMock(spec=SearchHistoryRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def identity_provider_mock() -> AsyncMock:
    return AsyncMock(spec=IdentityProvider)


@pytest.fixture
def search_history_service(
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
) -> SearchHistoryService:
    return SearchHistoryService(
        search_history_repository=search_history_repository_mock,
        transaction_manager=transaction_manager_mock,
        identity_provider=identity_provider_mock,
    )


@pytest.fixture
def mock_user(faker: Faker) -> User:
    return User(
        id=uuid.uuid4(),
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=False,
    )


@pytest.fixture
def mock_search_history(mock_user: User, faker: Faker) -> SearchHistory:
    return SearchHistory(
        id=uuid.uuid4(),
        user_id=mock_user.id,
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
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_search_histories(mock_user: User, faker: Faker) -> list[SearchHistory]:
    histories = []
    for _ in range(3):
        history = SearchHistory(
            id=uuid.uuid4(),
            user_id=mock_user.id,
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
            created_at=datetime.now(UTC),
        )
        histories.append(history)
    return histories


async def test_get_user_search_history_success(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
    mock_search_histories: list[SearchHistory],
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_user.return_value = mock_search_histories

    limit = 10
    offset = 0
    result = await search_history_service.get_user_search_history(limit, offset)

    identity_provider_mock.get_current_user.assert_called_once()
    search_history_repository_mock.get_by_user.assert_called_once_with(
        mock_user.id, limit, offset
    )

    assert len(result) == len(mock_search_histories)
    for history_response in result:
        assert isinstance(history_response, SearchHistoryResponse)


async def test_get_user_search_history_empty(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_user.return_value = []

    limit = 10
    offset = 0
    result = await search_history_service.get_user_search_history(limit, offset)

    assert len(result) == 0


async def test_get_user_search_history_with_pagination(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
    mock_search_histories: list[SearchHistory],
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    search_history_repository_mock.get_by_user.return_value = mock_search_histories[:2]

    limit = 2
    offset = 0
    result = await search_history_service.get_user_search_history(limit, offset)

    search_history_repository_mock.get_by_user.assert_called_once_with(
        mock_user.id, limit, offset
    )
    assert len(result) == 2


async def test_delete_search_history_success(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
    mock_search_history: SearchHistory,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_id.return_value = mock_search_history

    await search_history_service.delete_search_history(mock_search_history.id)

    identity_provider_mock.get_current_user.assert_called_once()
    search_history_repository_mock.get_by_id.assert_called_once_with(
        search_history_id=mock_search_history.id,
        for_update=True,
    )
    search_history_repository_mock.delete.assert_called_once_with(mock_search_history)
    transaction_manager_mock.commit.assert_called_once()


async def test_delete_search_history_not_found(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    search_history_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_id.return_value = None

    with pytest.raises(SearchHistoryNotFoundException):
        await search_history_service.delete_search_history(search_history_id)

    search_history_repository_mock.get_by_id.assert_called_once_with(
        search_history_id=search_history_id,
        for_update=True,
    )
    search_history_repository_mock.delete.assert_not_called()


async def test_delete_search_history_wrong_user(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
    mock_search_history: SearchHistory,
) -> None:
    mock_search_history.user_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_id.return_value = mock_search_history

    with pytest.raises(SearchHistoryNotFoundException):
        await search_history_service.delete_search_history(mock_search_history.id)

    search_history_repository_mock.delete.assert_not_called()


async def test_clear_search_history_success(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    await search_history_service.clear_search_history()

    identity_provider_mock.get_current_user.assert_called_once()
    search_history_repository_mock.delete_all_for_user.assert_called_once_with(
        mock_user.id
    )
    transaction_manager_mock.commit.assert_called_once()


async def test_clear_search_history_no_history(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    await search_history_service.clear_search_history()

    search_history_repository_mock.delete_all_for_user.assert_called_once_with(
        mock_user.id
    )
    transaction_manager_mock.commit.assert_called_once()


async def test_delete_nonexistent_search_history(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    nonexistent_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_id.return_value = None

    with pytest.raises(SearchHistoryNotFoundException):
        await search_history_service.delete_search_history(nonexistent_id)

    search_history_repository_mock.delete.assert_not_called()


async def test_get_user_search_history_with_complex_params(
    search_history_service: SearchHistoryService,
    identity_provider_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    mock_user: User,
    faker: Faker,
) -> None:
    complex_search_history = SearchHistory(
        id=uuid.uuid4(),
        user_id=mock_user.id,
        search_params={
            "min_price": "25.50",
            "max_price": "100.00",
            "min_speed": 100,
            "max_speed": 1000,
            "connection_type": "FTTH",
            "has_tv": True,
            "has_phone": False,
            "limit": 50,
            "offset": 0,
        },
        created_at=datetime.now(UTC),
    )

    identity_provider_mock.get_current_user.return_value = mock_user
    search_history_repository_mock.get_by_user.return_value = [complex_search_history]

    result = await search_history_service.get_user_search_history(10, 0)

    assert len(result) == 1
    assert result[0].search_params == complex_search_history.search_params
