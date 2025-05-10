import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.models import Provider
from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_get_provider_tariffs_success(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    response = await client.get(f"/providers/{provider.id}/tariffs")
    data = check_response(response, 200)

    assert isinstance(data, list)
    expected_tariff_ids = [str(t.id) for t in tariffs]
    response_tariff_ids = [t["id"] for t in data]

    for tariff_id in expected_tariff_ids:
        assert tariff_id in response_tariff_ids


async def test_get_provider_tariffs_with_limit(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    limit = 2
    response = await client.get(
        f"/providers/{provider.id}/tariffs", params={"limit": limit}
    )
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == limit


async def test_get_provider_tariffs_with_offset(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    offset = 1
    response = await client.get(
        f"/providers/{provider.id}/tariffs", params={"offset": offset}
    )
    data = check_response(response, 200)

    assert len(data) == (len(tariffs) - 1)


async def test_get_provider_tariffs_only_active(
    client: AsyncClient,
    tariffs: list[Tariff],
    inactive_tariff: Tariff,
    provider: Provider,
) -> None:
    response = await client.get(f"/providers/{provider.id}/tariffs")
    data = check_response(response, 200)

    response_tariff_ids = [t["id"] for t in data]
    assert str(inactive_tariff.id) not in response_tariff_ids


async def test_get_provider_tariffs_empty(
    client: AsyncClient, provider: Provider
) -> None:
    response = await client.get(f"/providers/{provider.id}/tariffs")
    data = check_response(response)

    assert isinstance(data, list)
    assert len(data) == 0


async def test_get_provider_tariffs_provider_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/providers/{non_existent_id}/tariffs")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)
