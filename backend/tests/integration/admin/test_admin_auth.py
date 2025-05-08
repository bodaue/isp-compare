import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user import User
from isp_compare.services.password_hasher import PasswordHasher


@pytest.fixture
async def admin_for_sqladmin(session: AsyncSession) -> User:
    password_hasher = PasswordHasher()
    hashed_password = password_hasher.hash("AdminPassword123!")

    admin = User(
        fullname="Admin User",
        username="admin",
        hashed_password=hashed_password,
        email="admin@example.com",
        is_admin=True,
    )
    session.add(admin)
    await session.commit()
    return admin


@pytest.fixture
async def regular_user_for_sqladmin(session: AsyncSession) -> User:
    password_hasher = PasswordHasher()
    hashed_password = password_hasher.hash("UserPassword123!")

    user = User(
        fullname="Regular User",
        username="regularuser",
        hashed_password=hashed_password,
        email="user@example.com",
        is_admin=False,
    )
    session.add(user)
    await session.commit()
    return user


async def test_admin_login_success(
    client: AsyncClient, admin_for_sqladmin: User
) -> None:
    login_data = {
        "username": admin_for_sqladmin.username,
        "password": "AdminPassword123!",
    }

    response = await client.post("/admin/login", data=login_data)
    assert response.status_code == 302
    assert "session" in response.cookies


async def test_admin_login_wrong_password(
    client: AsyncClient, admin_for_sqladmin: User
) -> None:
    login_data = {
        "username": admin_for_sqladmin.username,
        "password": "WrongPassword",
    }

    response = await client.post("/admin/login", data=login_data)
    assert response.status_code == 400


async def test_admin_login_regular_user(
    client: AsyncClient, regular_user_for_sqladmin: User
) -> None:
    login_data = {
        "username": regular_user_for_sqladmin.username,
        "password": "UserPassword123!",
    }

    response = await client.post("/admin/login", data=login_data)
    assert response.status_code == 400


async def test_admin_logout(client: AsyncClient, admin_for_sqladmin: User) -> None:
    login_data = {
        "username": admin_for_sqladmin.username,
        "password": "AdminPassword123!",
    }
    login_response = await client.post("/admin/login", data=login_data)
    assert login_response.status_code == 302

    response = await client.get("/admin/logout")
    assert response.status_code == 302

    logout_cookies = response.cookies
    login_cookies = login_response.cookies

    if "session" in logout_cookies and "session" in login_cookies:
        assert logout_cookies["session"] != login_cookies["session"]


async def test_admin_access_without_auth(client: AsyncClient) -> None:
    response = await client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login" in response.headers.get("location", "")

    response = await client.get("/admin/providers/list")
    assert response.status_code == 302
    assert "/admin/login" in response.headers.get("location", "")


async def test_admin_access_after_login(
    client: AsyncClient, admin_for_sqladmin: User
) -> None:
    login_data = {
        "username": admin_for_sqladmin.username,
        "password": "AdminPassword123!",
    }

    login_response = await client.post("/admin/login", data=login_data)
    assert login_response.status_code == 302

    response = await client.get("/admin/")
    assert response.status_code == 200

    response = await client.get("/admin/provider/list")
    assert response.status_code == 200
