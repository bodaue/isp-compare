from uuid import UUID

from isp_compare.core.exceptions import ProviderNotFoundException
from isp_compare.models.provider import Provider
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.transaction_manager import TransactionManager


class ProviderService:
    def __init__(
        self,
        provider_repository: ProviderRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
    ) -> None:
        self._provider_repository = provider_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider

    async def create_provider(self, data: ProviderCreate) -> ProviderResponse:
        await self._identity_provider.ensure_is_admin()

        provider = Provider(**data.model_dump())

        await self._provider_repository.create(provider)
        await self._transaction_manager.commit()

        return ProviderResponse.model_validate(provider)

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

    async def update_provider(
        self,
        provider_id: UUID,
        data: ProviderUpdate,
    ) -> ProviderResponse:
        await self._identity_provider.ensure_is_admin()

        provider = await self._provider_repository.get_by_id(
            provider_id, for_update=True
        )
        if not provider:
            raise ProviderNotFoundException

        update_data = data.model_dump(exclude_unset=True)

        await self._provider_repository.update(provider_id, update_data)
        await self._transaction_manager.commit()
        await self._transaction_manager.refresh(provider)

        return ProviderResponse.model_validate(provider)

    async def delete_provider(self, provider_id: UUID) -> None:
        await self._identity_provider.ensure_is_admin()

        provider = await self._provider_repository.get_by_id(
            provider_id, for_update=True
        )
        if not provider:
            raise ProviderNotFoundException

        await self._provider_repository.delete(provider)
        await self._transaction_manager.commit()
