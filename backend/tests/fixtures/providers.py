import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.tariff import ConnectionType, Tariff


@pytest.fixture
async def provider(session: AsyncSession) -> Provider:
    test_provider = Provider(
        name="Test Provider",
        description="A provider for testing purposes",
        website="https://testprovider.com/",
        logo_url="https://testprovider.com/logo.png",
        rating=4.5,
    )
    session.add(test_provider)
    await session.commit()

    return test_provider


@pytest.fixture
async def providers(session: AsyncSession) -> list[Provider]:
    test_providers = [
        Provider(
            name=f"Provider {i}",
            description=f"Description for provider {i}",
            website=f"https://provider{i}.com/",
            logo_url=f"https://provider{i}.com/logo.png",
            rating=float(i) / 2,
        )
        for i in range(2, 11, 2)
    ]

    session.add_all(test_providers)

    await session.commit()

    return test_providers


@pytest.fixture
async def inactive_provider(session: AsyncSession) -> Provider:
    inactive_provider = Provider(
        name="Inactive Provider",
        description="A provider that should be filtered out in active-only queries",
        website="https://inactiveprovider.com",
        logo_url="https://inactiveprovider.com/logo.png",
        rating=1.0,
    )
    session.add(inactive_provider)
    await session.flush()

    inactive_tariff = Tariff(
        provider_id=inactive_provider.id,
        name="Outdated Plan",
        description="This plan is no longer available",
        price=19.99,
        speed=10,
        connection_type=ConnectionType.ADSL,
        has_tv=False,
        has_phone=False,
        is_active=False,
    )
    session.add(inactive_tariff)

    await session.commit()
    await session.refresh(inactive_provider)

    return inactive_provider
