import asyncio
import json
from uuid import UUID

from redis.asyncio import Redis

from isp_compare.core.exceptions import (
    AppException,
    ProviderNotFoundException,
    TariffNotFoundException,
)
from isp_compare.models import SearchHistory, User
from isp_compare.models.tariff import Tariff
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.search_history import SearchHistoryRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff import (
    TariffCreate,
    TariffResponse,
    TariffSearchParams,
    TariffUpdate,
)
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.transaction_manager import TransactionManager


class TariffService:
    def __init__(
        self,
        tariff_repository: TariffRepository,
        provider_repository: ProviderRepository,
        search_history_repository: SearchHistoryRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
        redis_client: Redis,
    ) -> None:
        self._tariff_repository = tariff_repository
        self._provider_repository = provider_repository
        self._search_history_repository = search_history_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider
        self._redis_client = redis_client

    async def create_tariff(
        self, provider_id: UUID, data: TariffCreate
    ) -> TariffResponse:
        await self._identity_provider.ensure_is_admin()

        provider = await self._provider_repository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundException

        tariff = Tariff(**data.model_dump(), provider_id=provider_id)
        await self._tariff_repository.create(tariff)
        await self._transaction_manager.commit()
        return TariffResponse.model_validate(tariff)

    async def get_tariff(self, tariff_id: UUID) -> TariffResponse:
        tariff = await self._tariff_repository.get_by_id(tariff_id)
        if not tariff:
            raise TariffNotFoundException
        return TariffResponse.model_validate(tariff)

    async def get_all_tariffs(self, limit: int, offset: int) -> list[TariffResponse]:
        cache_key = "all_active_tariffs"

        cached_data = await self._redis_client.get(cache_key)

        if cached_data:
            try:
                all_tariffs_data = json.loads(cached_data)

                all_tariffs = [TariffResponse(**tariff) for tariff in all_tariffs_data]
                return all_tariffs[offset : offset + limit]
            except (json.JSONDecodeError, TypeError, KeyError, IndexError):
                pass

        all_tariffs = await self._tariff_repository.get_all(limit=1000, offset=0)

        all_tariff_responses = [
            TariffResponse.model_validate(tariff) for tariff in all_tariffs
        ]

        serialized_data = json.dumps(
            [tariff.model_dump() for tariff in all_tariff_responses],
            default=str,
        )
        await self._redis_client.set(cache_key, serialized_data, ex=600)

        return all_tariff_responses[offset : offset + limit]

    async def get_provider_tariffs(
        self, provider_id: UUID, limit: int, offset: int
    ) -> list[TariffResponse]:
        provider_result = await self._provider_repository.get_by_id(provider_id)

        if not provider_result:
            raise ProviderNotFoundException

        tariffs = await self._tariff_repository.get_by_provider(
            provider_id, limit, offset
        )

        return [TariffResponse.model_validate(tariff) for tariff in tariffs]

    async def update_tariff(
        self, tariff_id: UUID, data: TariffUpdate
    ) -> TariffResponse:
        await self._identity_provider.ensure_is_admin()

        tariff = await self._tariff_repository.get_by_id(tariff_id, for_update=True)
        if not tariff:
            raise TariffNotFoundException

        update_data = data.model_dump(exclude_unset=True)
        await self._tariff_repository.update(tariff_id, update_data)
        await self._transaction_manager.commit()
        await self._transaction_manager.refresh(tariff)
        return TariffResponse.model_validate(tariff)

    async def delete_tariff(self, tariff_id: UUID) -> None:
        await self._identity_provider.ensure_is_admin()

        tariff = await self._tariff_repository.get_by_id(tariff_id, for_update=True)
        if not tariff:
            raise TariffNotFoundException

        await self._tariff_repository.delete(tariff)
        await self._transaction_manager.commit()

    async def search_tariffs(
        self, search_params: TariffSearchParams
    ) -> list[TariffResponse]:
        search_task = self._tariff_repository.search(
            min_price=search_params.min_price,
            max_price=search_params.max_price,
            min_speed=search_params.min_speed,
            max_speed=search_params.max_speed,
            has_tv=search_params.has_tv,
            has_phone=search_params.has_phone,
            limit=search_params.limit,
            offset=search_params.offset,
        )

        user_task = self._get_user_safe()

        tariffs, user = await asyncio.gather(search_task, user_task)

        tariff_responses = [TariffResponse.model_validate(tariff) for tariff in tariffs]

        if user:
            search_history = SearchHistory(
                user_id=user.id,
                search_params=search_params.model_dump(exclude_none=True, mode="json"),
            )
            await self._search_history_repository.create(search_history)
            await self._transaction_manager.commit()

        return tariff_responses

    async def _get_user_safe(self) -> User | None:
        try:
            return await self._identity_provider.get_current_user()
        except AppException:
            return None
