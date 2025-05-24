import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from isp_compare.models.provider import Provider
from isp_compare.models.tariff import Tariff
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff_comparison import (
    ComparisonRequest,
)
from isp_compare.services.tariff_comparison import TariffComparisonService


@pytest.fixture
def tariff_repository_mock() -> AsyncMock:
    return AsyncMock(spec=TariffRepository)


@pytest.fixture
def provider_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ProviderRepository)


@pytest.fixture
def tariff_comparison_service(
    tariff_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> TariffComparisonService:
    return TariffComparisonService(
        tariff_repository=tariff_repository_mock,
        provider_repository=provider_repository_mock,
    )


def create_mock_tariff(
    tariff_id: uuid.UUID,
    provider_id: uuid.UUID,
    price: float = 29.99,
    speed: int = 100,
    has_tv: bool = False,
    has_phone: bool = False,
    promo_price: float | None = None,
    connection_cost: float | None = None,
) -> Tariff:
    return Tariff(
        id=tariff_id,
        provider_id=provider_id,
        name=f"Test Tariff {tariff_id}",
        description="Test description",
        price=price,
        speed=speed,
        has_tv=has_tv,
        has_phone=has_phone,
        connection_cost=connection_cost,
        promo_price=promo_price,
        promo_period=3 if promo_price else None,
        is_active=True,
    )


def create_mock_provider(provider_id: uuid.UUID, name: str) -> Provider:
    return Provider(
        id=provider_id,
        name=name,
        description="Test provider",
        website="https://example.com",
        phone="+7 900 000-00-00",
        rating=4.5,
    )


async def test_compare_tariffs_without_additional_features(
    tariff_comparison_service: TariffComparisonService,
    tariff_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id_1 = uuid.uuid4()
    provider_id_2 = uuid.uuid4()
    tariff_id_1 = uuid.uuid4()
    tariff_id_2 = uuid.uuid4()

    tariff_1 = create_mock_tariff(
        tariff_id=tariff_id_1,
        provider_id=provider_id_1,
        price=25.0,
        speed=100,
        has_tv=False,
        has_phone=False,
    )

    tariff_2 = create_mock_tariff(
        tariff_id=tariff_id_2,
        provider_id=provider_id_2,
        price=30.0,
        speed=200,
        has_tv=False,
        has_phone=False,
    )

    provider_1 = create_mock_provider(provider_id_1, "Provider 1")
    provider_2 = create_mock_provider(provider_id_2, "Provider 2")

    tariff_repository_mock.get_multiple_by_ids.return_value = {
        tariff_id_1: tariff_1,
        tariff_id_2: tariff_2,
    }

    provider_repository_mock.get_multiple_by_ids.return_value = {
        provider_id_1: provider_1,
        provider_id_2: provider_2,
    }

    request = ComparisonRequest(tariff_ids=[tariff_id_1, tariff_id_2])
    result = await tariff_comparison_service.compare_tariffs(request)

    assert len(result.items) == 2

    for item in result.items:
        assert len(item.features) == 0
        assert item.has_most_features is False

    item_1 = next(i for i in result.items if i.id == tariff_id_1)
    item_2 = next(i for i in result.items if i.id == tariff_id_2)

    expected_score_1 = Decimal("25.0") / Decimal("100")
    expected_score_2 = Decimal("30.0") / Decimal("200")

    assert item_1.value_score == expected_score_1
    assert item_2.value_score == expected_score_2

    assert item_2.is_best_value is True
    assert item_1.is_best_value is False


async def test_compare_tariffs_with_high_connection_cost(
    tariff_comparison_service: TariffComparisonService,
    tariff_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    tariff_id_1 = uuid.uuid4()
    tariff_id_2 = uuid.uuid4()

    tariff_1 = create_mock_tariff(
        tariff_id=tariff_id_1,
        provider_id=provider_id,
        price=30.0,
        speed=100,
        connection_cost=5000.0,
    )

    tariff_2 = create_mock_tariff(
        tariff_id=tariff_id_2,
        provider_id=provider_id,
        price=30.0,
        speed=100,
        connection_cost=0.0,
    )

    provider = create_mock_provider(provider_id, "Test Provider")

    tariff_repository_mock.get_multiple_by_ids.return_value = {
        tariff_id_1: tariff_1,
        tariff_id_2: tariff_2,
    }

    provider_repository_mock.get_multiple_by_ids.return_value = {
        provider_id: provider,
    }

    request = ComparisonRequest(tariff_ids=[tariff_id_1, tariff_id_2])
    result = await tariff_comparison_service.compare_tariffs(request)

    assert len(result.items) == 2

    item_1 = next(i for i in result.items if i.id == tariff_id_1)
    item_2 = next(i for i in result.items if i.id == tariff_id_2)

    assert item_1.value_score > item_2.value_score
    assert item_2.is_best_value is True
    assert item_1.is_best_value is False

    assert item_1.connection_cost == Decimal("5000.0")
    assert item_2.connection_cost == Decimal("0.0")


async def test_mark_best_tariffs_empty_list(
    tariff_comparison_service: TariffComparisonService,
) -> None:
    items = []

    tariff_comparison_service._mark_best_tariffs(items)

    assert len(items) == 0


async def test_compare_tariffs_single_tariff_with_all_features(
    tariff_comparison_service: TariffComparisonService,
    tariff_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    tariff_id = uuid.uuid4()

    tariff = create_mock_tariff(
        tariff_id=tariff_id,
        provider_id=provider_id,
        price=50.0,
        speed=300,
        has_tv=True,
        has_phone=True,
        promo_price=40.0,
        connection_cost=0.0,
    )

    provider = create_mock_provider(provider_id, "Premium Provider")

    tariff_repository_mock.get_multiple_by_ids.return_value = {
        tariff_id: tariff,
    }

    provider_repository_mock.get_multiple_by_ids.return_value = {
        provider_id: provider,
    }

    request = ComparisonRequest(tariff_ids=[tariff_id, tariff_id])
    result = await tariff_comparison_service.compare_tariffs(request)

    assert len(result.items) == 1

    item = result.items[0]

    assert item.is_cheapest is True
    assert item.is_fastest is True
    assert item.is_best_value is True
    assert item.has_most_features is True

    assert len(item.features) == 2
    assert "ТВ" in item.features
    assert "Телефон" in item.features

    assert item.is_promo is True
    assert item.current_price == Decimal("40.0")
    assert item.original_price == Decimal("50.0")
    assert item.promo_period == 3

    assert len(result.recommendations) > 0
    assert any("акция" in rec.lower() for rec in result.recommendations)
