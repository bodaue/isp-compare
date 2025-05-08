import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker

from isp_compare.core.exceptions import (
    ProviderNotFoundException,
    ReviewNotFoundException,
)
from isp_compare.models import Provider, User
from isp_compare.models.review import Review
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.review import ReviewRepository
from isp_compare.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.review import ReviewService
from isp_compare.services.transaction_manager import TransactionManager


@pytest.fixture
def review_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ReviewRepository)


@pytest.fixture
def provider_repository_mock() -> AsyncMock:
    return AsyncMock(spec=ProviderRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def identity_provider_mock() -> AsyncMock:
    return AsyncMock(spec=IdentityProvider)


@pytest.fixture
def review_service(
    review_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
) -> ReviewService:
    return ReviewService(
        review_repository=review_repository_mock,
        provider_repository=provider_repository_mock,
        transaction_manager=transaction_manager_mock,
        identity_provider=identity_provider_mock,
    )


@pytest.fixture
def mock_user(faker: Faker) -> User:
    return User(
        id=uuid.uuid4(),
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=False,
    )


@pytest.fixture
def mock_admin_user(faker: Faker) -> User:
    return User(
        id=uuid.uuid4(),
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=True,
    )


@pytest.fixture
def mock_provider(faker: Faker) -> Provider:
    return Provider(
        id=uuid.uuid4(),
        name=faker.company(),
        description=faker.paragraph(),
        website=faker.url(),
        logo_url=faker.image_url(),
        rating=faker.pyfloat(min_value=1, max_value=5, right_digits=1),
    )


@pytest.fixture
def mock_review(mock_user: User, mock_provider: Provider, faker: Faker) -> Review:
    return Review(
        id=uuid.uuid4(),
        user_id=mock_user.id,
        provider_id=mock_provider.id,
        rating=faker.pyint(min_value=1, max_value=5),
        comment=faker.paragraph(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


async def test_create_review_success(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
    mock_provider: Provider,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    provider_repository_mock.get_by_id.return_value = mock_provider
    review_repository_mock.get_by_user_and_provider.return_value = None
    review_repository_mock.calculate_average_rating.return_value = 4.5

    review_data = ReviewCreate(
        rating=5,
        comment="Отличный провайдер, стабильное соединение.",
    )

    async def create_side_effect(review: Review) -> None:
        review.id = uuid.uuid4()
        review.created_at = datetime.now(UTC)
        review.updated_at = datetime.now(UTC)

    review_repository_mock.create.side_effect = create_side_effect

    result = await review_service.create_review(mock_provider.id, review_data)

    identity_provider_mock.get_current_user.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id=mock_provider.id
    )
    review_repository_mock.get_by_user_and_provider.assert_called_once_with(
        user_id=mock_user.id, provider_id=mock_provider.id
    )
    review_repository_mock.create.assert_called_once()
    review_repository_mock.calculate_average_rating.assert_called_once_with(
        provider_id=mock_provider.id
    )
    provider_repository_mock.update.assert_called_once_with(
        mock_provider.id, {"rating": 4.5}
    )
    assert transaction_manager_mock.commit.call_count == 2

    assert isinstance(result, ReviewResponse)
    assert result.rating == review_data.rating
    assert result.comment == review_data.comment


async def test_create_review_update_existing(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
    mock_provider: Provider,
    mock_review: Review,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    provider_repository_mock.get_by_id.return_value = mock_provider
    review_repository_mock.get_by_user_and_provider.return_value = mock_review
    review_repository_mock.calculate_average_rating.return_value = 4.0
    review_repository_mock.get_by_id.return_value = mock_review

    review_data = ReviewCreate(
        rating=3,
        comment="Обновленный отзыв.",
    )

    result = await review_service.create_review(mock_provider.id, review_data)

    identity_provider_mock.get_current_user.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(
        provider_id=mock_provider.id
    )
    review_repository_mock.get_by_user_and_provider.assert_called_once()
    review_repository_mock.update.assert_called_once_with(
        mock_review.id, {"rating": review_data.rating, "comment": review_data.comment}
    )
    review_repository_mock.calculate_average_rating.assert_called_once()
    provider_repository_mock.update.assert_called_once_with(
        provider_id=mock_provider.id, update_data={"rating": 4.0}
    )
    assert transaction_manager_mock.commit.call_count == 2

    assert isinstance(result, ReviewResponse)


async def test_create_review_provider_not_found(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    provider_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    provider_repository_mock.get_by_id.return_value = None

    review_data = ReviewCreate(
        rating=5,
        comment="Отзыв для несуществующего провайдера.",
    )

    with pytest.raises(ProviderNotFoundException):
        await review_service.create_review(provider_id, review_data)

    identity_provider_mock.get_current_user.assert_called_once()
    provider_repository_mock.get_by_id.assert_called_once_with(provider_id=provider_id)


async def test_get_review_success(
    review_service: ReviewService,
    review_repository_mock: AsyncMock,
    mock_review: Review,
) -> None:
    review_repository_mock.get_by_id.return_value = mock_review

    result = await review_service.get_review(mock_review.id)

    review_repository_mock.get_by_id.assert_called_once_with(mock_review.id)
    assert isinstance(result, ReviewResponse)
    assert result.rating == mock_review.rating
    assert result.comment == mock_review.comment


async def test_get_review_not_found(
    review_service: ReviewService,
    review_repository_mock: AsyncMock,
) -> None:
    review_id = uuid.uuid4()
    review_repository_mock.get_by_id.return_value = None

    with pytest.raises(ReviewNotFoundException):
        await review_service.get_review(review_id)

    review_repository_mock.get_by_id.assert_called_once_with(review_id)


async def test_get_provider_reviews_success(
    review_service: ReviewService,
    provider_repository_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    mock_provider: Provider,
    mock_review: Review,
) -> None:
    provider_repository_mock.get_by_id.return_value = mock_provider
    review_repository_mock.get_by_provider.return_value = [mock_review]

    limit = 10
    offset = 0
    result = await review_service.get_provider_reviews(mock_provider.id, limit, offset)

    provider_repository_mock.get_by_id.assert_called_once_with(mock_provider.id)
    review_repository_mock.get_by_provider.assert_called_once_with(
        mock_provider.id, limit, offset
    )
    assert len(result) == 1
    assert isinstance(result[0], ReviewResponse)


async def test_get_provider_reviews_provider_not_found(
    review_service: ReviewService,
    provider_repository_mock: AsyncMock,
) -> None:
    provider_id = uuid.uuid4()
    provider_repository_mock.get_by_id.return_value = None

    with pytest.raises(ProviderNotFoundException):
        await review_service.get_provider_reviews(provider_id, 10, 0)

    provider_repository_mock.get_by_id.assert_called_once_with(provider_id)


async def test_update_review_success(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
    mock_review: Review,
) -> None:
    mock_review.user_id = mock_user.id
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = mock_review
    review_repository_mock.calculate_average_rating.return_value = 4.2

    update_data = ReviewUpdate(
        rating=4,
        comment="Обновленный комментарий.",
    )

    result = await review_service.update_review(mock_review.id, update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    review_repository_mock.get_by_id.assert_any_call(mock_review.id, for_update=True)
    review_repository_mock.update.assert_called_once_with(
        mock_review.id, update_data.model_dump(exclude_unset=True)
    )
    review_repository_mock.calculate_average_rating.assert_called_once_with(
        mock_review.provider_id
    )
    provider_repository_mock.update.assert_called_once_with(
        mock_review.provider_id, {"rating": 4.2}
    )
    assert transaction_manager_mock.commit.call_count == 2

    assert isinstance(result, ReviewResponse)


async def test_update_review_as_admin(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_admin_user: User,
    mock_review: Review,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_admin_user
    review_repository_mock.get_by_id.return_value = mock_review
    review_repository_mock.calculate_average_rating.return_value = 3.8

    update_data = ReviewUpdate(rating=3)

    result = await review_service.update_review(mock_review.id, update_data)

    assert result is not None
    review_repository_mock.update.assert_called_once()


async def test_update_review_not_found(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    review_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = None

    update_data = ReviewUpdate(rating=5)

    with pytest.raises(ReviewNotFoundException):
        await review_service.update_review(review_id, update_data)

    review_repository_mock.get_by_id.assert_called_once_with(review_id, for_update=True)


async def test_update_review_not_owner_not_admin(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    mock_user: User,
    mock_review: Review,
) -> None:
    mock_review.user_id = uuid.uuid4()  # Different user
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = mock_review

    update_data = ReviewUpdate(rating=1)

    with pytest.raises(ReviewNotFoundException):
        await review_service.update_review(mock_review.id, update_data)


async def test_delete_review_success(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
    mock_review: Review,
) -> None:
    mock_review.user_id = mock_user.id
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = mock_review
    review_repository_mock.calculate_average_rating.return_value = 3.5

    await review_service.delete_review(mock_review.id)

    identity_provider_mock.get_current_user.assert_called_once()
    review_repository_mock.get_by_id.assert_called_once_with(
        mock_review.id, for_update=True
    )
    review_repository_mock.delete.assert_called_once_with(mock_review)
    review_repository_mock.calculate_average_rating.assert_called_once_with(
        mock_review.provider_id
    )
    provider_repository_mock.update.assert_called_once_with(
        mock_review.provider_id, {"rating": 3.5}
    )
    assert transaction_manager_mock.commit.call_count == 2


async def test_delete_review_as_admin(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    provider_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_admin_user: User,
    mock_review: Review,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_admin_user
    review_repository_mock.get_by_id.return_value = mock_review
    review_repository_mock.calculate_average_rating.return_value = None

    await review_service.delete_review(mock_review.id)

    review_repository_mock.delete.assert_called_once_with(mock_review)
    provider_repository_mock.update.assert_called_once_with(
        mock_review.provider_id, {"rating": None}
    )


async def test_delete_review_not_found(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    review_id = uuid.uuid4()
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = None

    with pytest.raises(ReviewNotFoundException):
        await review_service.delete_review(review_id)

    review_repository_mock.get_by_id.assert_called_once_with(review_id, for_update=True)


async def test_delete_review_not_owner_not_admin(
    review_service: ReviewService,
    identity_provider_mock: AsyncMock,
    review_repository_mock: AsyncMock,
    mock_user: User,
    mock_review: Review,
) -> None:
    mock_review.user_id = uuid.uuid4()  # Different user
    identity_provider_mock.get_current_user.return_value = mock_user
    review_repository_mock.get_by_id.return_value = mock_review

    with pytest.raises(ReviewNotFoundException):
        await review_service.delete_review(mock_review.id)

    review_repository_mock.delete.assert_not_called()
