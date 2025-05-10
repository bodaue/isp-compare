import uuid

from httpx import AsyncClient

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.models import Review
from isp_compare.models.provider import Provider
from tests.utils import check_response


async def test_get_provider_success(client: AsyncClient, provider: Provider) -> None:
    response = await client.get(f"/providers/{provider.id}")
    data = check_response(response, 200)

    assert data["id"] == str(provider.id)
    assert data["name"] == provider.name
    assert data["description"] == provider.description
    assert data["website"] == provider.website
    assert data["logo_url"] == provider.logo_url
    assert data["rating"] == provider.rating


async def test_get_provider_with_reviews_count(
    client: AsyncClient,
    provider: Provider,
    review: Review,
    review_2: Review,
) -> None:
    response = await client.get(f"/providers/{provider.id}")
    data = check_response(response, 200)

    assert data["id"] == str(provider.id)
    assert data["name"] == provider.name
    assert data["description"] == provider.description
    assert data["website"] == provider.website
    assert data["logo_url"] == provider.logo_url
    assert data["rating"] == provider.rating
    assert data["reviews_count"] == 2


async def test_get_provider_as_authenticated_user(
    auth_client: AsyncClient, provider: Provider
) -> None:
    response = await auth_client.get(f"/providers/{provider.id}")
    data = check_response(response, 200)

    assert data["id"] == str(provider.id)
    assert data["name"] == provider.name


async def test_get_provider_as_admin(
    admin_client: AsyncClient, provider: Provider
) -> None:
    response = await admin_client.get(f"/providers/{provider.id}")
    data = check_response(response, 200)

    assert data["id"] == str(provider.id)
    assert data["name"] == provider.name


async def test_get_provider_not_found(client: AsyncClient) -> None:
    non_existent_id = str(uuid.uuid4())
    response = await client.get(f"/providers/{non_existent_id}")
    check_response(response, 404, expected_detail=ProviderNotFoundException.detail)


async def test_get_provider_invalid_id(client: AsyncClient) -> None:
    invalid_id = "not-a-uuid"
    response = await client.get(f"/providers/{invalid_id}")
    check_response(response, 422)
