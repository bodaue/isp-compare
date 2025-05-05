import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user import User
from isp_compare.services.password_hasher import PasswordHasher


@pytest.fixture
async def admin_user(session: AsyncSession) -> User:
    password_hasher = PasswordHasher()
    hashed_password = password_hasher.hash("Admin123")

    user = User(
        fullname="Admin User",
        username="admin",
        hashed_password=hashed_password,
        email="admin@example.com",
        is_admin=True,
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def regular_user(session: AsyncSession) -> User:
    password_hasher = PasswordHasher()
    hashed_password = password_hasher.hash("Password123!")

    user = User(
        fullname="Regular User",
        username="user",
        hashed_password=hashed_password,
        email="user@example.com",
        is_admin=False,
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def user_token(client: AsyncClient, regular_user: User) -> str:
    response = await client.post(
        "/auth/login",
        json={"username": regular_user.username, "password": "Password123!"},
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user: User) -> str:
    response = await client.post(
        "/auth/login", json={"username": admin_user.username, "password": "Admin123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]
