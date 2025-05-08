import uuid
from unittest.mock import AsyncMock, patch

import pytest

from isp_compare.services.rate_limiter import RateLimiter


@pytest.fixture
def redis_mock() -> AsyncMock:
    redis = AsyncMock()
    redis.zremrangebyscore = AsyncMock()
    redis.zcard = AsyncMock()
    redis.zadd = AsyncMock()
    redis.expire = AsyncMock()
    return redis


@pytest.fixture
def rate_limiter(redis_mock: AsyncMock) -> RateLimiter:
    return RateLimiter(redis_mock)


async def test_check_rate_limit_allowed(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    redis_mock.zcard.return_value = 2

    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    assert is_allowed is True
    assert remaining == 2

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.zadd.assert_called_once()
    redis_mock.expire.assert_called_once()


async def test_check_rate_limit_exceeded(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    redis_mock.zcard.return_value = 5

    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    assert is_allowed is False
    assert remaining == 0

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    assert redis_mock.zadd.call_count == 0
    redis_mock.expire.assert_called_once()


async def test_login_rate_limit(rate_limiter: RateLimiter) -> None:
    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(True, 4)
    ) as mock_check:
        result = await rate_limiter.login_rate_limit("127.0.0.1")

        assert result == (True, 4)

        mock_check.assert_called_once_with("login_limit:127.0.0.1", 5, 5)


async def test_password_change_rate_limit(rate_limiter: RateLimiter) -> None:
    user_id = uuid.uuid4()

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(True, 1)
    ) as mock_check:
        result = await rate_limiter.password_change_rate_limit(user_id)

        assert result == (True, 1)

        mock_check.assert_called_once_with(f"password_change_limit:{user_id}", 2, 1440)


async def test_token_refresh_rate_limit(rate_limiter: RateLimiter) -> None:
    user_id = uuid.uuid4()

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(False, 0)
    ) as mock_check:
        result = await rate_limiter.refresh_token_rate_limit_by_user_id(user_id)

        assert result == (False, 0)

        mock_check.assert_called_once_with(f"refresh_token_limit:{user_id}", 10, 60)


async def test_token_refresh_rate_limit_by_ip(rate_limiter: RateLimiter) -> None:
    ip_address = "127.0.0.1"

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(False, 0)
    ) as mock_check:
        result = await rate_limiter.refresh_token_rate_limit_by_ip(ip_address)

        assert result == (False, 0)

        mock_check.assert_called_once_with(
            f"refresh_token_limit:ip:{ip_address}", 10, 60
        )
