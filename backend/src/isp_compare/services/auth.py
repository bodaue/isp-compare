from typing import cast

from asyncpg import UniqueViolationError
from fastapi import Request, Response
from sqlalchemy.exc import IntegrityError

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
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.password_hasher import PasswordHasher
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.token_processor import TokenProcessor
from isp_compare.services.token_service import TokenService
from isp_compare.services.transaction_manager import TransactionManager


class AuthService:
    def __init__(
        self,
        request: Request,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        jwt_config: JWTConfig,
        cookie_config: CookieConfig,
        password_hasher: PasswordHasher,
        token_processor: TokenProcessor,
        token_service: TokenService,
        identity_provider: IdentityProvider,
        rate_limiter: RateLimiter,
    ) -> None:
        self._request = request
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager
        self._jwt_config = jwt_config
        self._cookie_config = cookie_config
        self._password_hasher = password_hasher
        self._token_processor = token_processor
        self._token_service = token_service
        self._identity_provider = identity_provider
        self._rate_limiter = rate_limiter

    async def register(self, data: UserCreate, response: Response) -> TokenResponse:
        hashed_password = self._password_hasher.hash(data.password)

        user = User(
            fullname=data.fullname,
            username=data.username,
            hashed_password=hashed_password,
            email=data.email,
        )
        try:
            await self._user_repository.create(user)
            await self._transaction_manager.commit()
        except IntegrityError as e:
            orig = cast("BaseException", e.orig)
            if isinstance(orig.__cause__, UniqueViolationError):
                error_detail = str(e).lower()
                if "uq_users_username" in error_detail:
                    raise UsernameAlreadyExistsException from e
                if "uq_users_email" in error_detail:
                    raise EmailAlreadyExistsException from e
            raise e from e

        (
            access_token,
            refresh_token,
            refresh_expires,
        ) = await self._token_service.create_tokens(user, skip_revocation=True)

        response.set_cookie(
            key=self._cookie_config.refresh_token_key,
            value=refresh_token,
            httponly=self._cookie_config.httponly,
            secure=self._cookie_config.secure,
            samesite=self._cookie_config.samesite,
            expires=refresh_expires,
            path=self._cookie_config.path,
        )

        return TokenResponse(access_token=access_token)

    async def login(self, data: UserLogin, response: Response) -> TokenResponse:
        client_ip = self._request.client.host if self._request.client else "unknown"
        is_allowed, remaining = await self._rate_limiter.login_rate_limit(
            ip_address=client_ip
        )
        if not is_allowed:
            raise LoginRateLimitExceededException(retry_after=300)

        user = await self._user_repository.get_by_username(data.username)
        if not user or not self._password_hasher.verify(
            data.password, user.hashed_password
        ):
            if remaining == 0:
                raise InvalidCredentialsException(
                    remaining_attempts=0,
                    max_attempts=5,
                    is_last_attempt=True,
                    retry_after=300,
                )
            raise InvalidCredentialsException(
                remaining_attempts=remaining, max_attempts=5
            )

        (
            access_token,
            refresh_token,
            refresh_expires,
        ) = await self._token_service.create_tokens(user)

        response.set_cookie(
            key=self._cookie_config.refresh_token_key,
            value=refresh_token,
            httponly=self._cookie_config.httponly,
            secure=self._cookie_config.secure,
            samesite=self._cookie_config.samesite,
            expires=refresh_expires,
            path=self._cookie_config.path,
        )

        return TokenResponse(access_token=access_token)

    async def refresh_token(self, response: Response) -> TokenResponse:
        client_ip = self._request.client.host if self._request.client else "unknown"
        is_allowed, remaining = await self._rate_limiter.refresh_token_rate_limit_by_ip(
            ip_address=client_ip
        )
        if not is_allowed:
            raise TokenRefreshRateLimitExceededException

        refresh_token = self._request.cookies.get("refresh_token")

        if not refresh_token:
            raise RefreshTokenMissingException

        (
            access_token,
            new_refresh_token,
            expires_at,
        ) = await self._token_service.rotate_refresh_token(refresh_token)

        response.set_cookie(
            key=self._cookie_config.refresh_token_key,
            value=new_refresh_token,
            httponly=self._cookie_config.httponly,
            secure=self._cookie_config.secure,
            samesite=self._cookie_config.samesite,
            expires=expires_at,
            path=self._cookie_config.path,
        )

        return TokenResponse(access_token=access_token)

    async def logout(self, response: Response) -> None:
        authorization = self._request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):
            access_token = authorization.replace("Bearer ", "")
            await self._token_service.blacklist_access_token(access_token)

        refresh_token = self._request.cookies.get("refresh_token")
        if refresh_token:
            await self._token_service.revoke_refresh_token(refresh_token)

        response.delete_cookie(
            key=self._cookie_config.refresh_token_key,
            path=self._cookie_config.path,
        )

    async def change_password(self, data: PasswordChange) -> None:
        user = await self._identity_provider.get_current_user()
        if not user:
            raise UserNotFoundException

        is_allowed, remaining = await self._rate_limiter.password_change_rate_limit(
            user.id
        )
        if not is_allowed:
            raise PasswordChangeRateLimitExceededException

        if not self._password_hasher.verify(
            data.current_password, user.hashed_password
        ):
            raise IncorrectPasswordException

        hashed_password = self._password_hasher.hash(data.new_password)

        await self._user_repository.update_password(user.id, hashed_password)

        await self._transaction_manager.commit()
