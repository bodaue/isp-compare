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


async def test_check_rate_limit_first_attempt(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    """Тест первой попытки (Redis пуст)"""
    redis_mock.zcard.return_value = 0  # В Redis пока нет попыток

    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    assert is_allowed is True
    assert remaining == 4  # 5 - 1 = 4

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.zadd.assert_called_once()  # Добавляем первую попытку
    redis_mock.expire.assert_called_once()


async def test_check_rate_limit_allowed(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    redis_mock.zcard.return_value = 2

    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    assert is_allowed is True
    assert remaining == 2  # 5 - 3 (2 в Redis + 1 текущая)

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.zadd.assert_called_once()  # Добавляем текущую попытку
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
    assert redis_mock.zadd.call_count == 0  # Не добавляем при превышении лимита
    redis_mock.expire.assert_called_once()


async def test_check_rate_limit_at_limit(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    """Тест случая, когда достигаем точно лимита"""
    redis_mock.zcard.return_value = 4  # 4 попытки в Redis

    is_allowed, remaining = await rate_limiter.check_rate_limit("test:key", 5, 10)

    assert is_allowed is True  # 4 + 1 = 5, что равно лимиту
    assert remaining == 0  # 5 - 5 = 0

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.zadd.assert_called_once()  # Добавляем 5-ю (последнюю) попытку
    redis_mock.expire.assert_called_once()


async def test_add_failed_attempt(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    await rate_limiter.add_failed_attempt("test:key", 5)

    redis_mock.zadd.assert_called_once()
    redis_mock.expire.assert_called_once()


async def test_check_failed_login_limit_allowed(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    redis_mock.zcard.return_value = 5

    is_allowed, remaining = await rate_limiter.check_failed_login_limit("testuser")

    assert is_allowed is True
    assert remaining == 5  # 10 - 5 (НЕ добавляем текущую попытку)

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    assert redis_mock.zadd.call_count == 0  # НЕ добавляем попытку - только проверяем
    redis_mock.expire.assert_called_once()


async def test_check_failed_login_limit_exceeded(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    redis_mock.zcard.return_value = 10

    is_allowed, remaining = await rate_limiter.check_failed_login_limit("testuser")

    assert is_allowed is False
    assert remaining == 0

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.expire.assert_called_once()


async def test_add_failed_login_attempt(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    with patch.object(rate_limiter, "add_failed_attempt") as mock_add_failed_attempt:
        await rate_limiter.add_failed_login_attempt("testuser")

        mock_add_failed_attempt.assert_called_once_with(
            "failed_login_limit:testuser", 5
        )


async def test_check_failed_password_change_limit_allowed(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    redis_mock.zcard.return_value = 3

    is_allowed, remaining = await rate_limiter.check_failed_password_change_limit(
        user_id
    )

    assert is_allowed is True
    assert remaining == 7  # 10 - 3 (НЕ добавляем текущую попытку)

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    assert redis_mock.zadd.call_count == 0  # НЕ добавляем попытку - только проверяем
    redis_mock.expire.assert_called_once()


async def test_check_failed_password_change_limit_exceeded(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    redis_mock.zcard.return_value = 10

    is_allowed, remaining = await rate_limiter.check_failed_password_change_limit(
        user_id
    )

    assert is_allowed is False
    assert remaining == 0

    redis_mock.zremrangebyscore.assert_called_once()
    redis_mock.zcard.assert_called_once()
    redis_mock.expire.assert_called_once()


async def test_add_failed_password_change_attempt(
    rate_limiter: RateLimiter, redis_mock: AsyncMock
) -> None:
    user_id = uuid.uuid4()

    with patch.object(rate_limiter, "add_failed_attempt") as mock_add_failed_attempt:
        await rate_limiter.add_failed_password_change_attempt(user_id)

        mock_add_failed_attempt.assert_called_once_with(
            f"failed_password_change_limit:{user_id}", 5
        )


async def test_refresh_token_rate_limit_by_ip(rate_limiter: RateLimiter) -> None:
    ip_address = "127.0.0.1"

    with patch.object(
        rate_limiter, "check_rate_limit", return_value=(False, 0)
    ) as mock_check:
        result = await rate_limiter.refresh_token_rate_limit_by_ip(ip_address)

        assert result == (False, 0)
        mock_check.assert_called_once_with(
            f"refresh_token_limit:ip:{ip_address}", 10, 60
        )
