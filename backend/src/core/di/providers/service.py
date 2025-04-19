from dishka import Provider, Scope, provide
from services.auth import AuthService
from services.identity_provider import IdentityProvider
from services.password_hasher import PasswordHasher
from services.token_processor import TokenProcessor
from services.token_service import TokenService
from services.user import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    password_hasher = provide(PasswordHasher, scope=Scope.APP)

    token_processor = provide(TokenProcessor)
    identity_provider = provide(IdentityProvider)
    auth_service = provide(AuthService)
    user_service = provide(UserService)
    token_service = provide(TokenService)
