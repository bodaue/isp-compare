from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends
from isp_compare.schemas.common import APIResponse
from isp_compare.schemas.user import PasswordChange, UserProfile, UserProfileUpdate
from isp_compare.services.auth import AuthService
from isp_compare.services.user import UserService

from isp_compare.api.v1 import security

router = APIRouter(prefix="/users", tags=["User"], dependencies=[Depends(security)])


@router.get("/me")
@inject
async def get_current_user(
    service: FromDishka[UserService],
) -> UserProfile:
    return await service.get_profile()


@router.patch("/profile")
@inject
async def update_profile(
    data: UserProfileUpdate,
    service: FromDishka[UserService],
) -> UserProfile:
    return await service.update_profile(data)


@router.post("/change-password")
@inject
async def change_password(
    data: PasswordChange,
    service: FromDishka[AuthService],
) -> APIResponse:
    await service.change_password(data)
    return APIResponse(message="Password successfully changed")
