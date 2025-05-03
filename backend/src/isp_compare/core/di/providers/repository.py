from dishka import Provider, Scope, provide

from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.token import RefreshTokenRepository
from isp_compare.repositories.user import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    user_repository = provide(UserRepository)
    refresh_token_repository = provide(RefreshTokenRepository)

    provider_repository = provide(ProviderRepository)
