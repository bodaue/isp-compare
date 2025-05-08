import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from faker import Faker
from fastapi import Request, Response

from isp_compare.core.config import CookieConfig, JWTConfig
from isp_compare.core.exceptions import (
    EmailAlreadyExistsException,
    IncorrectPasswordException,
    InvalidCredentialsException,
    LoginRateLimitExceededException,
    PasswordChangeRateLimitExceededException,
    RefreshTokenMissingException,
    TokenRefreshRateLimitExceededException,
    UsernameAlreadyExistsException,
    UserNotFoundException,
)
from isp_compare.models.user import User
from isp_compare.repositories.user import UserRepository
from isp_compare.schemas.user import (
    PasswordChange,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from isp_compare.services.auth import AuthService
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.password_hasher import PasswordHasher
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.token_processor import TokenProcessor
from isp_compare.services.token_service import TokenService
from isp_compare.services.transaction_manager import TransactionManager


@pytest.fixture
def request_mock() -> MagicMock:
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {}
    request.cookies = {}
    return request


@pytest.fixture
def response_mock() -> MagicMock:
    return MagicMock(spec=Response)


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def password_hasher_mock() -> MagicMock:
    return MagicMock(spec=PasswordHasher)


@pytest.fixture
def token_processor_mock() -> MagicMock:
    return MagicMock(spec=TokenProcessor)


@pytest.fixture
def token_service_mock() -> AsyncMock:
    return AsyncMock(spec=TokenService)


@pytest.fixture
def identity_provider_mock() -> AsyncMock:
    return AsyncMock(spec=IdentityProvider)


@pytest.fixture
def rate_limiter_mock() -> AsyncMock:
    return AsyncMock(spec=RateLimiter)


@pytest.fixture
def auth_service(
    request_mock: MagicMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    jwt_config: JWTConfig,
    cookie_config: CookieConfig,
    password_hasher_mock: MagicMock,
    token_processor_mock: MagicMock,
    token_service_mock: AsyncMock,
    identity_provider_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
) -> AuthService:
    return AuthService(
        request=request_mock,
        user_repository=user_repository_mock,
        transaction_manager=transaction_manager_mock,
        jwt_config=jwt_config,
        cookie_config=cookie_config,
        password_hasher=password_hasher_mock,
        token_processor=token_processor_mock,
        token_service=token_service_mock,
        identity_provider=identity_provider_mock,
        rate_limiter=rate_limiter_mock,
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


# Register tests
async def test_register_success(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    password_hasher_mock: MagicMock,
    token_service_mock: AsyncMock,
) -> None:
    user_data = UserCreate(
        fullname="Test User",
        username="testuser",
        password="Password123",
        email="test@example.com",
    )

    user_repository_mock.get_by_username.return_value = None
    user_repository_mock.get_by_email.return_value = None
    password_hasher_mock.hash.return_value = "hashed_password"

    access_token = "test_access_token"
    refresh_token = "test_refresh_token"
    expires_at = datetime.now(UTC) + timedelta(days=7)
    token_service_mock.create_tokens.return_value = (
        access_token,
        refresh_token,
        expires_at,
    )

    async def create_side_effect(user: User) -> None:
        user.id = uuid.uuid4()

    user_repository_mock.create.side_effect = create_side_effect

    result = await auth_service.register(user_data, response_mock)

    user_repository_mock.get_by_username.assert_called_once_with(user_data.username)
    user_repository_mock.get_by_email.assert_called_once_with(user_data.email)
    password_hasher_mock.hash.assert_called_once_with(user_data.password)
    user_repository_mock.create.assert_called_once()
    transaction_manager_mock.commit.assert_called_once()
    token_service_mock.create_tokens.assert_called_once()

    response_mock.set_cookie.assert_called_once()

    assert isinstance(result, TokenResponse)
    assert result.access_token == access_token


async def test_register_username_already_exists(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    user_data = UserCreate(
        fullname="Test User",
        username="existing_user",
        password="Password123",
        email="test@example.com",
    )

    user_repository_mock.get_by_username.return_value = mock_user

    with pytest.raises(UsernameAlreadyExistsException):
        await auth_service.register(user_data, response_mock)

    user_repository_mock.get_by_username.assert_called_once_with(user_data.username)
    user_repository_mock.get_by_email.assert_not_called()
    user_repository_mock.create.assert_not_called()


async def test_register_email_already_exists(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    user_data = UserCreate(
        fullname="Test User",
        username="testuser",
        password="Password123",
        email="existing@example.com",
    )

    user_repository_mock.get_by_username.return_value = None
    user_repository_mock.get_by_email.return_value = mock_user

    with pytest.raises(EmailAlreadyExistsException):
        await auth_service.register(user_data, response_mock)

    user_repository_mock.get_by_username.assert_called_once_with(user_data.username)
    user_repository_mock.get_by_email.assert_called_once_with(user_data.email)
    user_repository_mock.create.assert_not_called()


# Login tests
async def test_login_success(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    password_hasher_mock: MagicMock,
    token_service_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    login_data = UserLogin(
        username="testuser",
        password="Password123",
    )

    rate_limiter_mock.login_rate_limit.return_value = (True, 5)
    user_repository_mock.get_by_username.return_value = mock_user
    password_hasher_mock.verify.return_value = True

    access_token = "test_access_token"
    refresh_token = "test_refresh_token"
    expires_at = datetime.now(UTC) + timedelta(days=7)
    token_service_mock.create_tokens.return_value = (
        access_token,
        refresh_token,
        expires_at,
    )

    result = await auth_service.login(login_data, response_mock)

    rate_limiter_mock.login_rate_limit.assert_called_once()
    user_repository_mock.get_by_username.assert_called_once_with(login_data.username)
    password_hasher_mock.verify.assert_called_once_with(
        login_data.password, mock_user.hashed_password
    )
    token_service_mock.create_tokens.assert_called_once_with(mock_user)

    response_mock.set_cookie.assert_called_once()

    assert isinstance(result, TokenResponse)
    assert result.access_token == access_token


async def test_login_invalid_credentials(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
) -> None:
    login_data = UserLogin(
        username="nonexistent",
        password="Password123",
    )

    rate_limiter_mock.login_rate_limit.return_value = (True, 5)
    user_repository_mock.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(login_data, response_mock)

    rate_limiter_mock.login_rate_limit.assert_called_once()
    user_repository_mock.get_by_username.assert_called_once_with(login_data.username)


async def test_login_wrong_password(
    auth_service: AuthService,
    response_mock: MagicMock,
    user_repository_mock: AsyncMock,
    password_hasher_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    login_data = UserLogin(
        username="testuser",
        password="WrongPassword",
    )

    rate_limiter_mock.login_rate_limit.return_value = (True, 5)
    user_repository_mock.get_by_username.return_value = mock_user
    password_hasher_mock.verify.return_value = False

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(login_data, response_mock)

    password_hasher_mock.verify.assert_called_once_with(
        login_data.password, mock_user.hashed_password
    )


async def test_login_rate_limit_exceeded(
    auth_service: AuthService,
    response_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
) -> None:
    login_data = UserLogin(
        username="testuser",
        password="Password123",
    )

    rate_limiter_mock.login_rate_limit.return_value = (False, 0)

    with pytest.raises(LoginRateLimitExceededException):
        await auth_service.login(login_data, response_mock)

    rate_limiter_mock.login_rate_limit.assert_called_once()


# Refresh token tests
async def test_refresh_token_success(
    auth_service: AuthService,
    request_mock: MagicMock,
    response_mock: MagicMock,
    token_service_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
) -> None:
    request_mock.cookies = {"refresh_token": "old_refresh_token"}

    rate_limiter_mock.refresh_token_rate_limit_by_ip.return_value = (True, 10)

    access_token = "new_access_token"
    refresh_token = "new_refresh_token"
    expires_at = datetime.now(UTC) + timedelta(days=7)
    token_service_mock.rotate_refresh_token.return_value = (
        access_token,
        refresh_token,
        expires_at,
    )

    result = await auth_service.refresh_token(response_mock)

    rate_limiter_mock.refresh_token_rate_limit_by_ip.assert_called_once_with(
        ip_address="127.0.0.1"
    )
    token_service_mock.rotate_refresh_token.assert_called_once_with("old_refresh_token")

    response_mock.set_cookie.assert_called_once()

    assert isinstance(result, TokenResponse)
    assert result.access_token == access_token


async def test_refresh_token_missing(
    auth_service: AuthService,
    request_mock: MagicMock,
    response_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
) -> None:
    request_mock.cookies = {}

    rate_limiter_mock.refresh_token_rate_limit_by_ip.return_value = (True, 10)

    with pytest.raises(RefreshTokenMissingException):
        await auth_service.refresh_token(response_mock)


async def test_refresh_token_rate_limit_exceeded(
    auth_service: AuthService,
    response_mock: MagicMock,
    rate_limiter_mock: AsyncMock,
) -> None:
    rate_limiter_mock.refresh_token_rate_limit_by_ip.return_value = (False, 0)

    with pytest.raises(TokenRefreshRateLimitExceededException):
        await auth_service.refresh_token(response_mock)


# Logout tests
async def test_logout_success(
    auth_service: AuthService,
    request_mock: MagicMock,
    response_mock: MagicMock,
    token_service_mock: AsyncMock,
) -> None:
    request_mock.headers = {"Authorization": "Bearer access_token"}
    request_mock.cookies = {"refresh_token": "refresh_token"}

    await auth_service.logout(response_mock)

    token_service_mock.blacklist_access_token.assert_called_once_with("access_token")
    token_service_mock.revoke_refresh_token.assert_called_once_with("refresh_token")
    response_mock.delete_cookie.assert_called_once_with(
        key="refresh_token",
        path="/",
    )


async def test_logout_no_tokens(
    auth_service: AuthService,
    request_mock: MagicMock,
    response_mock: MagicMock,
    token_service_mock: AsyncMock,
) -> None:
    request_mock.headers = {}
    request_mock.cookies = {}

    await auth_service.logout(response_mock)

    token_service_mock.blacklist_access_token.assert_not_called()
    token_service_mock.revoke_refresh_token.assert_not_called()
    response_mock.delete_cookie.assert_called_once()


# Change password tests
async def test_change_password_success(
    auth_service: AuthService,
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
    rate_limiter_mock.password_change_rate_limit.return_value = (True, 2)
    password_hasher_mock.verify.return_value = True
    password_hasher_mock.hash.return_value = "new_hashed_password"

    await auth_service.change_password(password_data)

    identity_provider_mock.get_current_user.assert_called_once()
    rate_limiter_mock.password_change_rate_limit.assert_called_once_with(mock_user.id)
    password_hasher_mock.verify.assert_called_once_with(
        password_data.current_password, mock_user.hashed_password
    )
    password_hasher_mock.hash.assert_called_once_with(password_data.new_password)
    user_repository_mock.update_password.assert_called_once_with(
        mock_user.id, "new_hashed_password"
    )
    transaction_manager_mock.commit.assert_called_once()


async def test_change_password_user_not_found(
    auth_service: AuthService,
    identity_provider_mock: AsyncMock,
) -> None:
    password_data = PasswordChange(
        current_password="OldPassword123",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = None

    with pytest.raises(UserNotFoundException):
        await auth_service.change_password(password_data)


async def test_change_password_incorrect_current(
    auth_service: AuthService,
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
    rate_limiter_mock.password_change_rate_limit.return_value = (True, 2)
    password_hasher_mock.verify.return_value = False

    with pytest.raises(IncorrectPasswordException):
        await auth_service.change_password(password_data)


async def test_change_password_rate_limit_exceeded(
    auth_service: AuthService,
    identity_provider_mock: AsyncMock,
    rate_limiter_mock: AsyncMock,
    mock_user: User,
) -> None:
    password_data = PasswordChange(
        current_password="OldPassword123",
        new_password="NewPassword123",
    )

    identity_provider_mock.get_current_user.return_value = mock_user
    rate_limiter_mock.password_change_rate_limit.return_value = (False, 0)

    with pytest.raises(PasswordChangeRateLimitExceededException):
        await auth_service.change_password(password_data)
