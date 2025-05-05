from httpx import AsyncClient


async def test_provider_api_crud(admin_client: AsyncClient) -> None:
    create_data = {
        "name": "Test ISP Provider",
        "description": "A provider for testing",
        "website": "https://example.com/",
        "logo_url": "https://example.com/logo.png",
    }
    create_response = await admin_client.post("/providers", json=create_data)
    assert create_response.status_code == 201, (
        f"Create failed: {create_response.json()}"
    )
