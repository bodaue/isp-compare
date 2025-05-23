import uuid
from typing import Any
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from redis.asyncio import Redis

from isp_compare.core.exceptions import (
    ProviderNotFoundException,
)
from isp_compare.models.provider import Provider
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.schemas.provider import (
    ProviderResponse,
)
from isp_compare.services.provider import ProviderService


@pytest.fixture
def provider_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ProviderRepository)


@pytest.fixture
def redis_client_mock() -> AsyncMock:
    redis_mock = AsyncMock(spec=Redis)

    async def async_none(*_: Any, **__: Any) -> None:
        return None

    async def async_true(*_: Any, **__: Any) -> True:
        return True

    redis_mock.get.side_effect = async_none
    redis_mock.set.side_effect = async_true

    return redis_mock


@pytest.fixture
def provider_service(
    provider_repository_mock: AsyncMock,
    redis_client_mock: AsyncMock,
) -> ProviderService:
    return ProviderService(
        provider_repository=provider_repository_mock,
        redis_client=redis_client_mock,
    )


@pytest.fixture
def mock_provider(faker: Faker) -> Provider:
    return Provider(
        id=uuid.uuid4(),
        name="Test Provider",
        description="Test Description",
        website="https://example.com",
        phone=faker.phone_number(),
        logo_url="https://example.com/logo.png",
        rating=4.5,
    )


async def test_get_provider_success(
    provider_service: ProviderService,
    provider_repository_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = mock_provider, 0

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
    redis_client_mock: AsyncMock,
    mock_provider: Provider,
) -> None:
    providers = [(mock_provider, 0), (mock_provider, 0), (mock_provider, 0)]
    provider_repository_mock.get_all.return_value = providers

    result = await provider_service.get_all_providers()

    redis_client_mock.get.assert_called_once_with("all_providers")
    provider_repository_mock.get_all.assert_called_once()
    assert len(result) == len(providers)
    for provider_response in result:
        assert isinstance(provider_response, ProviderResponse)
        assert provider_response.id == mock_provider.id
        assert provider_response.name == mock_provider.name
