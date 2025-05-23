from httpx import AsyncClient

from isp_compare.core.exceptions import (
    InvalidTokenException,
    ProviderNotFoundException,
)
from isp_compare.models import User
from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from tests.utils import check_response


async def test_create_review_success(
    auth_client: AsyncClient, regular_user: User, provider: Provider
) -> None:
    review_data = {
        "rating": 5,
        "comment": "Отличный провайдер, высокая скорость и стабильное соединение.",
    }

    response = await auth_client.post(
        f"/providers/{provider.id}/reviews", json=review_data
    )
    data = check_response(response, 201)

    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["user"]["username"] == regular_user.username


async def test_create_review_unauthorized(
    client: AsyncClient, provider: Provider
) -> None:
    review_data = {
        "rating": 4,
        "comment": "Неавторизованный отзыв не должен быть создан.",
    }

    response = await client.post(f"/providers/{provider.id}/reviews", json=review_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_create_review_provider_not_found(auth_client: AsyncClient) -> None:
    import uuid

    non_existent_id = str(uuid.uuid4())

    review_data = {"rating": 3, "comment": "Отзыв для несуществующего провайдера."}

    response = await auth_client.post(
        f"/providers/{non_existent_id}/reviews", json=review_data
    )
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_create_review_invalid_data(
    auth_client: AsyncClient, provider: Provider
) -> None:
    invalid_data = {"rating": 6, "comment": "Некорректный рейтинг."}
    response = await auth_client.post(
        f"/providers/{provider.id}/reviews", json=invalid_data
    )
    check_response(response, 422)

    invalid_data = {"rating": 4, "comment": "OK"}
    response = await auth_client.post(
        f"/providers/{provider.id}/reviews", json=invalid_data
    )
    check_response(response, 422)


async def test_create_review_already_exists(
    auth_client: AsyncClient, provider: Provider, review: Review
) -> None:
    review_data = {
        "rating": 2,
        "comment": "Повторный отзыв должен обновить существующий.",
    }

    response = await auth_client.post(
        f"/providers/{provider.id}/reviews", json=review_data
    )
    data = check_response(response, 201)

    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert data["id"] == str(review.id)


async def test_review_creation_updates_provider_rating(
    auth_client: AsyncClient, provider: Provider
) -> None:
    provider_response = await auth_client.get(f"/providers/{provider.id}")
    provider_data = provider_response.json()
    initial_rating = provider_data["rating"]

    review_data = {
        "rating": 5,
        "comment": "Excellent provider with great service and fast speeds.",
    }

    await auth_client.post(f"/providers/{provider.id}/reviews", json=review_data)

    updated_provider_response = await auth_client.get(f"/providers/{provider.id}")
    updated_provider_data = updated_provider_response.json()
    updated_rating = updated_provider_data["rating"]

    assert updated_rating != initial_rating
    assert updated_rating == 5.0
