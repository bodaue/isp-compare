from isp_compare.core.exceptions import (
    UsernameAlreadyExistsException,
)
from isp_compare.repositories.user import UserRepository
from isp_compare.schemas.user import UserProfile, UserProfileUpdate

from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.transaction_manager import TransactionManager


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        identity_provider: IdentityProvider,
    ) -> None:
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager
        self._identity_provider = identity_provider

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
            existing_user = await self._user_repository.get_by_username(
                update_fields["username"]
            )
            if existing_user and existing_user.id != user.id:
                raise UsernameAlreadyExistsException

        await self._user_repository.update_profile(user.id, update_fields)
        await self._transaction_manager.commit()
        await self._transaction_manager.refresh(user)
        return UserProfile.model_validate(user)
