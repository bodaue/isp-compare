from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from isp_compare.api.v1 import security
from isp_compare.schemas.tariff import (
    TariffCreate,
    TariffResponse,
    TariffSearchParams,
    TariffUpdate,
)
from isp_compare.services.tariff import TariffService

router = APIRouter(tags=["Tariffs"])


@router.post(
    "/providers/{provider_id}/tariffs",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(security)],
)
@inject
async def create_tariff(
    provider_id: UUID,
    data: TariffCreate,
    service: FromDishka[TariffService],
) -> TariffResponse:
    return await service.create_tariff(provider_id=provider_id, data=data)


@router.get("/tariffs")
@inject
async def get_all_tariffs(
    service: FromDishka[TariffService],
    limit: int = 100,
    offset: int = 0,
) -> list[TariffResponse]:
    return await service.get_all_tariffs(limit, offset)


@router.get("/providers/{provider_id}/tariffs")
@inject
async def get_provider_tariffs(
    provider_id: UUID,
    service: FromDishka[TariffService],
    limit: int = 100,
    offset: int = 0,
) -> list[TariffResponse]:
    return await service.get_provider_tariffs(provider_id, limit, offset)


@router.get("/tariffs/search", dependencies=[Depends(security)])
@inject
async def search_tariffs(
    service: FromDishka[TariffService],
    search_params: Annotated[TariffSearchParams, Depends(TariffSearchParams)],
) -> list[TariffResponse]:
    return await service.search_tariffs(search_params)


@router.get("/tariffs/{tariff_id}")
@inject
async def get_tariff(
    tariff_id: UUID,
    service: FromDishka[TariffService],
) -> TariffResponse:
    return await service.get_tariff(tariff_id)


@router.patch("/tariffs/{tariff_id}", dependencies=[Depends(security)])
@inject
async def update_tariff(
    tariff_id: UUID,
    data: TariffUpdate,
    service: FromDishka[TariffService],
) -> TariffResponse:
    return await service.update_tariff(tariff_id, data)


@router.delete(
    "/tariffs/{tariff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(security)],
)
@inject
async def delete_tariff(
    tariff_id: UUID,
    service: FromDishka[TariffService],
) -> None:
    await service.delete_tariff(tariff_id)
