# backend/src/isp_compare/services/user_session.py
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models import UserSession
from isp_compare.repositories.user_session import UserSessionRepository
from isp_compare.schemas.analytics import UserSessionData
from isp_compare.services.transaction_manager import TransactionManager


class UserSessionService:
    def __init__(
        self,
        session: AsyncSession,
        user_session_repository: UserSessionRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._session = session
        self._user_session_repository = user_session_repository
        self._transaction_manager = transaction_manager

    async def save_user_session(self, session_data: UserSessionData) -> None:
        user_session = UserSession(
            session_id=session_data.session_id,
            start_time=datetime.fromtimestamp(session_data.start_time / 1000, UTC),
            end_time=(
                datetime.fromtimestamp(session_data.end_time / 1000, UTC)
                if session_data.end_time
                else None
            ),
            total_clicks=session_data.total_clicks,
            click_path=[click.model_dump() for click in session_data.click_path],
            user_path=session_data.user_path,
            goal_reached=session_data.goal_reached,
            session_duration=session_data.session_duration,
        )

        try:
            await self._user_session_repository.create(user_session)
            await self._transaction_manager.commit()
        except IntegrityError:
            await self._transaction_manager.rollback()
