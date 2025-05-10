from httpx import AsyncClient

from isp_compare.models.provider import Provider
from tests.utils import check_response


async def test_list_providers_success(
    client: AsyncClient, providers: list[Provider]
) -> None:
    response = await client.get("/providers")
    data = check_response(response, 200)
    assert isinstance(data, list)
    assert len(data) >= len(providers)
    provider_ids = [p["id"] for p in data]
    for provider in providers:
        assert str(provider.id) in provider_ids


async def test_list_providers_empty(client: AsyncClient) -> None:
    response = await client.get("/providers")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == 0


async def test_list_providers_as_authenticated_user(
    auth_client: AsyncClient, providers: list[Provider]
) -> None:
    response = await auth_client.get("/providers")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == len(providers)


async def test_list_providers_as_admin(
    admin_client: AsyncClient, providers: list[Provider]
) -> None:
    response = await admin_client.get("/providers")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == len(providers)
