from uuid import UUID

from isp_compare.core.exceptions import (
    ProviderNotFoundException,
    ReviewNotFoundException,
)
from isp_compare.models.review import Review
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.review import ReviewRepository
from isp_compare.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.transaction_manager import TransactionManager


class ReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
        provider_repository: ProviderRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
    ) -> None:
        self._review_repository = review_repository
        self._provider_repository = provider_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider

    async def create_review(
        self, provider_id: UUID, data: ReviewCreate
    ) -> ReviewResponse:
        user = await self._identity_provider.get_current_user()

        provider = await self._provider_repository.get_by_id(provider_id=provider_id)
        if not provider:
            raise ProviderNotFoundException

        existing_review = await self._review_repository.get_by_user_and_provider(
            user_id=user.id, provider_id=provider_id
        )

        if existing_review:
            update_data = {
                "rating": data.rating,
                "comment": data.comment,
            }
            await self._review_repository.update(existing_review.id, update_data)

            avg_rating = await self._review_repository.calculate_average_rating(
                provider_id=provider_id
            )
            await self._provider_repository.update(
                provider_id=provider_id, update_data={"rating": avg_rating}
            )
            await self._transaction_manager.commit()

            updated_review = await self._review_repository.get_by_id(existing_review.id)
            return ReviewResponse.model_validate(updated_review)

        review = Review(
            user_id=user.id,
            provider_id=provider_id,
            rating=data.rating,
            comment=data.comment,
        )

        await self._review_repository.create(review)

        avg_rating = await self._review_repository.calculate_average_rating(
            provider_id=provider_id
        )
        await self._provider_repository.update(provider_id, {"rating": avg_rating})
        await self._transaction_manager.commit()

        return ReviewResponse.model_validate(review)

    async def get_review(self, review_id: UUID) -> ReviewResponse:
        review = await self._review_repository.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException

        return ReviewResponse.model_validate(review)

    async def get_provider_reviews(
        self, provider_id: UUID, limit: int, offset: int
    ) -> list[ReviewResponse]:
        provider = await self._provider_repository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundException

        reviews = await self._review_repository.get_by_provider(
            provider_id, limit, offset
        )
        return [ReviewResponse.model_validate(review) for review in reviews]

    async def update_review(
        self, review_id: UUID, data: ReviewUpdate
    ) -> ReviewResponse:
        user = await self._identity_provider.get_current_user()

        review = await self._review_repository.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException

        if review.user_id != user.id and not user.is_admin:
            raise ReviewNotFoundException

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            await self._review_repository.update(review_id, update_data)

            avg_rating = await self._review_repository.calculate_average_rating(
                review.provider_id
            )
            await self._provider_repository.update(
                review.provider_id, {"rating": avg_rating}
            )
            await self._transaction_manager.commit()
            review = await self._review_repository.get_by_id(review.id)

        return ReviewResponse.model_validate(review)

    async def delete_review(self, review_id: UUID) -> None:
        user = await self._identity_provider.get_current_user()

        review = await self._review_repository.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundException

        if review.user_id != user.id and not user.is_admin:
            raise ReviewNotFoundException

        provider_id = review.provider_id

        await self._review_repository.delete(review_id)

        avg_rating = await self._review_repository.calculate_average_rating(provider_id)
        await self._provider_repository.update(provider_id, {"rating": avg_rating})
        await self._transaction_manager.commit()
