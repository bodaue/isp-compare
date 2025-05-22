from isp_compare.core.exceptions import (
    IncorrectPasswordException,
    PasswordChangeRateLimitExceededException,
    UsernameAlreadyExistsException,
    UsernameChangeRateLimitExceededException,
    UserNotFoundException,
)
from isp_compare.repositories.user import UserRepository
from isp_compare.schemas.user import PasswordChange, UserProfile, UserProfileUpdate
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.password_hasher import PasswordHasher
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.transaction_manager import TransactionManager


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
        rate_limiter: RateLimiter,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider
        self._rate_limiter = rate_limiter
        self._password_hasher = password_hasher

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

    async def change_password(self, data: PasswordChange) -> None:
        user = await self._identity_provider.get_current_user()
        if not user:
            raise UserNotFoundException

        (
            is_allowed,
            remaining,
        ) = await self._rate_limiter.check_password_change_limit(user.id)
        if not is_allowed:
            raise PasswordChangeRateLimitExceededException

        if not self._password_hasher.verify(
            data.current_password, user.hashed_password
        ):
            raise IncorrectPasswordException

        await self._rate_limiter.add_password_change_attempt(user.id)
        hashed_password = self._password_hasher.hash(data.new_password)
        await self._user_repository.update_password(user.id, hashed_password)
        await self._transaction_manager.commit()
