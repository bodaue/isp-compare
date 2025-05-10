from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from isp_compare.api.v1 import security
from isp_compare.schemas.tariff import (
    TariffResponse,
    TariffSearchParams,
)
from isp_compare.services.tariff import TariffService

router = APIRouter(tags=["Tariffs"])


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
