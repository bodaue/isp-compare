from httpx import AsyncClient
from tests.utils import check_response

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
)


async def test_create_provider_success(admin_client: AsyncClient) -> None:
    create_data = {
        "name": "Test Provider",
        "description": "A test provider description",
        "website": "https://testprovider.com/",
        "logo_url": "https://testprovider.com/logo.png",
    }

    response = await admin_client.post("/providers", json=create_data)
    data = check_response(response, 201)

    assert data["name"] == create_data["name"]
    assert data["description"] == create_data["description"]
    assert data["website"] == create_data["website"]
    assert data["logo_url"] == create_data["logo_url"]
    assert "id" in data
    assert "rating" in data
    assert data["rating"] is None


async def test_create_provider_unauthorized(client: AsyncClient) -> None:
    create_data = {
        "name": "Unauthorized Provider",
        "description": "This should fail",
    }

    response = await client.post("/providers", json=create_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_create_provider_regular_user(auth_client: AsyncClient) -> None:
    create_data = {
        "name": "Regular User Provider",
        "description": "This should fail without admin privileges",
    }

    response = await auth_client.post("/providers", json=create_data)
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)


async def test_create_provider_invalid_data(admin_client: AsyncClient) -> None:
    invalid_data = {
        "description": "Missing name field",
    }
    response = await admin_client.post("/providers", json=invalid_data)
    check_response(response, 422)

    invalid_data = {
        "name": "Invalid Website Provider",
        "website": "not-a-valid-url",
    }
    response = await admin_client.post("/providers", json=invalid_data)
    check_response(response, 422)

    invalid_data = {
        "name": "A" * 300,
    }
    response = await admin_client.post("/providers", json=invalid_data)
    check_response(response, 422)


async def test_create_provider_minimal_data(admin_client: AsyncClient) -> None:
    minimal_data = {
        "name": "Minimal Provider",
    }

    response = await admin_client.post("/providers", json=minimal_data)
    check_response(response, 201)

    provider_data = response.json()
    assert provider_data["name"] == minimal_data["name"]
    assert provider_data["description"] is None
    assert provider_data["website"] is None
    assert provider_data["logo_url"] is None
