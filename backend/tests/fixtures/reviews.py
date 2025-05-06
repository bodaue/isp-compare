import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from isp_compare.models.user import User


@pytest.fixture
async def review(
    session: AsyncSession, regular_user: User, provider: Provider
) -> Review:
    test_review = Review(
        user_id=regular_user.id,
        provider_id=provider.id,
        rating=4,
        comment="Хороший провайдер, стабильное подключение. Рекомендую.",
    )
    session.add(test_review)
    await session.commit()
    return test_review


@pytest.fixture
async def review_2(
    session: AsyncSession, regular_user_2: User, provider: Provider
) -> Review:
    test_review = Review(
        user_id=regular_user_2.id,
        provider_id=provider.id,
        rating=5,
        comment="Отличный провайдер, стабильное подключение. Рекомендую.",
    )
    session.add(test_review)
    await session.commit()
    return test_review


@pytest.fixture
async def reviews(
    session: AsyncSession,
    regular_user: User,
    admin_user: User,
    provider: Provider,
    providers: list[Provider],
) -> list[Review]:
    test_reviews = [
        Review(
            user_id=regular_user.id,
            provider_id=provider.id,
            rating=4,
            comment="Хороший провайдер, стабильное подключение.",
        ),
        Review(
            user_id=admin_user.id,
            provider_id=provider.id,
            rating=5,
            comment="Отличный сервис, быстро решают проблемы.",
        ),
    ]

    if providers:
        for i, _provider in enumerate(providers[:3]):
            test_reviews.append(
                Review(
                    user_id=regular_user.id if i % 2 == 0 else admin_user.id,
                    provider_id=_provider.id,
                    rating=3 + i % 3,
                    comment=f"Тестовый отзыв {i + 1} для провайдера {_provider.name}",
                )
            )

    session.add_all(test_reviews)
    await session.commit()
    return test_reviews
