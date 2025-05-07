from httpx import AsyncClient

from isp_compare.core.exceptions import (
    RefreshTokenMissingException,
    TokenRefreshRateLimitExceededException,
)
from isp_compare.models import User
from tests.utils import check_response


async def test_refresh_token_success(
    client: AsyncClient, user_token: str, regular_user: User
) -> None:
    login_response = await client.post(
        "/auth/login",
        json={"username": regular_user.username, "password": "Password123!"},
    )
    check_response(login_response, 200)

    refresh_response = await client.post("/auth/refresh")
    data = check_response(refresh_response, 200)

    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105
    assert "refresh_token" in refresh_response.cookies


async def test_refresh_token_missing(client: AsyncClient) -> None:
    response = await client.post("/auth/refresh")
    check_response(response, 401, expected_detail=RefreshTokenMissingException.detail)


async def test_refresh_token_after_logout(auth_client: AsyncClient) -> None:
    logout_response = await auth_client.post(
        "/auth/logout",
    )
    check_response(logout_response, 200)

    refresh_response = await auth_client.post("/auth/refresh")
    check_response(
        refresh_response, 401, expected_detail=RefreshTokenMissingException.detail
    )


async def test_refresh_token_rate_limit(
    client: AsyncClient, regular_user: User
) -> None:
    login_response = await client.post(
        "/auth/login",
        json={"username": regular_user.username, "password": "Password123!"},
    )
    check_response(login_response, 200)

    for _ in range(10):
        refresh_response = await client.post("/auth/refresh")
        check_response(refresh_response, 200)

    exceeded_response = await client.post("/auth/refresh")
    check_response(
        exceeded_response,
        429,
        expected_detail=TokenRefreshRateLimitExceededException.detail,
    )
