from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from isp_compare.api.v1 import security
from isp_compare.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)
from isp_compare.services.provider import ProviderService

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(security)])
@inject
async def create_provider(
    data: ProviderCreate,
    service: FromDishka[ProviderService],
) -> ProviderResponse:
    return await service.create_provider(data)


@router.get("")
@inject
async def get_all_providers(
    service: FromDishka[ProviderService],
    limit: int = 100,
    offset: int = 0,
) -> list[ProviderResponse]:
    return await service.get_all_providers(limit, offset)


@router.get("/{provider_id}")
@inject
async def get_provider(
    provider_id: UUID,
    service: FromDishka[ProviderService],
) -> ProviderResponse:
    return await service.get_provider(provider_id)


@router.patch("/{provider_id}", dependencies=[Depends(security)])
@inject
async def update_provider(
    provider_id: UUID,
    data: ProviderUpdate,
    service: FromDishka[ProviderService],
) -> ProviderResponse:
    return await service.update_provider(provider_id, data)


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(security)],
)
@inject
async def delete_provider(
    provider_id: UUID,
    service: FromDishka[ProviderService],
) -> None:
    await service.delete_provider(provider_id)
