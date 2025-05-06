import uuid

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from isp_compare.models.user import User
from isp_compare.repositories.review import ReviewRepository

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def review_repository(session: AsyncSession) -> ReviewRepository:
    return ReviewRepository(session=session)


@pytest.fixture
async def test_user(session: AsyncSession, faker: Faker) -> User:
    user = User(
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
        is_admin=faker.boolean(),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def test_provider(session: AsyncSession, faker: Faker) -> Provider:
    provider = Provider(
        name=faker.company(),
        description=faker.paragraph(),
        website=faker.url(),
        logo_url=faker.image_url(),
        rating=faker.pyfloat(min_value=1, max_value=5, right_digits=1),
    )
    session.add(provider)
    await session.commit()
    return provider


@pytest.fixture
async def test_review(
    session: AsyncSession, test_user: User, test_provider: Provider, faker: Faker
) -> Review:
    review = Review(
        user_id=test_user.id,
        provider_id=test_provider.id,
        rating=faker.pyint(min_value=1, max_value=5),
        comment=faker.paragraph(),
    )
    session.add(review)
    await session.commit()
    return review


@pytest.fixture
async def test_reviews(
    session: AsyncSession, test_provider: Provider, faker: Faker
) -> list[Review]:
    reviews = []

    for _ in range(3):
        user = User(
            fullname=faker.name(),
            username=faker.user_name(),
            hashed_password=faker.sha256(),
            email=faker.email(),
        )
        session.add(user)
        await session.flush()

        review = Review(
            user_id=user.id,
            provider_id=test_provider.id,
            rating=faker.pyint(min_value=1, max_value=5),
            comment=faker.paragraph(),
        )
        reviews.append(review)
        session.add(review)

    await session.commit()
    return reviews


async def test_create(
    session: AsyncSession,
    review_repository: ReviewRepository,
    test_user: User,
    test_provider: Provider,
    faker: Faker,
) -> None:
    review = Review(
        user_id=test_user.id,
        provider_id=test_provider.id,
        rating=faker.pyint(min_value=1, max_value=5),
        comment=faker.paragraph(),
    )

    await review_repository.create(review)
    await session.flush()

    stmt = select(Review).where(Review.id == review.id)
    result = await session.execute(stmt)
    saved_review = result.scalar_one()

    assert saved_review.id == review.id
    assert saved_review.user_id == test_user.id
    assert saved_review.provider_id == test_provider.id
    assert saved_review.rating == review.rating
    assert saved_review.comment == review.comment


async def test_get_by_id(
    review_repository: ReviewRepository, test_review: Review
) -> None:
    result = await review_repository.get_by_id(test_review.id)

    assert result is not None
    assert result.id == test_review.id
    assert result.user_id == test_review.user_id
    assert result.provider_id == test_review.provider_id
    assert result.rating == test_review.rating
    assert result.comment == test_review.comment


async def test_get_by_id_for_update(
    review_repository: ReviewRepository, test_review: Review
) -> None:
    result = await review_repository.get_by_id(test_review.id, for_update=True)

    assert result is not None
    assert result.id == test_review.id
    assert result.user_id == test_review.user_id
    assert result.provider_id == test_review.provider_id


async def test_get_by_id_not_found(review_repository: ReviewRepository) -> None:
    non_existent_id = uuid.uuid4()
    result = await review_repository.get_by_id(non_existent_id)

    assert result is None


async def test_get_by_user_and_provider(
    review_repository: ReviewRepository, test_review: Review
) -> None:
    result = await review_repository.get_by_user_and_provider(
        test_review.user_id, test_review.provider_id
    )

    assert result is not None
    assert result.id == test_review.id
    assert result.user_id == test_review.user_id
    assert result.provider_id == test_review.provider_id


async def test_get_by_user_and_provider_not_found(
    review_repository: ReviewRepository,
) -> None:
    non_existent_user_id = uuid.uuid4()
    non_existent_provider_id = uuid.uuid4()
    result = await review_repository.get_by_user_and_provider(
        non_existent_user_id, non_existent_provider_id
    )

    assert result is None


async def test_get_by_provider(
    review_repository: ReviewRepository,
    test_provider: Provider,
    test_reviews: list[Review],
) -> None:
    limit = 10
    offset = 0
    result = await review_repository.get_by_provider(test_provider.id, limit, offset)

    assert len(result) == len(test_reviews)

    for review in result:
        assert review.provider_id == test_provider.id


async def test_get_by_provider_with_limit(
    review_repository: ReviewRepository,
    test_provider: Provider,
    test_reviews: list[Review],
) -> None:
    limit = 2
    offset = 0
    result = await review_repository.get_by_provider(test_provider.id, limit, offset)

    assert len(result) == limit

    for review in result:
        assert review.provider_id == test_provider.id


async def test_get_by_provider_with_offset(
    review_repository: ReviewRepository,
    test_provider: Provider,
    test_reviews: list[Review],
) -> None:
    limit = 10
    offset = 1
    result = await review_repository.get_by_provider(test_provider.id, limit, offset)

    assert len(result) == len(test_reviews) - offset

    for review in result:
        assert review.provider_id == test_provider.id


async def test_update(
    session: AsyncSession,
    review_repository: ReviewRepository,
    test_review: Review,
    faker: Faker,
) -> None:
    new_rating = 5 if test_review.rating < 5 else 1
    new_comment = faker.paragraph()
    update_data = {"rating": new_rating, "comment": new_comment}

    await review_repository.update(test_review.id, update_data)
    await session.commit()

    stmt = select(Review).where(Review.id == test_review.id)
    result = await session.execute(stmt)
    updated_review = result.scalar_one()

    assert updated_review.rating == new_rating
    assert updated_review.comment == new_comment
    assert updated_review.user_id == test_review.user_id
    assert updated_review.provider_id == test_review.provider_id


async def test_delete(
    session: AsyncSession, review_repository: ReviewRepository, test_review: Review
) -> None:
    await review_repository.delete(test_review)
    await session.commit()

    stmt = select(Review).where(Review.id == test_review.id)
    result = await session.execute(stmt)
    deleted_review = result.scalar_one_or_none()

    assert deleted_review is None


async def test_calculate_average_rating(
    session: AsyncSession,
    review_repository: ReviewRepository,
    test_provider: Provider,
    test_user: User,
    faker: Faker,
) -> None:
    # Create reviews with specific ratings
    ratings = [3, 4, 5]
    for rating in ratings:
        user = User(
            fullname=faker.name(),
            username=faker.user_name(),
            hashed_password=faker.sha256(),
            email=faker.email(),
        )
        session.add(user)
        await session.flush()

        review = Review(
            user_id=user.id,
            provider_id=test_provider.id,
            rating=rating,
            comment=faker.paragraph(),
        )
        session.add(review)

    await session.commit()

    avg_rating = await review_repository.calculate_average_rating(test_provider.id)

    assert avg_rating == 4.0


async def test_calculate_average_rating_no_reviews(
    review_repository: ReviewRepository,
) -> None:
    provider_id = uuid.uuid4()
    avg_rating = await review_repository.calculate_average_rating(provider_id)

    assert avg_rating is None
