from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from services.transaction_manager import TransactionManager
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import Config


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, config: Config) -> AsyncEngine:
        return create_async_engine(config.postgres.build_dsn())

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
    def redis_client(self, config: Config) -> Redis:
        return Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
        )

    transaction_manager = provide(TransactionManager, scope=Scope.REQUEST)
