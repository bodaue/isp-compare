from httpx import AsyncClient

from isp_compare.models import User
from tests.utils import check_response


async def test_logout_success(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/auth/logout")
    data = check_response(response, 200)

    assert data["message"] == "Successfully logged out"
    assert "refresh_token" not in response.cookies


async def test_logout_without_token(client: AsyncClient) -> None:
    response = await client.post("/auth/logout")
    data = check_response(response, 200)

    assert data["message"] == "Successfully logged out"
    assert "refresh_token" not in response.cookies


async def test_logout_with_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    data = check_response(response, 200)

    assert data["message"] == "Successfully logged out"
    assert "refresh_token" not in response.cookies


async def test_logout_clears_cookies(
    auth_client: AsyncClient, regular_user: User
) -> None:
    login_response = await auth_client.post(
        "/auth/login",
        json={"username": regular_user.username, "password": "Password123!"},
    )
    check_response(login_response, 200)
    assert "refresh_token" in login_response.cookies

    logout_response = await auth_client.post("/auth/logout")
    check_response(logout_response, 200)
    assert "refresh_token" not in logout_response.cookies
