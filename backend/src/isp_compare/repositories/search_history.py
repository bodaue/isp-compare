from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.search_history import SearchHistory


class SearchHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, search_history: SearchHistory) -> None:
        self._session.add(search_history)

    async def get_by_id(self, search_history_id: UUID) -> SearchHistory | None:
        stmt = select(SearchHistory).where(SearchHistory.id == search_history_id)
        return await self._session.scalar(stmt)

    async def get_by_user(
        self, user_id: UUID, limit: int, offset: int
    ) -> list[SearchHistory]:
        stmt = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def delete(self, search_history_id: UUID) -> None:
        search_history = await self.get_by_id(search_history_id)
        if search_history:
            await self._session.delete(search_history)

    async def delete_all_for_user(self, user_id: UUID) -> None:
        stmt = select(SearchHistory).where(SearchHistory.user_id == user_id)
        result = await self._session.execute(stmt)
        search_histories = list(result.scalars())

        for search_history in search_histories:
            await self._session.delete(search_history)
