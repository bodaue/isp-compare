import uuid
from unittest.mock import AsyncMock

import pytest
from pydantic import HttpUrl

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    ProviderNotFoundException,
)
from isp_compare.models.provider import Provider
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.provider import ProviderService
from isp_compare.services.transaction_manager import TransactionManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def provider_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ProviderRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def identity_provider_mock() -> AsyncMock:
    return AsyncMock(spec=IdentityProvider)


@pytest.fixture
def provider_service(
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
) -> ProviderService:
    return ProviderService(
        provider_repository=provider_repository_mock,
        transaction_manager=transaction_manager_mock,
        identity_provider=identity_provider_mock,
    )


@pytest.fixture
def mock_provider() -> Provider:
    return Provider(
        id=uuid.uuid4(),
        name="Test Provider",
        description="Test Description",
        website="https://example.com/",
        logo_url="https://example.com/logo.png",
        rating=4.5,
    )


async def test_create_provider_success(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
) -> None:
    provider_data = ProviderCreate(
        name="Test Provider",
        description="Test Description",
        website=HttpUrl("https://example.com"),
        logo_url="https://example.com/logo.png",
    )

    async def create_side_effect(provider: Provider) -> None:
        provider.id = uuid.uuid4()

    provider_repository_mock.create.side_effect = create_side_effect

    result = await provider_service.create_provider(provider_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.create.assert_called_once()
    transaction_manager_mock.commit.assert_called_once()

    assert isinstance(result, ProviderResponse)
    assert result.name == provider_data.name
    assert result.description == provider_data.description
    assert str(result.website) == str(provider_data.website)
    assert result.logo_url == provider_data.logo_url
    assert result.id is not None


async def test_create_provider_not_admin(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_data = ProviderCreate(
        name="Test Provider",
        description="Test Description",
        website=HttpUrl("https://example.com"),
        logo_url="https://example.com/logo.png",
    )
    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await provider_service.create_provider(provider_data)

    provider_repository_mock.create.assert_not_called()


async def test_get_provider_success(
    provider_service: ProviderService,
    provider_repository_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = mock_provider

    result = await provider_service.get_provider(provider_id)

    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)
    assert isinstance(result, ProviderResponse)
    assert result.id == mock_provider.id
    assert result.name == mock_provider.name
    assert result.description == mock_provider.description
    assert str(result.website) == mock_provider.website
    assert result.logo_url == mock_provider.logo_url
    assert result.rating == mock_provider.rating


async def test_get_provider_not_found(
    provider_service: ProviderService,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await provider_service.get_provider(provider_id)

    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)


async def test_get_all_providers(
    provider_service: ProviderService,
    provider_repository_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    limit = 10
    offset = 0
    providers = [mock_provider, mock_provider, mock_provider]
    provider_repository_mock.get_all.return_value = providers

    result = await provider_service.get_all_providers(limit, offset)

    provider_repository_mock.get_all.assert_called_once_with(limit, offset)
    assert len(result) == len(providers)
    for provider_response in result:
        assert isinstance(provider_response, ProviderResponse)
        assert provider_response.id == mock_provider.id
        assert provider_response.name == mock_provider.name


async def test_update_provider_success(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    provider_id = uuid.uuid4()
    update_data = ProviderUpdate(
        name="Updated Provider",
        description="Updated Description",
        website=HttpUrl("https://updated-example.com"),
    )
    provider_repository_mock.get_by_id.return_value = mock_provider

    result = await provider_service.update_provider(provider_id, update_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id, for_update=True
    )
    provider_repository_mock.update.assert_called_once_with(
        provider_id, update_data.model_dump(exclude_unset=True)
    )
    transaction_manager_mock.commit.assert_called_once()
    transaction_manager_mock.refresh.assert_called_once_with(mock_provider)

    assert isinstance(result, ProviderResponse)
    assert result.id == mock_provider.id
    assert result.name == mock_provider.name


async def test_update_provider_not_found(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    update_data = ProviderUpdate(
        name="Updated Provider",
        description="Updated Description",
    )
    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await provider_service.update_provider(provider_id, update_data)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id, for_update=True
    )
    provider_repository_mock.update.assert_not_called()


async def test_update_provider_not_admin(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    update_data = ProviderUpdate(
        name="Updated Provider",
    )
    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await provider_service.update_provider(provider_id, update_data)

    provider_repository_mock.get_by_id.assert_not_called()
    provider_repository_mock.update.assert_not_called()


async def test_delete_provider_success(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = mock_provider

    await provider_service.delete_provider(provider_id)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id, for_update=True
    )
    provider_repository_mock.delete.assert_called_once_with(mock_provider)
    transaction_manager_mock.commit.assert_called_once()


async def test_delete_provider_not_found(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await provider_service.delete_provider(provider_id)

    identity_provider_mock.ensure_is_admin.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id, for_update=True
    )
    provider_repository_mock.delete.assert_not_called()


async def test_delete_provider_not_admin(
    provider_service: ProviderService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    identity_provider_mock.ensure_is_admin.side_effect = AdminAccessDeniedException()

    with pytest.raises(AdminAccessDeniedException):
        await provider_service.delete_provider(provider_id)

    provider_repository_mock.get_by_id.assert_not_called()
    provider_repository_mock.delete.assert_not_called()
