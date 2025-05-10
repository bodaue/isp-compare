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

    async def get_provider(self, provider_id: UUID) -> ProviderResponse | None:
        provider = await self._provider_repository.get_by_id(provider_id)

        if not provider:
            raise ProviderNotFoundException
        return ProviderResponse.model_validate(provider)

    async def get_all_providers(
        self, limit: int, offset: int
    ) -> list[ProviderResponse]:
        providers = await self._provider_repository.get_all(limit, offset)
        return [ProviderResponse.model_validate(provider) for provider in providers]
