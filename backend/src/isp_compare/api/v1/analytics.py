from datetime import UTC, datetime

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.api.v1 import security
from isp_compare.models.user_analytics import UserAnalytics
from isp_compare.schemas.analytics import AnalyticsStats, UserSessionData
from isp_compare.schemas.common import APIResponse
from isp_compare.services.analytics import AnalyticsService
from isp_compare.services.identity_provider import IdentityProvider

router = APIRouter(prefix="/analytics", tags=["UserAnalytics"])


@router.post("/user-session")
@inject
async def save_user_session(
    session_data: UserSessionData,
    session: FromDishka[AsyncSession],
) -> APIResponse:
    user_session = UserAnalytics(
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

    session.add(user_session)
    await session.commit()

    return APIResponse(message="Session data saved successfully")


@router.get("/stats", dependencies=[Depends(security)])
@inject
async def get_analytics_stats(
    service: FromDishka[AnalyticsService],
    identity_provider: FromDishka[IdentityProvider],
) -> AnalyticsStats:
    await identity_provider.ensure_is_admin()
    return await service.get_analytics_stats()
