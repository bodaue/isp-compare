from isp_compare.core.exceptions import (
    UsernameAlreadyExistsException,
    UsernameChangeRateLimitExceededException,
)
from isp_compare.repositories.user import UserRepository
from isp_compare.schemas.user import UserProfile, UserProfileUpdate
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.transaction_manager import TransactionManager


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
        rate_limiter: RateLimiter,
    ) -> None:
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider
        self._rate_limiter = rate_limiter

    async def get_profile(self) -> UserProfile:
        user = await self._identity_provider.get_current_user()
        return UserProfile.model_validate(user)

    async def update_profile(
        self,
        update_data: UserProfileUpdate,
    ) -> UserProfile:
        user = await self._identity_provider.get_current_user()

        update_fields = update_data.model_dump(exclude_unset=True)

        if not update_fields:
            return UserProfile.model_validate(user)

        if "username" in update_fields and update_fields["username"] != user.username:
            is_allowed, remaining = await self._rate_limiter.username_change_rate_limit(
                user.id
            )
            if not is_allowed:
                raise UsernameChangeRateLimitExceededException

            existing_user = await self._user_repository.get_by_username(
                update_fields["username"]
            )
            if existing_user and existing_user.id != user.id:
                raise UsernameAlreadyExistsException

        await self._user_repository.update_profile(user.id, update_fields)
        await self._transaction_manager.commit()
        await self._transaction_manager.refresh(user)
        return UserProfile.model_validate(user)
