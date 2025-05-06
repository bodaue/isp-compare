from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import InvalidTokenException
from isp_compare.models.search_history import SearchHistory


async def test_get_search_history_success(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await auth_client.get("/search-history")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == len(user_search_history)

    if len(data) > 1:
        assert data[0]["created_at"] >= data[1]["created_at"]

    for item in data:
        assert "id" in item
        assert "user_id" in item
        assert "search_params" in item
        assert "created_at" in item


async def test_get_search_history_unauthorized(
    client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await client.get("/search-history")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_get_search_history_with_limit(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    limit = 2
    response = await auth_client.get(f"/search-history?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit

    # If there are enough history entries, verify we got the right amount
    if len(user_search_history) >= limit:
        assert len(data) == limit


async def test_get_search_history_with_offset(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    offset = 1
    response = await auth_client.get(f"/search-history?offset={offset}")
    data = check_response(response, 200)

    # Get all search history to compare
    all_response = await auth_client.get("/search-history")
    all_data = all_response.json()

    # Check that offset works correctly
    if len(all_data) > offset:
        assert len(data) == len(all_data) - offset

        # Verify that offset items are skipped
        for i in range(len(data)):
            assert data[i]["id"] == all_data[i + offset]["id"]


async def test_get_search_history_empty(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/search-history")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) == 0
