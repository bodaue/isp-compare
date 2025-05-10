from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        stmt = select(Provider).where(Provider.id == provider_id)
        return await self._session.scalar(stmt)

    async def get_all(self) -> list[Provider]:
        stmt = select(Provider)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def update(self, provider_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Provider).where(Provider.id == provider_id).values(**update_data)
        await self._session.execute(stmt)
