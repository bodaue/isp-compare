from httpx import AsyncClient

from isp_compare.core.exceptions import (
    IncorrectPasswordException,
    InvalidTokenException,
    PasswordChangeRateLimitExceededException,
)
from isp_compare.models import User
from tests.utils import check_response


async def test_change_password_success(
    auth_client: AsyncClient, regular_user: User, client: AsyncClient
) -> None:
    password_data = {
        "current_password": "Password123!",
        "new_password": "NewPassword123!",
    }

    response = await auth_client.post("/users/change-password", json=password_data)
    data = check_response(response, 200)

    assert data["message"] == "Password successfully changed"

    login_data = {
        "username": regular_user.username,
        "password": "NewPassword123!",
    }

    login_response = await client.post("/auth/login", json=login_data)
    login_data = check_response(login_response, 200)

    assert "access_token" in login_data


async def test_change_password_incorrect_current(auth_client: AsyncClient) -> None:
    password_data = {
        "current_password": "WrongPassword123!",
        "new_password": "NewPassword123!",
    }

    response = await auth_client.post("/users/change-password", json=password_data)
    check_response(response, 400, expected_detail=IncorrectPasswordException.detail)


async def test_change_password_weak_new_password(auth_client: AsyncClient) -> None:
    password_data = {
        "current_password": "Password123!",
        "new_password": "weak",
    }

    response = await auth_client.post("/users/change-password", json=password_data)
    check_response(response, 422)


async def test_change_password_unauthorized(client: AsyncClient) -> None:
    password_data = {
        "current_password": "Password123!",
        "new_password": "NewPassword123!",
    }

    response = await client.post("/users/change-password", json=password_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_change_password_rate_limit_on_wrong_password(
    auth_client: AsyncClient,
) -> None:
    wrong_password_data = {
        "current_password": "WrongPassword123!",
        "new_password": "NewPassword123!",
    }

    for _ in range(10):
        response = await auth_client.post(
            "/users/change-password", json=wrong_password_data
        )
        assert response.status_code == 400

    response = await auth_client.post(
        "/users/change-password", json=wrong_password_data
    )
    check_response(
        response,
        429,
        expected_detail=PasswordChangeRateLimitExceededException.detail,
    )

    correct_password_data = {
        "current_password": "Password123!",
        "new_password": "NewPassword123!",
    }
    response = await auth_client.post(
        "/users/change-password", json=correct_password_data
    )
    check_response(
        response,
        429,
        expected_detail=PasswordChangeRateLimitExceededException.detail,
    )
