from core.config import CookieConfig, JWTConfig
from core.exceptions import (
    EmailAlreadyExistsException,
    IncorrectPasswordException,
    InvalidCredentialsException,
    RefreshTokenMissingException,
    UsernameAlreadyExistsException,
    UserNotFoundException,
)
from fastapi import Request, Response
from models.user import User
from repositories.user import UserRepository
from schemas.user import (
    PasswordChange,
    TokenResponse,
    UserCreate,
    UserLogin,
)

from services.identity_provider import IdentityProvider
from services.password_hasher import PasswordHasher
from services.token_processor import TokenProcessor
from services.token_service import TokenService
from services.transaction_manager import TransactionManager


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

    async def register(self, data: UserCreate, response: Response) -> TokenResponse:
        existing_username = await self._user_repository.get_by_username(data.username)
        if existing_username:
            raise UsernameAlreadyExistsException

        existing_email = await self._user_repository.get_by_email(data.email)
        if existing_email:
            raise EmailAlreadyExistsException

        hashed_password = self._password_hasher.hash(data.password)

        user = User(
            fullname=data.fullname,
            username=data.username,
            hashed_password=hashed_password,
            email=data.email,
        )
        await self._user_repository.create(user)
        await self._transaction_manager.commit()

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

    async def login(self, data: UserLogin, response: Response) -> TokenResponse:
        user = await self._user_repository.get_by_username(data.username)
        if not user or not self._password_hasher.verify(
            data.password, user.hashed_password
        ):
            raise InvalidCredentialsException

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
            value=refresh_token,
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

        if not self._password_hasher.verify(
            data.current_password, user.hashed_password
        ):
            raise IncorrectPasswordException

        hashed_password = self._password_hasher.hash(data.new_password)

        await self._user_repository.update_password(user.id, hashed_password)

        await self._transaction_manager.commit()
