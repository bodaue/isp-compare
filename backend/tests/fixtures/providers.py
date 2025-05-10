import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider


@pytest.fixture
async def provider(session: AsyncSession) -> Provider:
    test_provider = Provider(
        name="Test Provider",
        description="A provider for testing purposes",
        website="https://testprovider.com",
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
            website=f"https://provider{i}.com",
            logo_url=f"https://provider{i}.com/logo.png",
            rating=i,
        )
        for i in range(1, 6)
    ]
    session.add_all(test_providers)
    await session.commit()
    return test_providers
