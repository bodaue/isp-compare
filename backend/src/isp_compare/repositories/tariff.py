from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.tariff import Tariff


class TariffRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, tariff: Tariff) -> None:
        self._session.add(tariff)

    async def get_by_id(
        self, tariff_id: UUID, for_update: bool = False
    ) -> Tariff | None:
        stmt = select(Tariff).where(Tariff.id == tariff_id)
        if for_update:
            stmt = stmt.with_for_update()
        return await self._session.scalar(stmt)

    async def get_all(self, limit: int, offset: int) -> list[Tariff]:
        stmt = select(Tariff).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def get_by_provider(
        self, provider_id: UUID, limit: int, offset: int
    ) -> list[Tariff]:
        stmt = (
            select(Tariff)
            .where(Tariff.provider_id == provider_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def update(self, tariff_id: UUID, update_data: dict[str, Any]) -> None:
        stmt = update(Tariff).where(Tariff.id == tariff_id).values(**update_data)
        await self._session.execute(stmt)

    async def delete(self, tariff: Tariff) -> None:
        await self._session.delete(tariff)

    async def search(
        self,
        min_price: float | None,
        max_price: float | None,
        min_speed: int | None,
        max_speed: int | None,
        has_tv: bool | None,
        has_phone: bool | None,
        limit: int,
        offset: int,
    ) -> list[Tariff]:
        query = select(Tariff)

        if min_price is not None:
            query = query.where(Tariff.price >= min_price)
        if max_price is not None:
            query = query.where(Tariff.price <= max_price)
        if min_speed is not None:
            query = query.where(Tariff.speed >= min_speed)
        if max_speed is not None:
            query = query.where(Tariff.speed <= max_speed)
        if has_tv is not None:
            query = query.where(Tariff.has_tv == has_tv)
        if has_phone is not None:
            query = query.where(Tariff.has_phone == has_phone)

        query = query.where(Tariff.is_active.is_(True))
        query = query.limit(limit).offset(offset)

        result = await self._session.execute(query)
        return list(result.scalars())
