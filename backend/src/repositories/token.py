from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, refresh_token: RefreshToken) -> None:
        self._session.add(refresh_token)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        return await self._session.scalar(stmt)

    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def revoke(self, token: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token, RefreshToken.revoked.is_(False))
            .values(revoked=True, revoked_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True, revoked_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)

    async def delete_expired(self) -> None:
        stmt = select(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
        result = await self._session.execute(stmt)
        expired_tokens = list(result.scalars())

        for token in expired_tokens:
            await self._session.delete(token)
