from typing import TYPE_CHECKING

from jose import JWTError, jwt
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from isp_compare.core.config import JWTConfig
from isp_compare.repositories.user import UserRepository
from isp_compare.services.password_hasher import PasswordHasher

if TYPE_CHECKING:
    from dishka import AsyncContainer


class AdminAuth(AuthenticationBackend):
    def __init__(
        self,
        secret_key: str,
        jwt_config: JWTConfig,
    ) -> None:
        super().__init__(secret_key)
        self.secret_key = secret_key
        self.jwt_config = jwt_config

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username: str | None = form.get("username")
        password: str | None = form.get("password")
        if not username or not password:
            return False

        container: AsyncContainer = request.state.dishka_container
        async with container() as nested_container:
            user_repository = await nested_container.get(UserRepository)
            password_hasher = await nested_container.get(PasswordHasher)

            user = await user_repository.get_by_username(username)

            if not user or not password_hasher.verify(password, user.hashed_password):
                return False

            if not user.is_admin:
                return False

            token = jwt.encode(
                {"sub": str(user.id), "is_admin": True},
                self.secret_key,
                algorithm=self.jwt_config.algorithm,
            )

            request.session.update({"token": token})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.jwt_config.algorithm],
            )
            if not payload.get("is_admin"):
                return False

        except JWTError:
            return False
        return True
