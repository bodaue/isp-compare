import uuid

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.repositories.provider import ProviderRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def provider_repository(session: AsyncSession) -> ProviderRepository:
    return ProviderRepository(session=session)


@pytest.fixture
async def test_provider(session: AsyncSession, faker: Faker) -> Provider:
    provider = Provider(
        name=faker.company(),
        description=faker.paragraph(),
        website=faker.url(),
        logo_url=faker.image_url(),
        rating=faker.pyfloat(min_value=1, max_value=5, right_digits=1),
    )
    session.add(provider)
    await session.commit()
    return provider


@pytest.fixture
async def test_providers(session: AsyncSession, faker: Faker) -> list[Provider]:
    providers = []
    for _ in range(3):
        provider = Provider(
            name=faker.company(),
            description=faker.paragraph(),
            website=faker.url(),
            logo_url=faker.image_url(),
            rating=faker.pyfloat(min_value=1, max_value=5, right_digits=1),
        )
        providers.append(provider)

    session.add_all(providers)
    await session.commit()
    return providers


async def test_create_provider(
    session: AsyncSession, provider_repository: ProviderRepository, faker: Faker
) -> None:
    provider = Provider(
        name=faker.company(),
        description=faker.paragraph(),
        website=faker.url(),
        logo_url=faker.image_url(),
        rating=faker.pyfloat(min_value=1, max_value=5, right_digits=1),
    )

    await provider_repository.create(provider)
    await session.flush()

    stmt = select(Provider).where(Provider.id == provider.id)
    result = await session.execute(stmt)
    saved_provider = result.scalar_one()

    assert saved_provider.id == provider.id
    assert saved_provider.name == provider.name
    assert saved_provider.description == provider.description
    assert saved_provider.website == provider.website
    assert saved_provider.logo_url == provider.logo_url
    assert saved_provider.rating == provider.rating


async def test_get_by_id(
    provider_repository: ProviderRepository, test_provider: Provider
) -> None:
    result = await provider_repository.get_by_id(test_provider.id)

    assert result is not None
    assert result.id == test_provider.id
    assert result.name == test_provider.name
    assert result.description == test_provider.description


async def test_get_by_id_for_update(
    provider_repository: ProviderRepository, test_provider: Provider
) -> None:
    result = await provider_repository.get_by_id(test_provider.id, for_update=True)

    assert result is not None
    assert result.id == test_provider.id
    assert result.name == test_provider.name


async def test_get_by_id_not_found(provider_repository: ProviderRepository) -> None:
    non_existent_id = uuid.uuid4()
    result = await provider_repository.get_by_id(non_existent_id)

    assert result is None


async def test_get_all(
    provider_repository: ProviderRepository, test_providers: list[Provider]
) -> None:
    limit = 10
    offset = 0
    result = await provider_repository.get_all(limit, offset)

    assert len(result) == len(test_providers)

    provider_ids = {p.id for p in result}
    for provider in test_providers:
        assert provider.id in provider_ids


async def test_get_all_with_limit(
    provider_repository: ProviderRepository, test_providers: list[Provider]
) -> None:
    limit = 2
    offset = 0
    result = await provider_repository.get_all(limit, offset)

    assert len(result) == limit

    provider_ids = [p.id for p in result]
    for provider in test_providers[:limit]:
        assert provider.id in provider_ids


async def test_get_all_with_offset(
    provider_repository: ProviderRepository, test_providers: list[Provider]
) -> None:
    limit = 10
    offset = 1
    result = await provider_repository.get_all(limit, offset)

    assert len(result) == len(test_providers) - offset

    provider_ids = [p.id for p in result]
    assert test_providers[0].id not in provider_ids
    for provider in test_providers[offset:]:
        assert provider.id in provider_ids


async def test_update(
    session: AsyncSession,
    provider_repository: ProviderRepository,
    test_provider: Provider,
    faker: Faker,
) -> None:
    new_name = faker.company()
    new_description = faker.paragraph()
    new_website = faker.url()
    update_data = {
        "name": new_name,
        "description": new_description,
        "website": new_website,
    }

    await provider_repository.update(test_provider.id, update_data)
    await session.commit()

    stmt = select(Provider).where(Provider.id == test_provider.id)
    result = await session.execute(stmt)
    updated_provider = result.scalar_one()

    assert updated_provider.name == new_name
    assert updated_provider.description == new_description
    assert updated_provider.website == new_website
    assert updated_provider.logo_url == test_provider.logo_url


async def test_update_partial(
    session: AsyncSession,
    provider_repository: ProviderRepository,
    test_provider: Provider,
    faker: Faker,
) -> None:
    new_name = faker.company()
    update_data = {"name": new_name}

    await provider_repository.update(test_provider.id, update_data)
    await session.commit()

    stmt = select(Provider).where(Provider.id == test_provider.id)
    result = await session.execute(stmt)
    updated_provider = result.scalar_one()

    assert updated_provider.name == new_name
    assert updated_provider.description == test_provider.description
    assert updated_provider.website == test_provider.website


async def test_update_nonexistent(
    provider_repository: ProviderRepository, faker: Faker
) -> None:
    non_existent_id = uuid.uuid4()
    update_data = {"name": faker.company()}

    await provider_repository.update(non_existent_id, update_data)


async def test_delete(
    session: AsyncSession,
    provider_repository: ProviderRepository,
    test_provider: Provider,
) -> None:
    await provider_repository.delete(test_provider)
    await session.commit()

    stmt = select(Provider).where(Provider.id == test_provider.id)
    result = await session.execute(stmt)
    deleted_provider = result.scalar_one_or_none()

    assert deleted_provider is None
