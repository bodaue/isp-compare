from faker import Faker
from httpx import AsyncClient

from isp_compare.core.exceptions import (
    UsernameAlreadyExistsException,
    UsernameChangeRateLimitExceededException,
)
from isp_compare.models import User
from tests.utils import check_response


async def test_update_profile_success(
    auth_client: AsyncClient, regular_user: User
) -> None:
    update_data = {"fullname": "Updated Name", "username": "updated_user"}

    response = await auth_client.patch("/users/profile", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(regular_user.id)
    assert data["fullname"] == update_data["fullname"]
    assert data["username"] == update_data["username"]
    assert data["email"] == regular_user.email


async def test_update_profile_partial(
    auth_client: AsyncClient, regular_user: User
) -> None:
    update_data = {"fullname": "Partially Updated Name"}

    response = await auth_client.patch("/users/profile", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(regular_user.id)
    assert data["fullname"] == update_data["fullname"]
    assert data["username"] == regular_user.username


async def test_update_profile_duplicate_username(
    auth_client: AsyncClient,
    regular_user: User,
    regular_user_2: User,
) -> None:
    update_data = {"username": regular_user_2.username}

    response = await auth_client.patch("/users/profile", json=update_data)
    check_response(response, 409, expected_detail=UsernameAlreadyExistsException.detail)


async def test_update_profile_empty(
    auth_client: AsyncClient, regular_user: User
) -> None:
    update_data = {}

    response = await auth_client.patch("/users/profile", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(regular_user.id)
    assert data["fullname"] == regular_user.fullname
    assert data["username"] == regular_user.username


async def test_update_profile_invalid_username(auth_client: AsyncClient) -> None:
    update_data = {"username": "a"}

    response = await auth_client.patch("/users/profile", json=update_data)
    check_response(response, 422)


async def test_update_profile_rate_limit(
    auth_client: AsyncClient,
    regular_user: User,
    faker: Faker,
) -> None:
    for _ in range(2):
        update_data = {"username": faker.unique.user_name()}
        await auth_client.patch("/users/profile", json=update_data)

    update_data = {"username": faker.unique.user_name()}
    response = await auth_client.patch("/users/profile", json=update_data)
    check_response(
        response, 429, expected_detail=UsernameChangeRateLimitExceededException.detail
    )
