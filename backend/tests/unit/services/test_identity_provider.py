import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faker import Faker
from fastapi import Request
from jose import JWTError

from isp_compare.core.exceptions import (
    AdminAccessDeniedException,
    InvalidTokenException,
    TokenRevokedException,
    UserNotFoundException,
)
from isp_compare.models.user import User
from isp_compare.repositories.user import UserRepository
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.token_processor import TokenProcessor
from isp_compare.services.token_service import TokenService


@pytest.fixture
def request_mock() -> MagicMock:
    request = MagicMock(spec=Request)
    request.headers = {"Authorization": "Bearer valid_token"}
    return request


@pytest.fixture
def token_processor_mock() -> MagicMock:
    processor = MagicMock(spec=TokenProcessor)
    processor.get_user_id_from_token.return_value = uuid.uuid4()
    return processor


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def token_service_mock() -> AsyncMock:
    service = AsyncMock(spec=TokenService)
    service.is_access_token_blacklisted.return_value = False
    return service


@pytest.fixture
def identity_provider(
    request_mock: MagicMock,
    token_processor_mock: MagicMock,
    user_repository_mock: AsyncMock,
    token_service_mock: AsyncMock,
) -> IdentityProvider:
    return IdentityProvider(
        request=request_mock,
        token_processor=token_processor_mock,
        user_repository=user_repository_mock,
        token_service=token_service_mock,
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


async def test_get_current_user_id_success(
    identity_provider: IdentityProvider,
    token_processor_mock: MagicMock,
    token_service_mock: AsyncMock,
) -> None:
    user_id = uuid.uuid4()
    token_processor_mock.get_user_id_from_token.return_value = user_id

    result = await identity_provider.get_current_user_id()

    token_service_mock.is_access_token_blacklisted.assert_called_once_with(
        "valid_token"
    )
    token_processor_mock.get_user_id_from_token.assert_called_once_with("valid_token")
    assert result == user_id


async def test_get_current_user_id_no_authorization(
    identity_provider: IdentityProvider, request_mock: MagicMock
) -> None:
    request_mock.headers = {}

    with pytest.raises(InvalidTokenException):
        await identity_provider.get_current_user_id()


async def test_get_current_user_id_invalid_authorization_format(
    identity_provider: IdentityProvider, request_mock: MagicMock
) -> None:
    request_mock.headers = {"Authorization": "invalid_format"}

    with pytest.raises(InvalidTokenException):
        await identity_provider.get_current_user_id()


async def test_get_current_user_id_blacklisted_token(
    identity_provider: IdentityProvider, token_service_mock: AsyncMock
) -> None:
    token_service_mock.is_access_token_blacklisted.return_value = True

    with pytest.raises(TokenRevokedException):
        await identity_provider.get_current_user_id()

    token_service_mock.is_access_token_blacklisted.assert_called_once_with(
        "valid_token"
    )


async def test_get_current_user_id_jwt_error(
    identity_provider: IdentityProvider, token_processor_mock: MagicMock
) -> None:
    token_processor_mock.get_user_id_from_token.side_effect = JWTError("Invalid token")

    with pytest.raises(InvalidTokenException):
        await identity_provider.get_current_user_id()

    token_processor_mock.get_user_id_from_token.assert_called_once_with("valid_token")


async def test_get_current_user_id_value_error(
    identity_provider: IdentityProvider, token_processor_mock: MagicMock
) -> None:
    token_processor_mock.get_user_id_from_token.side_effect = ValueError("Invalid UUID")

    with pytest.raises(InvalidTokenException):
        await identity_provider.get_current_user_id()

    token_processor_mock.get_user_id_from_token.assert_called_once_with("valid_token")


async def test_get_current_user_success(
    identity_provider: IdentityProvider,
    user_repository_mock: AsyncMock,
    mock_user: User,
) -> None:
    user_id = uuid.uuid4()
    with patch.object(
        identity_provider, "get_current_user_id", return_value=user_id
    ) as mock_get_id:
        user_repository_mock.get_by_id.return_value = mock_user

        result = await identity_provider.get_current_user()

        mock_get_id.assert_called_once()
        user_repository_mock.get_by_id.assert_called_once_with(user_id)
        assert result == mock_user


async def test_get_current_user_not_found(
    identity_provider: IdentityProvider, user_repository_mock: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    with patch.object(
        identity_provider, "get_current_user_id", return_value=user_id
    ) as mock_get_id:
        user_repository_mock.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            await identity_provider.get_current_user()

        mock_get_id.assert_called_once()
        user_repository_mock.get_by_id.assert_called_once_with(user_id)


async def test_ensure_is_admin_success(
    identity_provider: IdentityProvider, admin_user: User
) -> None:
    with patch.object(
        identity_provider, "get_current_user", return_value=admin_user
    ) as mock_get_user:
        await identity_provider.ensure_is_admin()
        mock_get_user.assert_called_once()


async def test_ensure_is_admin_not_admin(
    identity_provider: IdentityProvider, mock_user: User
) -> None:
    with patch.object(
        identity_provider, "get_current_user", return_value=mock_user
    ) as mock_get_user:
        with pytest.raises(AdminAccessDeniedException):
            await identity_provider.ensure_is_admin()
        mock_get_user.assert_called_once()
