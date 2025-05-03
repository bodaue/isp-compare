from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, provider: Provider) -> None:
        self._session.add(provider)

    async def get_by_id(
        self, provider_id: UUID, for_update: bool = False
    ) -> Provider | None:
        stmt = select(Provider).where(Provider.id == provider_id)

        if for_update:
            stmt = stmt.with_for_update()
        return await self._session.scalar(stmt)

    async def get_all(self, limit: int, offset: int) -> list[Provider]:
        stmt = select(Provider).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def update(self, provider_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Provider).where(Provider.id == provider_id).values(**update_data)
        await self._session.execute(stmt)

    async def delete(self, provider: Provider) -> None:
        await self._session.delete(provider)
