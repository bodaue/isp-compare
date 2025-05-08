import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from tests.utils import check_response


async def test_get_provider_reviews_success(
    client: AsyncClient, provider: Provider, reviews: list[Review]
) -> None:
    response = await client.get(f"/providers/{provider.id}/reviews")
    data = check_response(response, 200)

    assert isinstance(data, list)
    provider_review_count = sum(1 for r in reviews if r.provider_id == provider.id)
    assert len(data) == provider_review_count

    if data:
        assert "id" in data[0]
        assert "rating" in data[0]
        assert "comment" in data[0]
        assert "created_at" in data[0]
        assert "user" in data[0]


async def test_get_provider_reviews_with_limit(
    client: AsyncClient, provider: Provider, reviews: list[Review]
) -> None:
    limit = 1
    response = await client.get(f"/providers/{provider.id}/reviews?limit={limit}")
    data = check_response(response, 200)

    assert isinstance(data, list)
    assert len(data) <= limit

    for review in data:
        assert review["provider"]["id"] == str(provider.id)


async def test_get_provider_reviews_with_offset(
    client: AsyncClient, provider: Provider, reviews: list[Review]
) -> None:
    all_response = await client.get(f"/providers/{provider.id}/reviews")
    all_data = all_response.json()

    offset = 1
    response = await client.get(f"/providers/{provider.id}/reviews?offset={offset}")
    data = check_response(response, 200)

    if len(all_data) > offset:
        expected_length = len(all_data) - offset
        assert len(data) <= expected_length

        for i in range(min(len(data), len(all_data) - offset)):
            assert data[i]["id"] == all_data[i + offset]["id"]


async def test_get_provider_reviews_provider_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/providers/{non_existent_id}/reviews")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_get_provider_reviews_empty_list(
    client: AsyncClient, provider: Provider
) -> None:
    response = await client.get(f"/providers/{provider.id}/reviews")
    data = check_response(response, 200)

    assert isinstance(data, list)

    assert len(data) == 0
