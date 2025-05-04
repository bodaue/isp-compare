from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis


class RateLimiter:
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def check_rate_limit(
        self, key: str, max_attempts: int, window_minutes: int
    ) -> tuple[bool, int]:
        window_seconds = window_minutes * 60
        current_time = int(datetime.now(UTC).timestamp())
        window_start_time = current_time - window_seconds

        await self._redis.zremrangebyscore(key, 0, window_start_time)
        attempt_count = await self._redis.zcard(key)
        if attempt_count >= max_attempts:
            remaining_attempts = 0
            is_allowed = False
        else:
            member = f"{current_time}:{key}"
            await self._redis.zadd(key, {member: current_time})

            attempt_count += 1

            is_allowed = attempt_count <= max_attempts
            remaining_attempts = max(0, max_attempts - attempt_count)

        await self._redis.expire(key, window_seconds)

        return is_allowed, remaining_attempts

    async def login_rate_limit(
        self, ip_address: str, username: str
    ) -> tuple[bool, int]:
        key = f"login_limit:{ip_address}:{username}"
        return await self.check_rate_limit(key, 5, 5)  # 5 попыток в течение 5 минут

    async def password_change_rate_limit(self, user_id: UUID) -> tuple[bool, int]:
        key = f"password_change_limit:{user_id}"
        return await self.check_rate_limit(key, 2, 1440)  # 2 смены в течение 24 часов

    async def token_refresh_rate_limit(self, user_id: UUID) -> tuple[bool, int]:
        key = f"token_refresh_limit:{user_id}"
        return await self.check_rate_limit(key, 10, 60)  # 10 обновлений в час
