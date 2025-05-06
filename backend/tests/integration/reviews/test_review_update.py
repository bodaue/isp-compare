import uuid

from httpx import AsyncClient
from tests.utils import check_response

from isp_compare.core.exceptions import (
    InvalidTokenException,
    ReviewNotFoundException,
)
from isp_compare.models.review import Review


async def test_update_review_success(auth_client: AsyncClient, review: Review) -> None:
    update_data = {
        "rating": 3,
        "comment": "Обновленный отзыв после использования услуг некоторое время.",
    }

    response = await auth_client.patch(f"/reviews/{review.id}", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(review.id)
    assert data["rating"] == update_data["rating"]
    assert data["comment"] == update_data["comment"]


async def test_update_review_partial(auth_client: AsyncClient, review: Review) -> None:
    update_data = {"rating": 2}

    response = await auth_client.patch(f"/reviews/{review.id}", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(review.id)
    assert data["rating"] == update_data["rating"]
    assert data["comment"] == review.comment


async def test_update_review_unauthorized(client: AsyncClient, review: Review) -> None:
    update_data = {
        "rating": 1,
        "comment": "Неавторизованное обновление не должно пройти.",
    }

    response = await client.patch(f"/reviews/{review.id}", json=update_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_update_review_not_owner(
    admin_client: AsyncClient, review: Review
) -> None:
    update_data = {"rating": 5, "comment": "Администратор изменил отзыв."}

    response = await admin_client.patch(f"/reviews/{review.id}", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(review.id)
    assert data["rating"] == update_data["rating"]
    assert data["comment"] == update_data["comment"]


async def test_update_review_not_found(auth_client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())
    update_data = {"rating": 4, "comment": "Отзыв не существует."}

    response = await auth_client.patch(f"/reviews/{non_existent_id}", json=update_data)
    check_response(response, 404, expected_detail=ReviewNotFoundException.detail)


async def test_update_review_invalid_data(
    auth_client: AsyncClient, review: Review
) -> None:
    invalid_data = {"rating": 0}
    response = await auth_client.patch(f"/reviews/{review.id}", json=invalid_data)
    check_response(response, 422)

    invalid_data = {"comment": "Кр"}
    response = await auth_client.patch(f"/reviews/{review.id}", json=invalid_data)
    check_response(response, 422)
