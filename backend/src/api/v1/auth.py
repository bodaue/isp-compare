from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response
from fastapi.params import Depends
from schemas.common import APIResponse
from schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
)
from services.auth import AuthService
from starlette import status

from api.v1 import security

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register_user(
    data: UserCreate,
    response: Response,
    service: FromDishka[AuthService],
) -> TokenResponse:
    return await service.register(data, response)


@router.post("/login")
@inject
async def login_user(
    data: UserLogin,
    response: Response,
    service: FromDishka[AuthService],
) -> TokenResponse:
    return await service.login(data, response)


@router.post("/refresh")
@inject
async def refresh_token(
    response: Response,
    service: FromDishka[AuthService],
) -> TokenResponse:
    return await service.refresh_token(response)


@router.post("/logout", dependencies=[Depends(security)])
@inject
async def logout_user(
    response: Response,
    service: FromDishka[AuthService],
) -> APIResponse:
    await service.logout(response)
    return APIResponse(message="Successfully logged out")
