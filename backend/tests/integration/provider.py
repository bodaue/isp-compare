import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user import User
from isp_compare.services.password_hasher import PasswordHasher

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def admin_user(session: AsyncSession) -> User:
    """Create an admin user for testing."""
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
    await session.flush()
    return user


@pytest.fixture
async def auth_token(client: AsyncClient, admin_user: User) -> str:
    """Login and get an authentication token."""
    response = await client.post(
        "/auth/login", json={"username": admin_user.username, "password": "Admin123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


async def test_provider_api_crud(client: AsyncClient, auth_token: str) -> None:
    """
    End-to-end integration test of the Provider API.

    Tests the complete CRUD operations flow using the HTTP endpoints.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Create a provider
    create_data = {
        "name": "Test ISP Provider",
        "description": "A provider for testing",
        "website": "https://example.com",
        "logo_url": "https://example.com/logo.png",
    }

    create_response = await client.post("/providers", json=create_data, headers=headers)
    assert create_response.status_code == 201, (
        f"Create failed: {create_response.json()}"
    )

    created_provider = create_response.json()
    provider_id = created_provider["id"]

    # Verify the provider was created with correct data
    assert created_provider["name"] == create_data["name"]
    assert created_provider["description"] == create_data["description"]
    assert created_provider["website"] == create_data["website"]
    assert created_provider["logo_url"] == create_data["logo_url"]

    # 2. Get the provider
    get_response = await client.get(f"/providers/{provider_id}")
    assert get_response.status_code == 200, f"Get failed: {get_response.json()}"

    retrieved_provider = get_response.json()
    assert retrieved_provider["id"] == provider_id
    assert retrieved_provider["name"] == create_data["name"]
    assert retrieved_provider["description"] == create_data["description"]
