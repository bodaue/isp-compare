from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from isp_compare.core.config import PostgresConfig, RedisConfig
from isp_compare.services.transaction_manager import TransactionManager


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, config: PostgresConfig) -> AsyncEngine:
        return create_async_engine(config.build_dsn(), echo=config.enable_logging)

    @provide(scope=Scope.APP)
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.APP)
    def redis_client(self, config: RedisConfig) -> Redis:
        return Redis(
            host=config.host,
            port=config.port,
            password=config.password.get_secret_value(),
        )

    transaction_manager = provide(TransactionManager, scope=Scope.REQUEST)
