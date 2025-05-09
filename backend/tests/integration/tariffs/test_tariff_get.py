import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import TariffNotFoundException
from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_get_tariff_success(client: AsyncClient, tariff: Tariff) -> None:
    response = await client.get(f"/tariffs/{tariff.id}")
    data = check_response(response, 200)

    assert data["id"] == str(tariff.id)
    assert data["name"] == tariff.name
    assert data["description"] == tariff.description
    assert float(data["price"]) == tariff.price
    assert data["speed"] == tariff.speed
    assert data["has_tv"] == tariff.has_tv
    assert data["has_phone"] == tariff.has_phone
    assert float(data["connection_cost"]) == tariff.connection_cost
    if tariff.promo_price:
        assert float(data["promo_price"]) == tariff.promo_price
    else:
        assert data["promo_price"] is None
    assert data["promo_period"] == tariff.promo_period
    assert data["is_active"] == tariff.is_active
    assert data["provider_id"] == str(tariff.provider_id)


async def test_get_tariff_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = await client.get(f"/tariffs/{non_existent_id}")
    check_response(response, 404, expected_detail=TariffNotFoundException.detail)


async def test_get_tariff_invalid_id(client: AsyncClient) -> None:
    invalid_id = "not-a-uuid"
    response = await client.get(f"/tariffs/{invalid_id}")
    check_response(response, 422)
