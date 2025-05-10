from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from isp_compare.api.v1 import security
from isp_compare.schemas.tariff import (
    TariffResponse,
    TariffSearchParams,
)
from isp_compare.schemas.tariff_comparison import (
    TariffComparisonRequest,
    TariffComparisonResponse,
)
from isp_compare.services.tariff import TariffService
from isp_compare.services.tariff_comparison import TariffComparisonService

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


@router.post("/tariffs/comparison")
@inject
async def compare_tariffs(
    data: TariffComparisonRequest,
    service: FromDishka[TariffComparisonService],
) -> TariffComparisonResponse:
    if len(data.tariff_ids) < 2:
        raise HTTPException(
            status_code=400, detail="Для сравнения необходимо минимум 2 тарифа"
        )
    if len(data.tariff_ids) > 5:
        raise HTTPException(
            status_code=400, detail="Максимальное количество тарифов для сравнения - 5"
        )

    unique_tariff_ids = list(set(data.tariff_ids))

    return await service.compare_tariffs(unique_tariff_ids)
