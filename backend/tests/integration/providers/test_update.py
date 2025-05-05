from uuid import uuid4

from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    ProviderNotFoundException,
)
from isp_compare.models.provider import Provider


async def test_update_provider_success(
    admin_client: AsyncClient, provider: Provider
) -> None:
    update_data = {
        "name": "Updated Provider Name",
        "description": "This is an updated description",
        "website": "https://updated-provider.com/",
    }

    response = await admin_client.patch(f"/providers/{provider.id}", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(provider.id)
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["website"] == update_data["website"]
    assert data["logo_url"] == provider.logo_url  # Unchanged field


async def test_update_provider_unauthorized(
    client: AsyncClient, provider: Provider
) -> None:
    update_data = {
        "name": "Unauthorized Update",
    }

    response = await client.patch(f"/providers/{provider.id}", json=update_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_update_provider_regular_user(
    auth_client: AsyncClient, provider: Provider
) -> None:
    update_data = {
        "name": "Regular User Update",
    }

    response = await auth_client.patch(f"/providers/{provider.id}", json=update_data)
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)


async def test_update_provider_not_found(
    admin_client: AsyncClient, provider: Provider
) -> None:
    non_existent_id = str(uuid4())
    update_data = {
        "name": "Non-existent Provider",
    }

    response = await admin_client.patch(
        f"/providers/{non_existent_id}", json=update_data
    )
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_update_provider_invalid_data(
    admin_client: AsyncClient, provider: Provider
) -> None:
    invalid_data = {
        "website": "not-a-valid-url",
    }
    response = await admin_client.patch(f"/providers/{provider.id}", json=invalid_data)
    check_response(response, 422)

    invalid_data = {
        "name": "A" * 300,  # Exceeds max length
    }
    response = await admin_client.patch(f"/providers/{provider.id}", json=invalid_data)
    check_response(response, 422)


async def test_update_provider_partial(
    admin_client: AsyncClient, provider: Provider
) -> None:
    update_data = {
        "name": "Partially Updated Provider",
    }
    response = await admin_client.patch(f"/providers/{provider.id}", json=update_data)
    data = check_response(response, 200)

    assert data["name"] == update_data["name"]
    assert data["description"] == provider.description
    assert data["website"] == provider.website
    assert data["logo_url"] == provider.logo_url
