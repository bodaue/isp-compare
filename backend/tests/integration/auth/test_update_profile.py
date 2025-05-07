from httpx import AsyncClient

from isp_compare.core.exceptions import UsernameAlreadyExistsException
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
