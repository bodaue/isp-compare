from httpx import AsyncClient

from isp_compare.models import Provider
from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_get_provider_tariffs_success(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    response = await client.get(f"/providers/{provider.id}/tariffs")
    data = check_response(response, 200)

    assert isinstance(data, list)
    provider_tariff_ids = [str(t.id) for t in tariffs if t.provider_id == provider.id]
    response_tariff_ids = [t["id"] for t in data]

    for tariff_id in provider_tariff_ids:
        assert tariff_id in response_tariff_ids


async def test_get_provider_tariffs_with_limit(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    limit = 2
    response = await client.get(f"/providers/{provider.id}/tariffs?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit

    for tariff in data:
        assert tariff["provider_id"] == str(provider.id)


async def test_get_provider_tariffs_with_offset(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    all_response = await client.get(f"/providers/{provider.id}/tariffs")
    all_data = all_response.json()

    offset = 1
    response = await client.get(f"/providers/{provider.id}/tariffs?offset={offset}")
    data = check_response(response, 200)

    if len(all_data) > offset:
        expected_length = len(all_data) - offset
        assert len(data) <= expected_length

        for i in range(min(len(data), len(all_data) - offset)):
            assert data[i]["id"] == all_data[i + offset]["id"]


async def test_get_provider_tariffs_provider_not_found(client: AsyncClient) -> None:
    import uuid

    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/providers/{non_existent_id}/tariffs")
    from isp_compare.core.exceptions import ProviderNotFoundException

    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)
