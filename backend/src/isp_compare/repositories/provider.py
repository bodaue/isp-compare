from typing import Any
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.review import Review


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, provider_id: UUID) -> tuple[Provider, int] | None:
        stmt = (
            select(Provider, func.count(Review.id).label("reviews_count"))
            .outerjoin(Review, Provider.id == Review.provider_id)
            .where(Provider.id == provider_id)
            .group_by(Provider.id)
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()

        if row:
            provider, reviews_count = row
            return provider, reviews_count
        return None

    async def get_all(self) -> list[tuple[Provider, int]]:
        stmt = (
            select(Provider, func.count(Review.id).label("reviews_count"))
            .outerjoin(Review, Provider.id == Review.provider_id)
            .group_by(Provider.id)
        )
        result = await self._session.execute(stmt)

        providers_with_counts = []
        for row in result:
            provider, reviews_count = row
            providers_with_counts.append((provider, reviews_count))

        return providers_with_counts

    async def get_multiple_by_ids(
        self, provider_ids: list[UUID]
    ) -> dict[UUID, Provider]:
        if not provider_ids:
            return {}

        stmt = select(Provider).where(Provider.id.in_(provider_ids))
        result = await self._session.execute(stmt)
        providers = result.scalars().all()

        return {provider.id: provider for provider in providers}

    async def update(self, provider_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Provider).where(Provider.id == provider_id).values(**update_data)
        await self._session.execute(stmt)
