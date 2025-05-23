from httpx import AsyncClient

from isp_compare.core.exceptions import (
    InvalidCredentialsException,
    LoginRateLimitExceededException,
)
from isp_compare.models.user import User
from tests.utils import check_response


async def test_login_success(client: AsyncClient, regular_user: User) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "Password123!",
    }

    response = await client.post("/auth/login", json=login_data)
    data = check_response(response, 200)

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


async def test_login_admin_success(client: AsyncClient, admin_user: User) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "AdminPassword123!",
    }

    response = await client.post("/auth/login", json=login_data)
    data = check_response(response, 200)

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


async def test_login_invalid_username(client: AsyncClient) -> None:
    login_data = {
        "username": "nonexistentuser",
        "password": "Password123",
    }

    response = await client.post("/auth/login", json=login_data)
    check_response(response, 401, expected_detail=InvalidCredentialsException.detail)


async def test_login_invalid_password(client: AsyncClient, regular_user: User) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "WrongPassword123",
    }

    response = await client.post("/auth/login", json=login_data)
    check_response(response, 401, expected_detail=InvalidCredentialsException.detail)


async def test_login_rate_limit_by_username(
    client: AsyncClient, regular_user: User
) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "WrongPassword123",
    }

    for i in range(10):
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 401, (
            f"Attempt {i + 1}: expected 401, got {response.status_code}"
        )

    response = await client.post("/auth/login", json=login_data)
    check_response(
        response, 429, expected_detail=LoginRateLimitExceededException.detail
    )

    correct_login = {
        "username": regular_user.username,
        "password": "Password123!",
    }
    response = await client.post("/auth/login", json=correct_login)
    check_response(
        response, 429, expected_detail=LoginRateLimitExceededException.detail
    )


async def test_login_rate_limit_different_usernames(
    client: AsyncClient, regular_user: User, admin_user: User
) -> None:
    wrong_login_1 = {
        "username": regular_user.username,
        "password": "WrongPassword123",
    }

    for _ in range(10):
        await client.post("/auth/login", json=wrong_login_1)

    response = await client.post("/auth/login", json=wrong_login_1)
    check_response(
        response, 429, expected_detail=LoginRateLimitExceededException.detail
    )

    correct_login_2 = {
        "username": admin_user.username,
        "password": "AdminPassword123!",
    }
    response = await client.post("/auth/login", json=correct_login_2)
    check_response(response, 200)


async def test_login_successful_after_failed_attempts(
    client: AsyncClient, regular_user: User
) -> None:
    wrong_login = {
        "username": regular_user.username,
        "password": "WrongPassword123",
    }

    for _ in range(5):
        response = await client.post("/auth/login", json=wrong_login)
        assert response.status_code == 401

    correct_login = {
        "username": regular_user.username,
        "password": "Password123!",
    }
    response = await client.post("/auth/login", json=correct_login)
    check_response(response, 200)

    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies
