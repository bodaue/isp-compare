from uuid import uuid4

from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import (
    InvalidTokenException,
    SearchHistoryNotFoundException,
)
from isp_compare.models.search_history import SearchHistory


async def test_delete_search_history_entry_success(
    auth_client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    if not user_search_history:
        return

    history_id = user_search_history[0].id

    response = await auth_client.delete(f"/search-history/{history_id}")
    check_response(response, 204)

    all_response = await auth_client.get("/search-history")
    all_data = all_response.json()

    history_ids = [item["id"] for item in all_data]
    assert str(history_id) not in history_ids


async def test_delete_search_history_entry_not_found(auth_client: AsyncClient) -> None:
    non_existent_id = str(uuid4())
    response = await auth_client.delete(f"/search-history/{non_existent_id}")
    check_response(response, 404, expected_detail=SearchHistoryNotFoundException.detail)


async def test_delete_search_history_entry_unauthorized(
    client: AsyncClient, user_search_history: list[SearchHistory]
) -> None:
    if not user_search_history:
        return

    history_id = user_search_history[0].id
    response = await client.delete(f"/search-history/{history_id}")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_delete_search_history_entry_invalid_id(auth_client: AsyncClient) -> None:
    invalid_id = "not-a-uuid"
    response = await auth_client.delete(f"/search-history/{invalid_id}")
    check_response(response, 422)
