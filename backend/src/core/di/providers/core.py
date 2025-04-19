from dishka import Provider, Scope, from_context, provide

from core.config import Config, CookieConfig, JWTConfig, PostgresConfig, RedisConfig


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def get_jwt_config(self, config: Config) -> JWTConfig:
        return config.jwt

    @provide
    def get_cookie_config(self, config: Config) -> CookieConfig:
        return config.cookie

    @provide
    def get_postgres_config(self, config: Config) -> PostgresConfig:
        return config.postgres

    @provide
    def get_redis_config(self, config: Config) -> RedisConfig:
        return config.redis
