from uuid import UUID

from isp_compare.core.exceptions import SearchHistoryNotFoundException
from isp_compare.repositories.search_history import SearchHistoryRepository
from isp_compare.schemas.search_history import (
    SearchHistoryResponse,
)
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.transaction_manager import TransactionManager


class SearchHistoryService:
    def __init__(
        self,
        search_history_repository: SearchHistoryRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
    ) -> None:
        self._search_history_repository = search_history_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider

    async def get_user_search_history(
        self, limit: int, offset: int
    ) -> list[SearchHistoryResponse]:
        user = await self._identity_provider.get_current_user()
        search_histories = await self._search_history_repository.get_by_user(
            user.id, limit, offset
        )
        return [
            SearchHistoryResponse.model_validate(history)
            for history in search_histories
        ]

    async def delete_search_history(self, search_history_id: UUID) -> None:
        user = await self._identity_provider.get_current_user()
        search_history = await self._search_history_repository.get_by_id(
            search_history_id=search_history_id,
            for_update=True,
        )

        if not search_history or search_history.user_id != user.id:
            raise SearchHistoryNotFoundException

        await self._search_history_repository.delete(search_history)
        await self._transaction_manager.commit()

    async def clear_search_history(self) -> None:
        user = await self._identity_provider.get_current_user()
        await self._search_history_repository.delete_all_for_user(user.id)
        await self._transaction_manager.commit()
