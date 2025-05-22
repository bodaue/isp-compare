from datetime import UTC, datetime
from uuid import UUID, uuid4

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
            member = str(uuid4())
            await self._redis.zadd(key, {member: current_time})
            attempt_count += 1

            is_allowed = attempt_count <= max_attempts
            remaining_attempts = max(0, max_attempts - attempt_count)

        await self._redis.expire(key, window_seconds)
        return is_allowed, remaining_attempts

    async def add_failed_attempt(self, key: str, window_minutes: int) -> None:
        current_time = int(datetime.now(UTC).timestamp())
        window_seconds = window_minutes * 60

        member = str(uuid4())
        await self._redis.zadd(key, {member: current_time})
        await self._redis.expire(key, window_seconds)

    async def check_failed_login_limit(
        self, username: str, ip_address: str
    ) -> tuple[bool, int]:
        key = f"failed_login_limit:{username}:{ip_address}"
        window_seconds = 5 * 60
        current_time = int(datetime.now(UTC).timestamp())
        window_start_time = current_time - window_seconds

        await self._redis.zremrangebyscore(key, 0, window_start_time)
        attempt_count = await self._redis.zcard(key)

        max_attempts = 10
        if attempt_count >= max_attempts:
            remaining_attempts = 0
            is_allowed = False
        else:
            remaining_attempts = max_attempts - attempt_count
            is_allowed = True

        await self._redis.expire(key, window_seconds)
        return is_allowed, remaining_attempts

    async def add_failed_login_attempt(self, username: str, ip_address: str) -> None:
        key = f"failed_login_limit:{username}:{ip_address}"
        await self.add_failed_attempt(key, 5)

    async def check_password_change_limit(self, user_id: UUID) -> tuple[bool, int]:
        key = f"failed_password_change_limit:{user_id}"
        window_seconds = 5 * 60
        current_time = int(datetime.now(UTC).timestamp())
        window_start_time = current_time - window_seconds

        await self._redis.zremrangebyscore(key, 0, window_start_time)
        attempt_count = await self._redis.zcard(key)

        max_attempts = 10
        if attempt_count >= max_attempts:
            remaining_attempts = 0
            is_allowed = False
        else:
            remaining_attempts = max_attempts - attempt_count
            is_allowed = True

        await self._redis.expire(key, window_seconds)
        return is_allowed, remaining_attempts

    async def add_password_change_attempt(self, user_id: UUID) -> None:
        key = f"failed_password_change_limit:{user_id}"
        await self.add_failed_attempt(key, 5)

    async def refresh_token_rate_limit_by_ip(self, ip_address: str) -> tuple[bool, int]:
        key = f"refresh_token_limit:ip:{ip_address}"
        return await self.check_rate_limit(key, 10, 60)

    async def username_change_rate_limit(self, user_id: UUID) -> tuple[bool, int]:
        key = f"username_change_limit:{user_id}"
        return await self.check_rate_limit(key, 10, 60)
