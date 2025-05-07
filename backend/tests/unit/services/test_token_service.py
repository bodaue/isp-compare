import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
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
from isp_compare.services.token_service import TokenService
from isp_compare.services.transaction_manager import TransactionManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def token_processor_mock() -> MagicMock:
    mock = MagicMock(spec=TokenProcessor)
    mock.create_access_token.return_value = "test_access_token"
    mock.create_refresh_token.return_value = (
        "test_refresh_token",
        datetime.now(UTC) + timedelta(days=7),
    )
    return mock


@pytest.fixture
def refresh_token_repository_mock() -> AsyncMock:
    return AsyncMock(spec=RefreshTokenRepository)


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def transaction_manager_mock() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def redis_client_mock() -> AsyncMock:
    redis_mock = AsyncMock(spec=Redis)
    redis_mock.set = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    return redis_mock


@pytest.fixture
def token_service(
    token_processor_mock: MagicMock,
    refresh_token_repository_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
    redis_client_mock: AsyncMock,
) -> TokenService:
    return TokenService(
        token_processor=token_processor_mock,
        refresh_token_repository=refresh_token_repository_mock,
        user_repository=user_repository_mock,
        transaction_manager=transaction_manager_mock,
        redis_client=redis_client_mock,
    )


@pytest.fixture
def refresh_token(regular_user: User) -> RefreshToken:
    return RefreshToken(
        id=uuid.uuid4(),
        token="valid_refresh_token",
        user_id=regular_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=1),
        revoked=False,
    )


@pytest.fixture
def expired_refresh_token(regular_user: User) -> RefreshToken:
    return RefreshToken(
        id=uuid.uuid4(),
        token="expired_refresh_token",
        user_id=regular_user.id,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        revoked=False,
    )


@pytest.fixture
def revoked_refresh_token(regular_user: User) -> RefreshToken:
    return RefreshToken(
        id=uuid.uuid4(),
        token="revoked_refresh_token",
        user_id=regular_user.id,
        expires_at=datetime.now(UTC) + timedelta(days=1),
        revoked=True,
        revoked_at=datetime.now(UTC) - timedelta(hours=1),
    )


async def test_create_tokens(
    token_service: TokenService,
    regular_user: User,
    token_processor_mock: MagicMock,
    refresh_token_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
) -> None:
    access_token, refresh_token, expires_at = await token_service.create_tokens(
        regular_user
    )

    refresh_token_repository_mock.revoke_all_for_user.assert_called_once_with(
        regular_user.id
    )
    token_processor_mock.create_access_token.assert_called_once_with(
        user_id=regular_user.id
    )
    token_processor_mock.create_refresh_token.assert_called_once()

    assert refresh_token_repository_mock.create.call_count == 1
    created_token = refresh_token_repository_mock.create.call_args[0][0]
    assert isinstance(created_token, RefreshToken)
    assert created_token.token == "test_refresh_token"
    assert created_token.user_id == regular_user.id

    transaction_manager_mock.commit.assert_called_once()

    assert access_token == "test_access_token"
    assert refresh_token == "test_refresh_token"
    assert expires_at > datetime.now(UTC)


async def test_revoke_refresh_token(
    token_service: TokenService,
    refresh_token_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
) -> None:
    await token_service.revoke_refresh_token("test_token")

    refresh_token_repository_mock.revoke.assert_called_once_with("test_token")
    transaction_manager_mock.commit.assert_called_once()


async def test_blacklist_access_token_valid(
    token_service: TokenService,
    token_processor_mock: MagicMock,
    redis_client_mock: AsyncMock,
) -> None:
    token_processor_mock.decode_token.return_value = {
        "exp": int(datetime.now(UTC).timestamp()) + 1800
    }

    await token_service.blacklist_access_token("valid_token")

    token_processor_mock.decode_token.assert_called_once_with("valid_token")
    redis_client_mock.set.assert_called_once()
    _, kwargs = redis_client_mock.set.call_args
    assert abs(kwargs["ex"] - 1800) < 5


async def test_blacklist_access_token_no_expiry(
    token_service: TokenService,
    token_processor_mock: MagicMock,
    redis_client_mock: AsyncMock,
) -> None:
    token_processor_mock.decode_token.return_value = {}

    await token_service.blacklist_access_token("valid_token_no_exp")

    token_processor_mock.decode_token.assert_called_once_with("valid_token_no_exp")
    redis_client_mock.set.assert_called_once()
    _, kwargs = redis_client_mock.set.call_args
    assert kwargs["ex"] == 1800


async def test_blacklist_access_token_invalid(
    token_service: TokenService,
    token_processor_mock: MagicMock,
    redis_client_mock: AsyncMock,
) -> None:
    token_processor_mock.decode_token.side_effect = JWTError("Invalid token")

    await token_service.blacklist_access_token("invalid_token")

    token_processor_mock.decode_token.assert_called_once_with("invalid_token")
    redis_client_mock.set.assert_not_called()


async def test_is_access_token_blacklisted_true(
    token_service: TokenService,
    redis_client_mock: AsyncMock,
) -> None:
    redis_client_mock.get.return_value = "1"

    result = await token_service.is_access_token_blacklisted("blacklisted_token")

    assert result is True
    redis_client_mock.get.assert_called_once_with("blacklisted_token:blacklisted_token")


async def test_is_access_token_blacklisted_false(
    token_service: TokenService,
    redis_client_mock: AsyncMock,
) -> None:
    redis_client_mock.get.return_value = None

    result = await token_service.is_access_token_blacklisted("regular_token")

    assert result is False
    redis_client_mock.get.assert_called_once_with("blacklisted_token:regular_token")


async def test_rotate_refresh_token_success(
    token_service: TokenService,
    refresh_token: RefreshToken,
    regular_user: User,
    refresh_token_repository_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    token_processor_mock: MagicMock,
    transaction_manager_mock: AsyncMock,
) -> None:
    refresh_token_repository_mock.get_by_token.return_value = refresh_token
    user_repository_mock.get_by_id.return_value = regular_user

    (
        access_token,
        new_refresh_token,
        expires_at,
    ) = await token_service.rotate_refresh_token(refresh_token.token)

    refresh_token_repository_mock.get_by_token.assert_called_once_with(
        refresh_token.token
    )
    user_repository_mock.get_by_id.assert_called_once_with(refresh_token.user_id)
    refresh_token_repository_mock.revoke.assert_called_once_with(refresh_token.token)
    token_processor_mock.create_access_token.assert_called_once_with(
        user_id=regular_user.id
    )
    token_processor_mock.create_refresh_token.assert_called_once()

    assert refresh_token_repository_mock.create.call_count == 1
    created_token = refresh_token_repository_mock.create.call_args[0][0]
    assert isinstance(created_token, RefreshToken)
    assert created_token.token == "test_refresh_token"
    assert created_token.user_id == regular_user.id

    transaction_manager_mock.commit.assert_called_once()

    assert access_token == "test_access_token"
    assert new_refresh_token == "test_refresh_token"
    assert expires_at > datetime.now(UTC)


async def test_rotate_refresh_token_not_found(
    token_service: TokenService,
    refresh_token_repository_mock: AsyncMock,
) -> None:
    refresh_token_repository_mock.get_by_token.return_value = None

    with pytest.raises(InvalidTokenException):
        await token_service.rotate_refresh_token("nonexistent_token")

    refresh_token_repository_mock.get_by_token.assert_called_once_with(
        "nonexistent_token"
    )


async def test_rotate_refresh_token_expired(
    token_service: TokenService,
    expired_refresh_token: RefreshToken,
    refresh_token_repository_mock: AsyncMock,
) -> None:
    refresh_token_repository_mock.get_by_token.return_value = expired_refresh_token

    with pytest.raises(TokenExpiredException):
        await token_service.rotate_refresh_token(expired_refresh_token.token)

    refresh_token_repository_mock.get_by_token.assert_called_once_with(
        expired_refresh_token.token
    )


async def test_rotate_refresh_token_revoked(
    token_service: TokenService,
    revoked_refresh_token: RefreshToken,
    refresh_token_repository_mock: AsyncMock,
    transaction_manager_mock: AsyncMock,
) -> None:
    refresh_token_repository_mock.get_by_token.return_value = revoked_refresh_token

    with pytest.raises(TokenRevokedException):
        await token_service.rotate_refresh_token(revoked_refresh_token.token)

    refresh_token_repository_mock.get_by_token.assert_called_once_with(
        revoked_refresh_token.token
    )
    refresh_token_repository_mock.revoke_all_for_user.assert_called_once_with(
        revoked_refresh_token.user_id
    )
    transaction_manager_mock.commit.assert_called_once()


async def test_rotate_refresh_token_user_not_found(
    token_service: TokenService,
    refresh_token: RefreshToken,
    refresh_token_repository_mock: AsyncMock,
    user_repository_mock: AsyncMock,
) -> None:
    refresh_token_repository_mock.get_by_token.return_value = refresh_token
    user_repository_mock.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        await token_service.rotate_refresh_token(refresh_token.token)

    refresh_token_repository_mock.get_by_token.assert_called_once_with(
        refresh_token.token
    )
    user_repository_mock.get_by_id.assert_called_once_with(refresh_token.user_id)
