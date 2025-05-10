from typing import Any
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from isp_compare.models.review import Review


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, review: Review) -> None:
        self._session.add(review)

    async def get_by_id(
        self, review_id: UUID, for_update: bool = False
    ) -> Review | None:
        if for_update:
            stmt = select(Review).where(Review.id == review_id)
            stmt = stmt.with_for_update()
            review = await self._session.scalar(stmt)

            if review:
                await self._session.refresh(review, ["user"])
            return review
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.id == review_id)
        )
        return await self._session.scalar(stmt)

    async def get_by_user_and_provider(
        self, user_id: UUID, provider_id: UUID
    ) -> Review | None:
        stmt = select(Review).where(
            Review.user_id == user_id, Review.provider_id == provider_id
        )
        return await self._session.scalar(stmt)

    async def get_by_provider(
        self, provider_id: UUID, limit: int, offset: int
    ) -> list[Review]:
        stmt = (
            select(Review)
            .options(joinedload(Review.user))
            .where(Review.provider_id == provider_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique())

    async def update(self, review_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Review).where(Review.id == review_id).values(**update_data)
        await self._session.execute(stmt)

    async def delete(self, review: Review) -> None:
        await self._session.delete(review)

    async def calculate_average_rating(self, provider_id: UUID) -> float:
        stmt = select(func.avg(Review.rating)).where(Review.provider_id == provider_id)
        result = await self._session.scalar(stmt)
        return result or None
