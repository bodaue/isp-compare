from dishka import Provider, Scope, provide
from repositories.token import RefreshTokenRepository
from repositories.user import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    user_repository = provide(UserRepository)
    refresh_token_repository = provide(RefreshTokenRepository)
