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


@pytest.mark.asyncio
async def test_check_rate_limit_allowed(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    # Mock setup
    redis_mock.zcard.return_value = 2  # Current count is below limit

    # Test with limit not reached
    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    # Checks
    assert is_allowed is True
    assert remaining == 2  # 5 (limit) - 3 (current count after adding new attempt)

    # Verify Redis calls
    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.zadd.assert_called_once()
    redis_mock.expire.assert_called_once()


@pytest.mark.asyncio
async def test_check_rate_limit_exceeded(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    # Mock setup
    redis_mock.zcard.return_value = 5  # Current count equals limit

    # Test with limit reached
    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    # Checks
    assert is_allowed is False
    assert remaining == 0

    # Verify Redis calls
    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    assert redis_mock.zadd.call_count == 0  # Should not add new entry
    redis_mock.expire.assert_called_once()


@pytest.mark.asyncio
async def test_login_rate_limit(rate_limiter: RateLimiter) -> None:
    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(True, 4)
    ) as mock_check:
        result = await rate_limiter.login_rate_limit("127.0.0.1", "test_user")

        # Check result
        assert result == (True, 4)

        # Verify correct parameters
        mock_check.assert_called_once_with("login_limit:127.0.0.1:test_user", 5, 5)


@pytest.mark.asyncio
async def test_password_change_rate_limit(rate_limiter: RateLimiter) -> None:
    user_id = uuid.uuid4()

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(True, 1)
    ) as mock_check:
        result = await rate_limiter.password_change_rate_limit(user_id)

        # Check result
        assert result == (True, 1)

        # Verify correct parameters
        mock_check.assert_called_once_with(f"password_change_limit:{user_id}", 2, 1440)


@pytest.mark.asyncio
async def test_token_refresh_rate_limit(rate_limiter: RateLimiter) -> None:
    user_id = uuid.uuid4()

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(False, 0)
    ) as mock_check:
        result = await rate_limiter.token_refresh_rate_limit(user_id)

        assert result == (False, 0)

        mock_check.assert_called_once_with(f"token_refresh_limit:{user_id}", 10, 60)
