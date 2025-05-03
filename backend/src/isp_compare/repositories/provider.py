from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, provider: Provider) -> None:
        self._session.add(provider)

    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        stmt = select(Provider).where(Provider.id == provider_id)
        return await self._session.scalar(stmt)

    async def get_all(self, limit: int, offset: int) -> list[Provider]:
        stmt = select(Provider).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def update(self, provider_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Provider).where(Provider.id == provider_id).values(**update_data)
        await self._session.execute(stmt)

    async def delete(self, provider_id: UUID) -> None:
        stmt = delete(Provider).where(Provider.id == provider_id)
        await self._session.execute(stmt)
