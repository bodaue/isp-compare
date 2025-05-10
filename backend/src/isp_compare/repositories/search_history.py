from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.search_history import SearchHistory


class SearchHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, search_history: SearchHistory) -> None:
        self._session.add(search_history)

    async def get_by_id(
        self, search_history_id: UUID, for_update: bool = False
    ) -> SearchHistory | None:
        stmt = select(SearchHistory).where(SearchHistory.id == search_history_id)
        if for_update:
            stmt = stmt.with_for_update()

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

    async def get_latest_by_user(self, user_id: UUID) -> SearchHistory | None:
        stmt = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(1)
        )
        return await self._session.scalar(stmt)

    async def delete(self, search_history: SearchHistory) -> None:
        await self._session.delete(search_history)

    async def delete_all_for_user(self, user_id: UUID) -> None:
        stmt = delete(SearchHistory).where(SearchHistory.user_id == user_id)
        await self._session.execute(stmt)
