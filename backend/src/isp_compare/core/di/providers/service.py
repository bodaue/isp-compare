from dishka import Provider, Scope, provide

from isp_compare.services.auth import AuthService
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.parser_service import ParserService
from isp_compare.services.password_hasher import PasswordHasher
from isp_compare.services.provider import ProviderService
from isp_compare.services.rate_limiter import RateLimiter
from isp_compare.services.review import ReviewService
from isp_compare.services.search_history import SearchHistoryService
from isp_compare.services.tariff import TariffService
from isp_compare.services.tariff_comparison import TariffComparisonService
from isp_compare.services.token_processor import TokenProcessor
from isp_compare.services.token_service import TokenService
from isp_compare.services.user import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    password_hasher = provide(PasswordHasher, scope=Scope.APP)

    token_processor = provide(TokenProcessor)
    identity_provider = provide(IdentityProvider)
    auth_service = provide(AuthService)
    user_service = provide(UserService)
    token_service = provide(TokenService)

    provider_service = provide(ProviderService)
    tariff_service = provide(TariffService)
    tariff_comparison_service = provide(TariffComparisonService)
    review_service = provide(ReviewService)
    search_history_service = provide(SearchHistoryService)

    rate_limiter = provide(RateLimiter)
    parser_service = provide(ParserService)
