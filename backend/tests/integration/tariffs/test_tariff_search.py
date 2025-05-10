from httpx import AsyncClient

from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_search_tariffs_success(
    auth_client: AsyncClient, tariffs: list[Tariff]
) -> None:
    search_params = {
        "min_price": 20,
        "max_price": 40,
        "min_speed": 50,
        "max_speed": 150,
        "has_tv": True,
        "has_phone": False,
    }

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    assert isinstance(data, list)

    for tariff_data in data:
        assert float(tariff_data["price"]) >= search_params["min_price"]
        assert float(tariff_data["price"]) <= search_params["max_price"]
        assert tariff_data["speed"] >= search_params["min_speed"]
        assert tariff_data["speed"] <= search_params["max_speed"]
        assert tariff_data["has_tv"] == search_params["has_tv"]
        assert tariff_data["has_phone"] == search_params["has_phone"]
        assert tariff_data["is_active"] is True


async def test_search_tariffs_by_promo_price(
    auth_client: AsyncClient, tariff: Tariff
) -> None:
    search_params = {"min_price": 19, "max_price": 20}

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(tariff.id)


async def test_search_tariffs_unauthorized(client: AsyncClient) -> None:
    search_params = {"min_price": 20, "max_price": 40}

    response = await client.get("/tariffs/search", params=search_params)
    check_response(response, 200)


async def test_search_tariffs_partial_params(
    auth_client: AsyncClient, tariffs: list[Tariff]
) -> None:
    search_params = {"min_speed": 100, "has_tv": True}

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    assert isinstance(data, list)

    for tariff_data in data:
        assert tariff_data["speed"] >= search_params["min_speed"]
        assert tariff_data["has_tv"] == search_params["has_tv"]
        assert tariff_data["is_active"] is True


async def test_search_tariffs_no_results(auth_client: AsyncClient) -> None:
    search_params = {"min_price": 1000, "min_speed": 1000}

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == 0


async def test_search_tariffs_limit_offset(
    auth_client: AsyncClient, tariffs: list[Tariff]
) -> None:
    search_params = {"limit": 2, "offset": 1}

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= search_params["limit"]

    all_response = await auth_client.get("/tariffs/search")
    all_data = all_response.json()

    if len(all_data) > search_params["offset"]:
        for i in range(min(len(data), len(all_data) - search_params["offset"])):
            assert data[i]["id"] == all_data[i + search_params["offset"]]["id"]


async def test_search_tariffs_only_active(
    auth_client: AsyncClient,
    tariffs: list[Tariff],
    inactive_tariff: Tariff,
) -> None:
    search_params = {"min_speed": 1}

    response = await auth_client.get("/tariffs/search", params=search_params)
    data = check_response(response, 200)

    response_tariff_ids = [t["id"] for t in data]
    assert str(inactive_tariff.id) not in response_tariff_ids


async def test_search_tariffs_invalid_params(auth_client: AsyncClient) -> None:
    invalid_params = {"min_price": "not-a-number", "max_speed": "invalid"}

    response = await auth_client.get("/tariffs/search", params=invalid_params)
    check_response(response, 422)

    invalid_params = {"min_price": -10, "min_speed": -50}

    response = await auth_client.get("/tariffs/search", params=invalid_params)
    check_response(response, 422)


async def test_search_tariffs_creates_history(
    auth_client: AsyncClient, tariffs: list[Tariff]
) -> None:
    initial_response = await auth_client.get("/search-history")
    initial_data = initial_response.json()
    initial_count = len(initial_data)

    search_params = {
        "min_price": 25,
        "max_speed": 200,
        "has_tv": True,
    }

    await auth_client.get("/tariffs/search", params=search_params)

    history_response = await auth_client.get("/search-history")
    history_data = history_response.json()

    assert len(history_data) == initial_count + 1

    latest_history = history_data[0]
    assert latest_history["search_params"] == {
        "min_price": "25",
        "max_speed": 200,
        "has_tv": True,
        "limit": 50,
        "offset": 0,
    }
