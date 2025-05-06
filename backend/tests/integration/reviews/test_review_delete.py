import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import (
    InvalidTokenException,
    ReviewNotFoundException,
)
from isp_compare.models import Provider
from isp_compare.models.review import Review
from tests.utils import check_response


async def test_delete_review_success(auth_client: AsyncClient, review: Review) -> None:
    response = await auth_client.delete(f"/reviews/{review.id}")
    check_response(response, 204)

    response = await auth_client.get(f"/reviews/{review.id}")
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)


async def test_delete_review_unauthorized(client: AsyncClient, review: Review) -> None:
    response = await client.delete(f"/reviews/{review.id}")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)

    response = await client.get(f"/reviews/{review.id}")
    check_response(response, 200)


async def test_delete_review_as_admin(
    admin_client: AsyncClient, review: Review
) -> None:
    response = await admin_client.delete(f"/reviews/{review.id}")
    check_response(response, 204)

    response = await admin_client.get(f"/reviews/{review.id}")
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)


async def test_delete_review_not_found(
    auth_client: AsyncClient, review: Review
) -> None:
    non_existent_id = str(uuid.uuid4())
    response = await auth_client.delete(f"/reviews/{non_existent_id}")
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)


async def test_delete_review_updates_provider_rating(
    auth_client: AsyncClient,
    provider: Provider,
    review: Review,
    review_2: Review,
) -> None:
    provider_response = await auth_client.get(f"/providers/{provider.id}")
    provider_data = provider_response.json()
    initial_rating = provider_data["rating"]
    await auth_client.delete(f"/reviews/{review.id}")

    updated_provider_response = await auth_client.get(f"/providers/{provider.id}")
    updated_provider_data = updated_provider_response.json()

    current_rating = updated_provider_data["rating"]
    assert current_rating == 5.0 != initial_rating
