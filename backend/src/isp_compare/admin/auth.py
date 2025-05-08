from jose import JWTError, jwt
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from isp_compare.core.config import JWTConfig
from isp_compare.repositories.user import UserRepository
from isp_compare.services.password_hasher import PasswordHasher


class AdminAuth(AuthenticationBackend):
    def __init__(
        self,
        secret_key: str,
        session_maker: async_sessionmaker[AsyncSession],
        jwt_config: JWTConfig,
        password_hasher: PasswordHasher,
    ) -> None:
        super().__init__(secret_key)
        self.secret_key = secret_key
        self.session_maker = session_maker
        self.jwt_config = jwt_config
        self.password_hasher = password_hasher

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        async with self.session_maker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.get_by_username(username)

            if not user or not self.password_hasher.verify(
                password, user.hashed_password
            ):
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
