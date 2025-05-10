from uuid import UUID

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.schemas.provider import (
    ProviderResponse,
)


class ProviderService:
    def __init__(
        self,
        provider_repository: ProviderRepository,
    ) -> None:
        self._provider_repository = provider_repository

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
        providers_with_counts = await self._provider_repository.get_all()
        return [
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
