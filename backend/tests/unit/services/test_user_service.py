import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from faker.proxy import Faker

from isp_compare.core.exceptions import (
    IncorrectPasswordException,
    PasswordChangeRateLimitExceededException,
    UsernameAlreadyExistsException,
    UserNotFoundException,
)
from isp_compare.models.user import User
from isp_compare.repositories.user import UserRepository
from isp_compare.schemas.user import PasswordChange, UserProfile, UserProfileUpdate
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.password_hasher import PasswordHasher
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.transaction_manager import TransactionManager
from isp_compare.services.user import UserService


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def identity_provider_mock() -> AsyncMock:
    return AsyncMock(spec=IdentityProvider)


@pytest.fixture
def rate_limiter_mock() -> AsyncMock:
    return AsyncMock(spec=RateLimiter)


@pytest.fixture
def password_hasher_mock() -> MagicMock:
    return MagicMock(spec=PasswordHasher)


@pytest.fixture
def user_service(
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    password_hasher_mock: MagicMock,
) -> UserService:
    return UserService(
        user_repository=user_repository_mock,
        transaction_manager=transaction_manager_mock,
        identity_provider=identity_provider_mock,
        rate_limiter=rate_limiter_mock,
        password_hasher=password_hasher_mock,
    )


@pytest.fixture
def mock_user(faker: Faker) -> User:
    return User(
        id=uuid.uuid4(),
        fullname=faker.name(),
        username=faker.user_name(),
        hashed_password=faker.sha256(),
        email=faker.email(),
    )


async def test_get_profile_success(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    result = await user_service.get_profile()

    identity_provider_mock.get_current_user.assert_called_once()
    assert isinstance(result, UserProfile)
    assert result.id == mock_user.id
    assert result.fullname == mock_user.fullname
    assert result.username == mock_user.username
    assert result.email == mock_user.email


async def test_update_profile_success(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    user_repository_mock.get_by_username.return_value = None
    rate_limiter_mock.username_change_rate_limit.return_value = (
        True,
        2,
    )
    update_data = UserProfileUpdate(fullname="Updated Name", username="updated_user")

    result = await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    rate_limiter_mock.username_change_rate_limit.assert_called_once_with(mock_user.id)
    user_repository_mock.get_by_username.assert_called_once_with("updated_user")
    user_repository_mock.update_profile.assert_called_once_with(
        mock_user.id, {"fullname": "Updated Name", "username": "updated_user"}
    )
    transaction_manager_mock.commit.assert_called_once()
    transaction_manager_mock.refresh.assert_called_once_with(mock_user)

    assert isinstance(result, UserProfile)
    assert result.id == mock_user.id
    assert result.fullname == mock_user.fullname
    assert result.username == mock_user.username
    assert result.email == mock_user.email


async def test_update_profile_partial(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    update_data = UserProfileUpdate(fullname="Updated Name")

    result = await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    user_repository_mock.get_by_username.assert_not_called()
    user_repository_mock.update_profile.assert_called_once_with(
        mock_user.id, {"fullname": "Updated Name"}
    )
    transaction_manager_mock.commit.assert_called_once()
    transaction_manager_mock.refresh.assert_called_once_with(mock_user)

    assert isinstance(result, UserProfile)
    assert result.id == mock_user.id


async def test_update_profile_duplicate_username(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.username_change_rate_limit.return_value = (True, 2)

    existing_user = MagicMock(spec=User)
    existing_user.id = uuid.uuid4()
    user_repository_mock.get_by_username.return_value = existing_user

    update_data = UserProfileUpdate(username="existing_username")

    with pytest.raises(UsernameAlreadyExistsException):
        await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    rate_limiter_mock.username_change_rate_limit.assert_called_once_with(mock_user.id)
    user_repository_mock.get_by_username.assert_called_once_with("existing_username")
    user_repository_mock.update_profile.assert_not_called()
    transaction_manager_mock.commit.assert_not_called()
    transaction_manager_mock.refresh.assert_not_called()


async def test_update_profile_same_username(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    update_data = UserProfileUpdate(fullname="New Name", username=mock_user.username)

    result = await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    user_repository_mock.get_by_username.assert_not_called()
    user_repository_mock.update_profile.assert_called_once_with(
        mock_user.id, {"fullname": "New Name", "username": mock_user.username}
    )
    transaction_manager_mock.commit.assert_called_once()
    transaction_manager_mock.refresh.assert_called_once_with(mock_user)

    assert isinstance(result, UserProfile)
    assert result.id == mock_user.id


async def test_update_profile_empty_data(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    mock_user: User,
) -> None:
    identity_provider_mock.get_current_user.return_value = mock_user

    update_data = UserProfileUpdate()

    result = await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    user_repository_mock.get_by_username.assert_not_called()
    user_repository_mock.update_profile.assert_not_called()
    transaction_manager_mock.commit.assert_not_called()
    transaction_manager_mock.refresh.assert_not_called()

    assert isinstance(result, UserProfile)
    assert result.id == mock_user.id
    assert result.fullname == mock_user.fullname
    assert result.username == mock_user.username
    assert result.email == mock_user.email


async def test_update_profile_username_rate_limit_exceeded(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    from isp_compare.core.exceptions import UsernameChangeRateLimitExceededException

    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.username_change_rate_limit.return_value = (
        False,
        0,
    )

    update_data = UserProfileUpdate(username="new_username")

    with pytest.raises(UsernameChangeRateLimitExceededException):
        await user_service.update_profile(update_data)

    identity_provider_mock.get_current_user.assert_called_once()
    rate_limiter_mock.username_change_rate_limit.assert_called_once_with(mock_user.id)
    user_repository_mock.get_by_username.assert_not_called()
    user_repository_mock.update_profile.assert_not_called()


# Новые тесты для change_password
async def test_change_password_success(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    password_hasher_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    password_data = PasswordChange(
        current_password="OldPassword123",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.check_password_change_limit.return_value = (True, 10)
    password_hasher_mock.verify.return_value = True
    password_hasher_mock.hash.return_value = "new_hashed_password"

    await user_service.change_password(password_data)

    identity_provider_mock.get_current_user.assert_called_once()
    rate_limiter_mock.check_password_change_limit.assert_called_once_with(mock_user.id)
    password_hasher_mock.verify.assert_called_once_with(
        password_data.current_password, mock_user.hashed_password
    )
    password_hasher_mock.hash.assert_called_once_with(password_data.new_password)
    user_repository_mock.update_password.assert_called_once_with(
        mock_user.id, "new_hashed_password"
    )
    transaction_manager_mock.commit.assert_called_once()

    rate_limiter_mock.add_password_change_attempt.assert_called_once()


async def test_change_password_user_not_found(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
) -> None:
    password_data = PasswordChange(
        current_password="OldPassword123",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = None

    with pytest.raises(UserNotFoundException):
        await user_service.change_password(password_data)


async def test_change_password_rate_limit_exceeded_initial(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    password_data = PasswordChange(
        current_password="OldPassword123",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.check_password_change_limit.return_value = (False, 0)

    with pytest.raises(PasswordChangeRateLimitExceededException):
        await user_service.change_password(password_data)

    rate_limiter_mock.check_password_change_limit.assert_called_once_with(mock_user.id)


async def test_change_password_incorrect_current(
    user_service: UserService,
    identity_provider_mock: AsyncMock,
    password_hasher_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    password_data = PasswordChange(
        current_password="WrongPassword",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.check_password_change_limit.return_value = (True, 5)
    password_hasher_mock.verify.return_value = False

    with pytest.raises(IncorrectPasswordException):
        await user_service.change_password(password_data)
