from httpx import AsyncClient

from isp_compare.core.exceptions import InvalidTokenException
from isp_compare.models.search_history import SearchHistory
from tests.utils import check_response


async def test_get_latest_search_history_success(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await auth_client.get("/search-history/latest")
    data = check_response(response, 200)

    latest_history = max(user_search_history, key=lambda x: x.created_at)

    assert data["id"] == str(latest_history.id)
    assert data["user_id"] == str(latest_history.user_id)
    assert data["search_params"] == latest_history.search_params
    assert "created_at" in data


async def test_get_latest_search_history_empty(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/search-history/latest")
    assert response.status_code == 200
    assert response.json() is None


async def test_get_latest_search_history_unauthorized(
    client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    response = await client.get("/search-history/latest")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)
