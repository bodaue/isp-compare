import uuid

from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    TariffNotFoundException,
)
from isp_compare.models.tariff import Tariff


async def test_delete_tariff_success(admin_client: AsyncClient, tariff: Tariff) -> None:
    response = await admin_client.delete(f"/tariffs/{tariff.id}")
    check_response(response, 204)

    # Verify it's deleted
    response = await admin_client.get(f"/tariffs/{tariff.id}")
    check_response(response, 404, expected_detail=TariffNotFoundException.detail)


async def test_delete_tariff_unauthorized(client: AsyncClient, tariff: Tariff) -> None:
    response = await client.delete(f"/tariffs/{tariff.id}")
    check_response(response, 401, expected_detail=InvalidTokenException.detail)

    response = await client.get(f"/tariffs/{tariff.id}")
    check_response(response, 200)


async def test_delete_tariff_regular_user(
    auth_client: AsyncClient, tariff: Tariff
) -> None:
    response = await auth_client.delete(f"/tariffs/{tariff.id}")
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)

    response = await auth_client.get(f"/tariffs/{tariff.id}")
    check_response(response, 200)


async def test_delete_tariff_not_found(admin_client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = await admin_client.delete(f"/tariffs/{non_existent_id}")
    check_response(response, 404, expected_detail=TariffNotFoundException.detail)
