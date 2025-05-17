import json
from uuid import UUID

from redis.asyncio import Redis

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.schemas.provider import (
    ProviderResponse,
)


class ProviderService:
    def __init__(
        self,
        provider_repository: ProviderRepository,
        redis_client: Redis,
    ) -> None:
        self._provider_repository = provider_repository
        self._redis_client = redis_client

    async def get_provider(self, provider_id: UUID) -> ProviderResponse:
        result = await self._provider_repository.get_by_id(provider_id)

        if not result:
            raise ProviderNotFoundException

        provider, reviews_count = result
        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            description=provider.description,
            website=provider.website,
            phone=provider.phone,
            logo_url=provider.logo_url,
            rating=provider.rating,
            reviews_count=reviews_count,
        )

    async def get_all_providers(self) -> list[ProviderResponse]:
        cache_key = "all_providers"

        cached_data = await self._redis_client.get(cache_key)
        if cached_data:
            try:
                providers_data = json.loads(cached_data)
                return [ProviderResponse(**provider) for provider in providers_data]
            except (json.JSONDecodeError, TypeError, KeyError):
                pass
        providers_with_counts = await self._provider_repository.get_all()

        providers_response = [
            ProviderResponse(
                id=provider.id,
                name=provider.name,
                description=provider.description,
                website=provider.website,
                phone=provider.phone,
                logo_url=provider.logo_url,
                rating=provider.rating,
                reviews_count=reviews_count,
            )
            for provider, reviews_count in providers_with_counts
        ]

        serialized_data = json.dumps(
            [provider.model_dump() for provider in providers_response],
            default=str,
        )
        await self._redis_client.set(cache_key, serialized_data, ex=1800)

        return providers_response
