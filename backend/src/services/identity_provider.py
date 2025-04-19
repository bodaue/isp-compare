from uuid import UUID

from core.exceptions import (
    InvalidTokenException,
    TokenRevokedException,
    UserNotFoundException,
)
from fastapi import Request
from jose import JWTError
from models import User
from repositories.user import UserRepository

from services.token_processor import TokenProcessor
from services.token_service import TokenService


class IdentityProvider:
    def __init__(
        self,
        request: Request,
        token_processor: TokenProcessor,
        user_repository: UserRepository,
        token_service: TokenService,
    ) -> None:
        self._request = request
        self._token_processor = token_processor
        self._user_repository = user_repository
        self._token_service = token_service

    async def get_current_user_id(self) -> UUID:
        authorization = self._request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise InvalidTokenException

        token = authorization.replace("Bearer ", "")

        try:
            is_blacklisted = await self._token_service.is_access_token_blacklisted(
                token
            )
            if is_blacklisted:
                raise TokenRevokedException

            return self._token_processor.get_user_id_from_token(token)

        except (JWTError, ValueError) as e:
            raise InvalidTokenException from e

    async def get_current_user(self) -> User:
        user_id = await self.get_current_user_id()
        user = await self._user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException

        return user
