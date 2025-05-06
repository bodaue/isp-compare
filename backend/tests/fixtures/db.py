from collections.abc import AsyncGenerator

import fakeredis
import pytest
from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from isp_compare.core.config import PostgresConfig
from isp_compare.core.di.providers.database import DatabaseProvider
from isp_compare.models.base import Base


@pytest.fixture(scope="session")
async def engine(postgres_config: PostgresConfig) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        postgres_config.build_dsn(),
        echo=postgres_config.enable_logging,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session")
def session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def redis_client() -> Redis:
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def mock_database_provider(session: AsyncSession, redis_client: Redis) -> Provider:
    class MockProvider(DatabaseProvider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncSession:
            return session

        @provide(scope=Scope.APP)
        def redis_client(self) -> Redis:
            return redis_client

    return MockProvider()


@pytest.fixture(autouse=True)
async def clean_database(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))

        tables = Base.metadata.tables

        for table_name in tables:
            await conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE;'))

        await conn.execute(text("SET session_replication_role = 'origin';"))


@pytest.fixture(autouse=True)
async def clean_redis(redis_client: Redis) -> None:
    await redis_client.flushall()
