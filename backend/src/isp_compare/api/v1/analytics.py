from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from isp_compare.schemas.analytics import UserSessionData
from isp_compare.schemas.common import APIResponse
from isp_compare.services.user_session import UserSessionService

router = APIRouter(prefix="/analytics", tags=["UserAnalytics"])


@router.post("/user-session")
@inject
async def save_user_session(
    session_data: UserSessionData,
    user_session_service: FromDishka[UserSessionService],
) -> APIResponse:
    await user_session_service.save_user_session(session_data)
    return APIResponse(message="Session data saved successfully")
