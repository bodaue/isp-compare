import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import (
    ProviderNotFoundException,
    ReviewNotFoundException,
)
from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from tests.utils import check_response


async def test_get_review_success(client: AsyncClient, review: Review) -> None:
    response = await client.get(f"/reviews/{review.id}")
    data = check_response(response, 200)

    assert data["id"] == str(review.id)
    assert data["rating"] == review.rating
    assert data["comment"] == review.comment
    assert "created_at" in data
    assert "updated_at" in data
    assert "user" in data
    assert "provider" in data


async def test_get_review_not_found(client: AsyncClient) -> None:
    import uuid

    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/reviews/{non_existent_id}")
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)


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


async def test_get_provider_reviews_provider_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/providers/{non_existent_id}/reviews")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)
