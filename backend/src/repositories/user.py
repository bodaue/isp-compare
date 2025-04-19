from typing import Any
from uuid import UUID

from models.user import User
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> None:
        self._session.add(user)

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return await self._session.scalar(stmt)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return await self._session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return await self._session.scalar(stmt)

    async def update_password(self, user_id: UUID, hashed_password: str) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self._session.execute(stmt)

    async def update_profile(
        self,
        user_id: UUID,
        update_data: dict[str, Any],
    ) -> None:
        stmt = update(User).where(User.id == user_id).values(**update_data)
        await self._session.execute(stmt)
