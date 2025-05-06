import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    TariffNotFoundException,
)
from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_update_tariff_success(admin_client: AsyncClient, tariff: Tariff) -> None:
    update_data = {
        "name": "Updated Tariff Name",
        "description": "This is an updated description",
        "price": 49.99,
        "speed": 300,
        "has_tv": False,
        "additional_services": {
            "vpn": False,
            "static_ip": True,
            "parental_control": True,
        },
    }

    response = await admin_client.patch(f"/tariffs/{tariff.id}", json=update_data)
    data = check_response(response, 200)

    assert data["id"] == str(tariff.id)
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert float(data["price"]) == update_data["price"]
    assert data["speed"] == update_data["speed"]
    assert data["has_tv"] == update_data["has_tv"]
    assert data["additional_services"] == update_data["additional_services"]

    # Fields that weren't updated
    assert data["connection_type"] == tariff.connection_type.value
    assert data["has_phone"] == tariff.has_phone
    assert float(data["connection_cost"]) == tariff.connection_cost
    assert data["contract_period"] == tariff.contract_period
    assert data["provider_id"] == str(tariff.provider_id)


async def test_update_tariff_unauthorized(client: AsyncClient, tariff: Tariff) -> None:
    update_data = {
        "name": "Unauthorized Update",
    }

    response = await client.patch(f"/tariffs/{tariff.id}", json=update_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_update_tariff_regular_user(
    auth_client: AsyncClient, tariff: Tariff
) -> None:
    update_data = {
        "name": "Regular User Update",
    }

    response = await auth_client.patch(f"/tariffs/{tariff.id}", json=update_data)
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)


async def test_update_tariff_not_found(admin_client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())
    update_data = {
        "name": "Non-existent Tariff",
    }

    response = await admin_client.patch(f"/tariffs/{non_existent_id}", json=update_data)
    check_response(response, 404, expected_detail=TariffNotFoundException.detail)


async def test_update_tariff_invalid_data(
    admin_client: AsyncClient, tariff: Tariff
) -> None:
    # Negative price
    invalid_data = {
        "price": -19.99,
    }
    response = await admin_client.patch(f"/tariffs/{tariff.id}", json=invalid_data)
    check_response(response, 422)

    # Zero speed
    invalid_data = {
        "speed": 0,
    }
    response = await admin_client.patch(f"/tariffs/{tariff.id}", json=invalid_data)
    check_response(response, 422)

    # Invalid connection type
    invalid_data = {
        "connection_type": "INVALID_TYPE",
    }
    response = await admin_client.patch(f"/tariffs/{tariff.id}", json=invalid_data)
    check_response(response, 422)


async def test_update_tariff_partial(admin_client: AsyncClient, tariff: Tariff) -> None:
    update_data = {"name": "Partially Updated Tariff", "is_active": False}
    response = await admin_client.patch(f"/tariffs/{tariff.id}", json=update_data)
    data = check_response(response, 200)

    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]
    assert data["description"] == tariff.description
    assert float(data["price"]) == float(tariff.price)
    assert data["speed"] == tariff.speed
