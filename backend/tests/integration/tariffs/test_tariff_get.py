import uuid
from httpx import AsyncClient

from isp_compare.models import Provider
from tests.utils import check_response

from isp_compare.core.exceptions import TariffNotFoundException
from isp_compare.models.tariff import Tariff


async def test_get_tariff_success(client: AsyncClient, tariff: Tariff) -> None:
    response = await client.get(f"/tariffs/{tariff.id}")
    data = check_response(response, 200)

    assert data["id"] == str(tariff.id)
    assert data["name"] == tariff.name
    assert data["description"] == tariff.description
    assert float(data["price"]) == tariff.price
    assert data["speed"] == tariff.speed
    assert data["connection_type"] == tariff.connection_type.value
    assert data["has_tv"] == tariff.has_tv
    assert data["has_phone"] == tariff.has_phone
    assert data["additional_services"] == tariff.additional_services
    assert float(data["connection_cost"]) == tariff.connection_cost
    assert data["contract_period"] == tariff.contract_period
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


async def test_get_all_tariffs_success(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    response = await client.get("/tariffs")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) >= len([t for t in tariffs if t.is_active])

    active_tariff_ids = [str(t.id) for t in tariffs if t.is_active]
    response_tariff_ids = [t["id"] for t in data]

    for tariff_id in active_tariff_ids:
        assert tariff_id in response_tariff_ids


async def test_get_all_tariffs_with_limit(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    limit = 2
    response = await client.get(f"/tariffs?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit


async def test_get_all_tariffs_with_offset(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    all_response = await client.get("/tariffs")
    all_data = all_response.json()

    offset = 2
    response = await client.get(f"/tariffs?offset={offset}")
    data = check_response(response, 200)

    if len(all_data) > offset:
        expected_length = len(all_data) - offset
        assert len(data) <= expected_length

        for i in range(min(len(data), len(all_data) - offset)):
            assert data[i]["id"] == all_data[i + offset]["id"]


async def test_get_provider_tariffs_success(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    response = await client.get(f"/providers/{provider.id}/tariffs")
    data = check_response(response, 200)

    assert isinstance(data, list)
    provider_tariff_ids = [str(t.id) for t in tariffs]
    response_tariff_ids = [t["id"] for t in data]

    for tariff_id in provider_tariff_ids:
        if tariff_id in response_tariff_ids:
            assert tariff_id in response_tariff_ids
