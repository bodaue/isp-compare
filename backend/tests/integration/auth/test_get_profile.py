from httpx import AsyncClient
from isp_compare.core.exceptions import (
    InvalidTokenException,
)
from isp_compare.models.user import User
from tests.utils import check_response


async def test_get_profile_success(
    auth_client: AsyncClient, regular_user: User
) -> None:
    response = await auth_client.get("/users/me")
    data = check_response(response, 200)

    assert data["id"] == str(regular_user.id)
    assert data["fullname"] == regular_user.fullname
    assert data["username"] == regular_user.username
    assert data["email"] == regular_user.email


async def test_get_profile_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/users/me")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)
