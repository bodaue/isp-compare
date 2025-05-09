import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.tariff import Tariff


@pytest.fixture
async def tariff(session: AsyncSession, provider: Provider) -> Tariff:
    test_tariff = Tariff(
        provider_id=provider.id,
        name="Test Tariff",
        description="A tariff for testing purposes",
        price=29.99,
        speed=100,
        has_tv=True,
        has_phone=False,
        connection_cost=10.00,
        promo_price=19.99,
        promo_period=3,
        is_active=True,
    )
    session.add(test_tariff)
    await session.commit()
    return test_tariff


@pytest.fixture
async def tariffs(session: AsyncSession, provider: Provider) -> list[Tariff]:
    test_tariffs = [
        Tariff(
            provider_id=provider.id,
            name=f"Tariff {i}",
            description=f"Description for tariff {i}",
            price=float(i * 10),
            speed=i * 50,
            has_tv=i % 2 == 0,
            has_phone=i % 3 == 0,
            connection_cost=float(i * 5),
            promo_price=float(i * 8) if i % 2 == 0 else None,
            promo_period=i if i % 2 == 0 else None,
            is_active=True,
        )
        for i in range(1, 6)
    ]

    inactive_tariff = Tariff(
        provider_id=provider.id,
        name="Inactive Tariff",
        description="This tariff is not active",
        price=99.99,
        speed=200,
        has_tv=False,
        has_phone=False,
        is_active=False,
    )
    test_tariffs.append(inactive_tariff)

    session.add_all(test_tariffs)
    await session.commit()

    return test_tariffs
