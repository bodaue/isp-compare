from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import InvalidTokenException
from isp_compare.models.search_history import SearchHistory


async def test_clear_search_history_success(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await auth_client.delete("/search-history")
    check_response(response, 204)

    get_response = await auth_client.get("/search-history")
    data = check_response(get_response, 200)

    assert isinstance(data, list)
    assert len(data) == 0


async def test_clear_search_history_unauthorized(
    client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await client.delete("/search-history")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_clear_search_history_empty(auth_client: AsyncClient) -> None:
    response = await auth_client.delete("/search-history")
    check_response(response, 204)

    get_response = await auth_client.get("/search-history")
    data = check_response(get_response, 200)
    assert len(data) == 0
