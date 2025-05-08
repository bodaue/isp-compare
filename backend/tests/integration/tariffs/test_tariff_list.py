from httpx import AsyncClient

from isp_compare.models.tariff import Tariff
from tests.utils import check_response


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
