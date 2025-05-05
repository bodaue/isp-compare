from httpx import AsyncClient
from utils import check_response

from isp_compare.core.exceptions import InvalidTokenException


async def test_provider_api_crud(admin_client: AsyncClient) -> None:
    create_data = {
        "name": "Test ISP Provider",
        "description": "A provider for testing",
        "website": "https://example.com/",
        "logo_url": "https://example.com/logo.png",
    }
    response = await admin_client.post("/providers", json=create_data)
    check_response(response, 201)


async def test_unauthorized(client: AsyncClient) -> None:
    create_data = {
        "name": "Test ISP Provider",
        "description": "A provider for testing",
        "website": "https://example.com/",
        "logo_url": "https://example.com/logo.png",
    }
    response = await client.post("/providers", json=create_data)
    check_response(response, 401, expected_detail=InvalidTokenException.detail)
