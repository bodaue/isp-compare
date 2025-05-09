import uuid
from unittest.mock import AsyncMock

import pytest
from faker import Faker

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    AppException,
    ProviderNotFoundException,
    TariffNotFoundException,
)
from isp_compare.models import Provider, User
from isp_compare.models.tariff import Tariff
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.search_history import SearchHistoryRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff import (
    TariffCreate,
    TariffResponse,
    TariffSearchParams,
    TariffUpdate,
)
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.tariff import TariffService
from isp_compare.services.transaction_manager import TransactionManager


@pytest.fixture
def tariff_repository_mock() -> AsyncMock:
    return AsyncMock(spec=TariffRepository)


@pytest.fixture
def provider_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ProviderRepository)


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
def tariff_service(
    tariff_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
) -> TariffService:
    return TariffService(
        tariff_repository=tariff_repository_mock,
        provider_repository=provider_repository_mock,
        search_history_repository=search_history_repository_mock,
        transaction_manager=transaction_manager_mock,
        identity_provider=identity_provider_mock,
    )


@pytest.fixture
def mock_provider() -> Provider:
    return Provider(
        id=uuid.uuid4(),
        name="Test Provider",
        description="Test Description",
        website="https://example.com",
        logo_url="https://example.com/logo.png",
        rating=4.5,
    )


@pytest.fixture
def mock_tariff(mock_provider: Provider) -> Tariff:
    return Tariff(
        id=uuid.uuid4(),
        provider_id=mock_provider.id,
        name="Test Tariff",
        description="Test Description",
        price=29.99,
        speed=100,
        has_tv=True,
        has_phone=False,
        connection_cost=10.00,
        promo_price=19.99,
        promo_period=3,
        is_active=True,
    )


@pytest.fixture
def mock_user(faker: Faker) -> User:
    return User(
        id=uuid.uuid4(),
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
    )


async def test_create_tariff_success(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    provider_id = uuid.uuid4()
    tariff_data = TariffCreate(
        name="New Tariff",
        description="New Description",
        price=39.99,
        speed=200,
        has_tv=True,
        has_phone=False,
        connection_cost=15.00,
        promo_price=29.99,
        promo_period=3,
        is_active=True,
    )

    provider_repository_mock.get_by_id.return_value = mock_provider

    async def create_side_effect(tariff: Tariff) -> None:
        tariff.id = uuid.uuid4()

    tariff_repository_mock.create.side_effect = create_side_effect

    result = await tariff_service.create_tariff(provider_id, tariff_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)
    tariff_repository_mock.create.assert_called_once()
    transaction_manager_mock.commit.assert_called_once()

    assert isinstance(result, TariffResponse)
    assert result.name == tariff_data.name
    assert result.description == tariff_data.description
    assert result.price == tariff_data.price
    assert result.speed == tariff_data.speed
    assert result.has_tv == tariff_data.has_tv
    assert result.has_phone == tariff_data.has_phone
    assert result.promo_price == tariff_data.promo_price
    assert result.promo_period == tariff_data.promo_period
    assert result.provider_id == provider_id
    assert result.id is not None


async def test_create_tariff_not_admin(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    tariff_data = TariffCreate(
        name="New Tariff",
        price=39.99,
        speed=200,
    )

    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await tariff_service.create_tariff(provider_id, tariff_data)

    provider_repository_mock.get_by_id.assert_not_called()


async def test_create_tariff_provider_not_found(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    tariff_data = TariffCreate(
        name="New Tariff",
        price=39.99,
        speed=200,
    )

    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await tariff_service.create_tariff(provider_id, tariff_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)


async def test_get_tariff_success(
    tariff_service: TariffService,
    tariff_repository_mock: AsyncMock,
    mock_tariff: Tariff,
) -> None:
    tariff_id = uuid.uuid4()
    tariff_repository_mock.get_by_id.return_value = mock_tariff

    result = await tariff_service.get_tariff(tariff_id)

    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id)
    assert isinstance(result, TariffResponse)
    assert result.id == mock_tariff.id
    assert result.name == mock_tariff.name
    assert result.description == mock_tariff.description
    assert float(result.price) == mock_tariff.price
    assert result.speed == mock_tariff.speed


async def test_get_tariff_not_found(
    tariff_service: TariffService,
    tariff_repository_mock: AsyncMock,
) -> None:
    tariff_id = uuid.uuid4()
    tariff_repository_mock.get_by_id.return_value = None

    with pytest.raises(TariffNotFoundException):
        await tariff_service.get_tariff(tariff_id)

    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id)


async def test_get_all_tariffs(
    tariff_service: TariffService,
    tariff_repository_mock: AsyncMock,
    mock_tariff: Tariff,
) -> None:
    limit = 10
    offset = 0
    tariffs = [mock_tariff, mock_tariff, mock_tariff]
    tariff_repository_mock.get_all.return_value = tariffs

    result = await tariff_service.get_all_tariffs(limit, offset)

    tariff_repository_mock.get_all.assert_called_once_with(limit, offset)
    assert len(result) == len(tariffs)
    for tariff_response in result:
        assert isinstance(tariff_response, TariffResponse)
        assert tariff_response.id == mock_tariff.id
        assert tariff_response.name == mock_tariff.name


async def test_get_provider_tariffs_success(
    tariff_service: TariffService,
    provider_repository_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
    mock_provider: Provider,
    mock_tariff: Tariff,
) -> None:
    provider_id = uuid.uuid4()
    limit = 10
    offset = 0
    tariffs = [mock_tariff, mock_tariff]

    provider_repository_mock.get_by_id.return_value = mock_provider
    tariff_repository_mock.get_by_provider.return_value = tariffs

    result = await tariff_service.get_provider_tariffs(provider_id, limit, offset)

    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)
    tariff_repository_mock.get_by_provider.assert_called_once_with(
        provider_id, limit, offset
    )
    assert len(result) == len(tariffs)
    for tariff_response in result:
        assert isinstance(tariff_response, TariffResponse)


async def test_get_provider_tariffs_provider_not_found(
    tariff_service: TariffService,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    limit = 10
    offset = 0

    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await tariff_service.get_provider_tariffs(provider_id, limit, offset)

    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)


async def test_update_tariff_success(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_tariff: Tariff,
) -> None:
    tariff_id = uuid.uuid4()
    update_data = TariffUpdate(
        name="Updated Tariff",
        description="Updated Description",
        price=49.99,
        speed=300,
    )

    tariff_repository_mock.get_by_id.return_value = mock_tariff

    result = await tariff_service.update_tariff(tariff_id, update_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id, for_update=True)
    tariff_repository_mock.update.assert_called_once_with(
        tariff_id, update_data.model_dump(exclude_unset=True)
    )
    transaction_manager_mock.commit.assert_called_once()
    transaction_manager_mock.refresh.assert_called_once_with(mock_tariff)

    assert isinstance(result, TariffResponse)
    assert result.id == mock_tariff.id
    assert result.name == mock_tariff.name


async def test_update_tariff_not_found(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
) -> None:
    tariff_id = uuid.uuid4()
    update_data = TariffUpdate(name="Updated Tariff")

    tariff_repository_mock.get_by_id.return_value = None

    with pytest.raises(TariffNotFoundException):
        await tariff_service.update_tariff(tariff_id, update_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id, for_update=True)
    tariff_repository_mock.update.assert_not_called()


async def test_update_tariff_not_admin(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
) -> None:
    tariff_id = uuid.uuid4()
    update_data = TariffUpdate(name="Updated Tariff")

    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await tariff_service.update_tariff(tariff_id, update_data)

    tariff_repository_mock.get_by_id.assert_not_called()
    tariff_repository_mock.update.assert_not_called()


async def test_delete_tariff_success(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_tariff: Tariff,
) -> None:
    tariff_id = uuid.uuid4()
    tariff_repository_mock.get_by_id.return_value = mock_tariff

    await tariff_service.delete_tariff(tariff_id)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id, for_update=True)
    tariff_repository_mock.delete.assert_called_once_with(mock_tariff)
    transaction_manager_mock.commit.assert_called_once()


async def test_delete_tariff_not_found(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
) -> None:
    tariff_id = uuid.uuid4()
    tariff_repository_mock.get_by_id.return_value = None

    with pytest.raises(TariffNotFoundException):
        await tariff_service.delete_tariff(tariff_id)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    tariff_repository_mock.get_by_id.assert_called_once_with(tariff_id, for_update=True)
    tariff_repository_mock.delete.assert_not_called()


async def test_delete_tariff_not_admin(
    tariff_service: TariffService,
    identity_provider_mock: AsyncMock,
    tariff_repository_mock: AsyncMock,
) -> None:
    tariff_id = uuid.uuid4()
    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await tariff_service.delete_tariff(tariff_id)

    tariff_repository_mock.get_by_id.assert_not_called()
    tariff_repository_mock.delete.assert_not_called()


async def test_search_tariffs_authenticated_user(
    tariff_service: TariffService,
    tariff_repository_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
    mock_tariff: Tariff,
    mock_user: User,
) -> None:
    search_params = TariffSearchParams(
        min_price=20.0,
        max_price=50.0,
        min_speed=100,
        has_tv=True,
        limit=10,
        offset=0,
    )
    tariffs = [mock_tariff, mock_tariff]
    tariff_repository_mock.search.return_value = tariffs
    identity_provider_mock.get_current_user.return_value = mock_user

    result = await tariff_service.search_tariffs(search_params)

    tariff_repository_mock.search.assert_called_once_with(
        min_price=search_params.min_price,
        max_price=search_params.max_price,
        min_speed=search_params.min_speed,
        max_speed=search_params.max_speed,
        has_tv=search_params.has_tv,
        has_phone=search_params.has_phone,
        limit=search_params.limit,
        offset=search_params.offset,
    )
    identity_provider_mock.get_current_user.assert_called_once()
    search_history_repository_mock.create.assert_called_once()
    transaction_manager_mock.commit.assert_called_once()

    assert len(result) == len(tariffs)
    for tariff_response in result:
        assert isinstance(tariff_response, TariffResponse)


async def test_search_tariffs_unauthenticated_user(
    tariff_service: TariffService,
    tariff_repository_mock: AsyncMock,
    search_history_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
    mock_tariff: Tariff,
) -> None:
    search_params = TariffSearchParams(
        min_speed=50,
        has_tv=False,
        limit=5,
        offset=0,
    )

    tariffs = [mock_tariff]
    tariff_repository_mock.search.return_value = tariffs
    identity_provider_mock.get_current_user.side_effect = AppException(
        status_code=401, detail="Unauthorized"
    )

    result = await tariff_service.search_tariffs(search_params)

    tariff_repository_mock.search.assert_called_once_with(
        min_price=None,
        max_price=None,
        min_speed=search_params.min_speed,
        max_speed=None,
        has_tv=search_params.has_tv,
        has_phone=None,
        limit=search_params.limit,
        offset=search_params.offset,
    )

    identity_provider_mock.get_current_user.assert_called_once()
    search_history_repository_mock.create.assert_not_called()
    transaction_manager_mock.commit.assert_not_called()

    assert len(result) == len(tariffs)
    for tariff_response in result:
        assert isinstance(tariff_response, TariffResponse)
