from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def flush(self, objects: Sequence | None = None) -> None:
        await self.session.flush(objects)

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, instance: object) -> None:
        await self.session.refresh(instance)
