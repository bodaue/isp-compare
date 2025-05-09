import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.search_history import SearchHistory
from isp_compare.models.user import User


@pytest.fixture
async def user_search_history(
    session: AsyncSession, regular_user: User
) -> list[SearchHistory]:
    search_histories = [
        SearchHistory(
            user_id=regular_user.id,
            search_params={
                "min_price": 20.0,
                "max_price": 50.0,
                "min_speed": 100,
                "has_tv": True,
            },
        ),
        SearchHistory(
            user_id=regular_user.id,
            search_params={
                "min_speed": 50,
                "has_phone": True,
            },
        ),
        SearchHistory(
            user_id=regular_user.id,
            search_params={
                "max_price": 30.0,
            },
        ),
    ]

    session.add_all(search_histories)
    await session.commit()

    return search_histories
