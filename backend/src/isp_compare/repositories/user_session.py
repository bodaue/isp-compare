from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.user_session import UserSession


class UserSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_session: UserSession) -> None:
        self._session.add(user_session)
