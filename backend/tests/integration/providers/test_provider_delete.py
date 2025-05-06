from uuid import uuid4

from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    ProviderNotFoundException,
)
from isp_compare.models.provider import Provider


async def test_delete_provider_success(
    admin_client: AsyncClient, provider: Provider
) -> None:
    response = await admin_client.delete(f"/providers/{provider.id}")
    check_response(response, 204)

    response = await admin_client.get(f"/providers/{provider.id}")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_delete_provider_unauthorized(
    client: AsyncClient, provider: Provider
) -> None:
    response = await client.delete(f"/providers/{provider.id}")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_delete_provider_regular_user(
    auth_client: AsyncClient, provider: Provider
) -> None:
    response = await auth_client.delete(f"/providers/{provider.id}")
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)

    response = await auth_client.get(f"/providers/{provider.id}")
    check_response(response, 200)


async def test_delete_provider_not_found(admin_client: AsyncClient) -> None:
    non_existent_id = str(uuid4())
    response = await admin_client.delete(f"/providers/{non_existent_id}")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)
