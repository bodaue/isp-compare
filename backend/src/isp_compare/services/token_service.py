from datetime import UTC, datetime

from jose import JWTError
from redis.asyncio import Redis

from isp_compare.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
    UserNotFoundException,
)
from isp_compare.models.token import RefreshToken
from isp_compare.models.user import User
from isp_compare.repositories.token import RefreshTokenRepository
from isp_compare.repositories.user import UserRepository
from isp_compare.services.token_processor import TokenProcessor
from isp_compare.services.transaction_manager import TransactionManager


class TokenService:
    def __init__(
        self,
        token_processor: TokenProcessor,
        refresh_token_repository: RefreshTokenRepository,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        redis_client: Redis,
    ) -> None:
        self._token_processor = token_processor
        self._refresh_token_repository = refresh_token_repository
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager
        self._redis_client = redis_client

    async def create_tokens(
        self, user: User, skip_revocation: bool = False, skip_commit: bool = False
    ) -> tuple[str, str, datetime]:
        if not skip_revocation:
            await self._refresh_token_repository.revoke_all_for_user(user.id)

        access_token = self._token_processor.create_access_token(user_id=user.id)

        refresh_token_value, expires_at = self._token_processor.create_refresh_token()

        refresh_token = RefreshToken(
            token=refresh_token_value,
            user_id=user.id,
            expires_at=expires_at,
        )
        await self._refresh_token_repository.create(refresh_token)
        if not skip_commit:
            await self._transaction_manager.commit()

        return access_token, refresh_token_value, expires_at

    async def revoke_refresh_token(self, refresh_token_value: str) -> None:
        await self._refresh_token_repository.revoke(refresh_token_value)
        await self._transaction_manager.commit()

    async def blacklist_access_token(self, access_token: str) -> None:
        try:
            payload = self._token_processor.decode_token(access_token)
        except (JWTError, ValueError):
            return

        exp = payload.get("exp")

        if not exp:
            ttl = 1800
        else:
            now = int(datetime.now(UTC).timestamp())
            ttl = max(0, exp - now)

        key = f"blacklisted_token:{access_token}"
        await self._redis_client.set(key, "1", ex=ttl)

    async def is_access_token_blacklisted(self, access_token: str) -> bool:
        key = f"blacklisted_token:{access_token}"
        result = await self._redis_client.get(key)
        return result is not None

    async def rotate_refresh_token(
        self, refresh_token_value: str
    ) -> tuple[str, str, datetime]:
        refresh_token = await self._refresh_token_repository.get_by_token(
            refresh_token_value
        )

        if not refresh_token:
            raise InvalidTokenException

        now = datetime.now(UTC)
        if refresh_token.expires_at < now:
            raise TokenExpiredException

        if refresh_token.revoked:
            await self._refresh_token_repository.revoke_all_for_user(
                refresh_token.user_id
            )
            await self._transaction_manager.commit()

            raise TokenRevokedException

        user = await self._user_repository.get_by_id(refresh_token.user_id)
        if not user:
            raise UserNotFoundException

        await self._refresh_token_repository.revoke(refresh_token_value)

        access_token = self._token_processor.create_access_token(user_id=user.id)

        new_refresh_token_value, expires_at = (
            self._token_processor.create_refresh_token()
        )

        new_refresh_token = RefreshToken(
            token=new_refresh_token_value,
            user_id=user.id,
            expires_at=expires_at,
        )
        await self._refresh_token_repository.create(new_refresh_token)

        await self._transaction_manager.commit()

        return access_token, new_refresh_token_value, expires_at
