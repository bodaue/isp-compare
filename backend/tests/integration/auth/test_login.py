from httpx import AsyncClient
from redis.asyncio import Redis
from utils import check_response

from isp_compare.core.exceptions import (
    InvalidCredentialsException,
    LoginRateLimitExceededException,
)
from isp_compare.models.user import User


async def test_login_success(client: AsyncClient, regular_user: User) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "Password123!",
    }

    response = await client.post("/auth/login", json=login_data)
    data = check_response(response, 200)

    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105
    assert "refresh_token" in response.cookies


async def test_login_admin_success(client: AsyncClient, admin_user: User) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "Admin123",
    }

    response = await client.post("/auth/login", json=login_data)
    data = check_response(response, 200)

    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105
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


async def test_login_rate_limit(
    client: AsyncClient, regular_user: User, redis_client: Redis
) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "WrongPassword123",
    }

    for _ in range(5):
        await client.post("/auth/login", json=login_data)

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
