from httpx import AsyncClient

from isp_compare.models import User
from utils import check_response

from isp_compare.core.exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)


async def test_register_user_success(client: AsyncClient) -> None:
    user_data = {
        "fullname": "Test User",
        "username": "testuser",
        "password": "Password123",
        "email": "test@example.com",
    }

    response = await client.post("/auth/register", json=user_data)
    data = check_response(response, 201)

    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105
    assert "refresh_token" in response.cookies


async def test_register_with_weak_password(client: AsyncClient) -> None:
    user_data = {
        "fullname": "Weak Password User",
        "username": "weakpassword",
        "password": "password",
        "email": "weak@example.com",
    }

    response = await client.post("/auth/register", json=user_data)
    check_response(response, 422)


async def test_register_with_existing_username(
    client: AsyncClient, regular_user: User
) -> None:
    user_data = {
        "fullname": "Duplicate Username",
        "username": "user",
        "password": "Password123",
        "email": "different@example.com",
    }

    response = await client.post("/auth/register", json=user_data)
    check_response(response, 409, expected_detail=UsernameAlreadyExistsException.detail)


async def test_register_with_existing_email(
    client: AsyncClient, regular_user: User
) -> None:
    user_data = {
        "fullname": "Duplicate Email",
        "username": "differentuser",
        "password": "Password123",
        "email": "user@example.com",
    }

    response = await client.post("/auth/register", json=user_data)
    check_response(response, 409, expected_detail=EmailAlreadyExistsException.detail)


async def test_register_with_invalid_data(client: AsyncClient) -> None:
    invalid_data = {
        "username": "incomplete",
        "password": "Password123",
    }
    response = await client.post("/auth/register", json=invalid_data)
    check_response(response, 422)

    invalid_data = {
        "fullname": "Invalid Email",
        "username": "invalidemail",
        "password": "Password123",
        "email": "not-an-email",
    }
    response = await client.post("/auth/register", json=invalid_data)
    check_response(response, 422)

    invalid_data = {
        "fullname": "Short Username",
        "username": "abc",
        "password": "Password123",
        "email": "short@example.com",
    }
    response = await client.post("/auth/register", json=invalid_data)
    check_response(response, 422)
