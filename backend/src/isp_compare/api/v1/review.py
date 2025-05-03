from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from isp_compare.api.v1 import security
from isp_compare.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from isp_compare.services.review import ReviewService

router = APIRouter(tags=["Reviews"])


@router.post(
    "/providers/{provider_id}/reviews",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(security)],
)
@inject
async def create_review(
    provider_id: UUID,
    data: ReviewCreate,
    service: FromDishka[ReviewService],
) -> ReviewResponse:
    return await service.create_review(provider_id=provider_id, data=data)


@router.get("/providers/{provider_id}/reviews")
@inject
async def get_provider_reviews(
    provider_id: UUID,
    service: FromDishka[ReviewService],
    limit: int = 20,
    offset: int = 0,
) -> list[ReviewResponse]:
    return await service.get_provider_reviews(
        provider_id=provider_id, limit=limit, offset=offset
    )


@router.get("/reviews/{review_id}")
@inject
async def get_review(
    review_id: UUID,
    service: FromDishka[ReviewService],
) -> ReviewResponse:
    return await service.get_review(review_id=review_id)


@router.patch("/reviews/{review_id}", dependencies=[Depends(security)])
@inject
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    service: FromDishka[ReviewService],
) -> ReviewResponse:
    return await service.update_review(review_id=review_id, data=data)


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(security)],
)
@inject
async def delete_review(
    review_id: UUID,
    service: FromDishka[ReviewService],
) -> None:
    await service.delete_review(review_id=review_id)
