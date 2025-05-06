import uuid

from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    ProviderNotFoundException,
)
from isp_compare.models.provider import Provider


async def test_create_tariff_success(
    admin_client: AsyncClient, provider: Provider
) -> None:
    create_data = {
        "name": "New Tariff",
        "description": "A new test tariff",
        "price": 39.99,
        "speed": 200,
        "connection_type": "FTTH",
        "has_tv": True,
        "has_phone": False,
        "additional_services": {"vpn": True, "static_ip": True},
        "connection_cost": 15.00,
        "contract_period": 24,
        "is_active": True,
    }

    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=create_data
    )
    data = check_response(response, 201)

    assert data["name"] == create_data["name"]
    assert data["description"] == create_data["description"]
    assert float(data["price"]) == create_data["price"]
    assert data["speed"] == create_data["speed"]
    assert data["connection_type"] == create_data["connection_type"]
    assert data["has_tv"] == create_data["has_tv"]
    assert data["has_phone"] == create_data["has_phone"]
    assert data["additional_services"] == create_data["additional_services"]
    assert float(data["connection_cost"]) == create_data["connection_cost"]
    assert data["contract_period"] == create_data["contract_period"]
    assert data["is_active"] == create_data["is_active"]
    assert data["provider_id"] == str(provider.id)
    assert "id" in data


async def test_create_tariff_unauthorized(
    client: AsyncClient, provider: Provider
) -> None:
    create_data = {
        "name": "Unauthorized Tariff",
        "price": 19.99,
        "speed": 50,
        "connection_type": "ADSL",
    }

    response = await client.post(f"/providers/{provider.id}/tariffs", json=create_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)


async def test_create_tariff_regular_user(
    auth_client: AsyncClient, provider: Provider
) -> None:
    create_data = {
        "name": "Regular User Tariff",
        "price": 19.99,
        "speed": 50,
        "connection_type": "ADSL",
    }

    response = await auth_client.post(
        f"/providers/{provider.id}/tariffs", json=create_data
    )
    check_response(response, 403, expected_detail=AdminAccessDeniedException.detail)


async def test_create_tariff_nonexistent_provider(admin_client: AsyncClient) -> None:
    non_existent_provider_id = str(uuid.uuid4())

    create_data = {
        "name": "Nonexistent Provider Tariff",
        "price": 19.99,
        "speed": 50,
        "connection_type": "ADSL",
    }

    response = await admin_client.post(
        f"/providers/{non_existent_provider_id}/tariffs", json=create_data
    )
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_create_tariff_invalid_data(
    admin_client: AsyncClient, provider: Provider
) -> None:
    # Missing required fields
    invalid_data = {"name": "Invalid Tariff"}
    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=invalid_data
    )
    check_response(response, 422)

    # Invalid connection type
    invalid_data = {
        "name": "Invalid Connection Type",
        "price": 19.99,
        "speed": 50,
        "connection_type": "INVALID_TYPE",
    }
    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=invalid_data
    )
    check_response(response, 422)

    # Negative price
    invalid_data = {
        "name": "Negative Price",
        "price": -19.99,
        "speed": 50,
        "connection_type": "ADSL",
    }
    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=invalid_data
    )
    check_response(response, 422)

    # Zero speed
    invalid_data = {
        "name": "Zero Speed",
        "price": 19.99,
        "speed": 0,
        "connection_type": "ADSL",
    }
    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=invalid_data
    )
    check_response(response, 422)


async def test_create_tariff_minimal_data(
    admin_client: AsyncClient, provider: Provider
) -> None:
    minimal_data = {
        "name": "Minimal Tariff",
        "price": 19.99,
        "speed": 50,
        "connection_type": "ADSL",
    }

    response = await admin_client.post(
        f"/providers/{provider.id}/tariffs", json=minimal_data
    )
    data = check_response(response, 201)

    assert data["name"] == minimal_data["name"]
    assert float(data["price"]) == minimal_data["price"]
    assert data["speed"] == minimal_data["speed"]
    assert data["connection_type"] == minimal_data["connection_type"]
    assert data["description"] is None
    assert data["has_tv"] is False
    assert data["has_phone"] is False
    assert data["additional_services"] is None
    assert float(data["connection_cost"]) == 0.0
    assert data["contract_period"] is None
    assert data["is_active"] is True
