from httpx import AsyncClient
from utils import check_response

from isp_compare.models.provider import Provider


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


async def test_list_providers_with_limit(
    client: AsyncClient, providers: list[Provider]
) -> None:
    limit = 2
    response = await client.get(f"/providers?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit


async def test_list_providers_with_offset(
    client: AsyncClient, providers: list[Provider]
) -> None:
    response_all = await client.get("/providers")
    all_providers = response_all.json()

    offset = 2
    response_offset = await client.get(f"/providers?offset={offset}")
    offset_providers = check_response(response_offset, 200)

    if len(all_providers) > offset:
        assert len(offset_providers) == len(all_providers) - offset
        for i in range(len(offset_providers)):
            assert offset_providers[i]["id"] == all_providers[i + offset]["id"]


async def test_list_providers_with_limit_and_offset(
    client: AsyncClient, providers: list[Provider]
) -> None:
    limit = 2
    offset = 1
    response = await client.get(f"/providers?limit={limit}&offset={offset}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit

    response_all = await client.get("/providers")
    all_providers = response_all.json()

    if len(all_providers) > offset:
        for i in range(min(len(data), len(all_providers) - offset)):
            assert data[i]["id"] == all_providers[i + offset]["id"]


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


async def test_list_providers_with_large_limit(
    client: AsyncClient, providers: list[Provider]
) -> None:
    limit = 1000
    response = await client.get(f"/providers?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)

    provider_ids = [p["id"] for p in data]
    for provider in providers:
        assert str(provider.id) in provider_ids


async def test_list_providers_with_invalid_parameters(client: AsyncClient) -> None:
    response = await client.get("/providers?limit=abc")
    check_response(response, 422)
