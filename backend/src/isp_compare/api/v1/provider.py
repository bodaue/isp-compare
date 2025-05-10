from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from isp_compare.schemas.provider import (
    ProviderResponse,
)
from isp_compare.services.provider import ProviderService

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("")
@inject
async def get_all_providers(
    service: FromDishka[ProviderService],
) -> list[ProviderResponse]:
    return await service.get_all_providers()


@router.get("/{provider_id}")
@inject
async def get_provider(
    provider_id: UUID,
    service: FromDishka[ProviderService],
) -> ProviderResponse:
    return await service.get_provider(provider_id)
