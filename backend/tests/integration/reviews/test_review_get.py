import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import ReviewNotFoundException
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


async def test_get_review_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())

    response = await client.get(f"/reviews/{non_existent_id}")
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)
