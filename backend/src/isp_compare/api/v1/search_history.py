from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from isp_compare.api.v1 import security
from isp_compare.schemas.search_history import (
    SearchHistoryResponse,
)
from isp_compare.services.search_history import SearchHistoryService

router = APIRouter(
    prefix="/search-history", tags=["Search History"], dependencies=[Depends(security)]
)


@router.get("")
@inject
async def get_search_history(
    service: FromDishka[SearchHistoryService],
    limit: int = 20,
    offset: int = 0,
) -> list[SearchHistoryResponse]:
    return await service.get_user_search_history(limit, offset)


@router.delete("/{search_history_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_search_history(
    search_history_id: UUID,
    service: FromDishka[SearchHistoryService],
) -> None:
    await service.delete_search_history(search_history_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def clear_search_history(
    service: FromDishka[SearchHistoryService],
) -> None:
    await service.clear_search_history()
