import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from isp_compare.api.v1.auth import router as auth_router
from isp_compare.api.v1.provider import router as provider_router
from isp_compare.api.v1.review import router as review_router
from isp_compare.api.v1.search_history import router as search_history_router
from isp_compare.api.v1.tariff import router as tariff_router
from isp_compare.api.v1.user import router as settings_router
from isp_compare.core.config import (
    ApplicationConfig,
    Config,
    CookieConfig,
    JWTConfig,
    PostgresConfig,
    RedisConfig,
)
from isp_compare.core.di.providers.core import ConfigProvider
from isp_compare.core.di.providers.database import DatabaseProvider
from isp_compare.core.di.providers.repository import RepositoryProvider
from isp_compare.core.di.providers.service import ServiceProvider
from isp_compare.models.base import Base

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def postgres_config() -> PostgresConfig:
    return PostgresConfig(
        host=os.getenv("TEST_POSTGRES_HOST", "localhost"),
        port=int(os.getenv("TEST_POSTGRES_PORT", "5433")),
        user=os.getenv("TEST_POSTGRES_USER", "postgres"),
        password=SecretStr(os.getenv("TEST_POSTGRES_PASSWORD", "postgres")),
        db=os.getenv("TEST_POSTGRES_DB", "isp_compare_test"),
        enable_logging=False,
    )


@pytest.fixture(scope="session")
def redis_config() -> RedisConfig:
    return RedisConfig(
        host=os.getenv("TEST_REDIS_HOST", "localhost"),
        port=int(os.getenv("TEST_REDIS_PORT", "6379")),
        password=os.getenv("TEST_REDIS_PASSWORD", "redis_password"),
    )


@pytest.fixture(scope="session")
def jwt_config() -> JWTConfig:
    """Create JWT config for tests."""
    return JWTConfig(
        secret_key=SecretStr("test_secret_key"),
        algorithm="HS256",
        access_token_expires_minutes=30,
        refresh_token_expires_days=7,
    )


@pytest.fixture(scope="session")
def cookie_config() -> CookieConfig:
    """Create Cookie config for tests."""
    return CookieConfig(
        secure=False,
        refresh_token_key="refresh_token",  # noqa: S106
        samesite="lax",
        path="/",
        httponly=True,
    )


@pytest.fixture(scope="session")
def app_config() -> ApplicationConfig:
    """Create application config for tests."""
    return ApplicationConfig(
        title="ISP Compare Test",
        debug=True,
    )


@pytest.fixture(scope="session")
def config(
    app_config: ApplicationConfig,
    jwt_config: JWTConfig,
    cookie_config: CookieConfig,
    postgres_config: PostgresConfig,
    redis_config: RedisConfig,
) -> Config:
    """Create full config for tests."""
    return Config(
        app=app_config,
        jwt=jwt_config,
        cookie=cookie_config,
        postgres=postgres_config,
        redis=redis_config,
    )


@pytest.fixture(scope="session")
async def engine(postgres_config: PostgresConfig) -> AsyncGenerator[AsyncEngine]:
    """Create SQLAlchemy engine for tests."""
    engine = create_async_engine(
        postgres_config.build_dsn(),
        echo=postgres_config.enable_logging,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session")
def session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session maker for tests."""
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Create database session for tests."""
    async with session_maker() as session:
        # Transaction should be mocked to avoid actual commits
        session.commit = AsyncMock()
        yield session
        await session.rollback()


@pytest.fixture
def mock_database_provider(session: AsyncSession) -> Provider:
    class MockProvider(DatabaseProvider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncSession:
            return session

    return MockProvider()


@pytest.fixture
def container(mock_database_provider: Provider) -> AsyncContainer:
    """Create container for tests."""
    return make_async_container(
        FastapiProvider(),
        ConfigProvider(),
        mock_database_provider,
        RepositoryProvider(),
        ServiceProvider(),
        context={Config: MagicMock()},
    )


@pytest.fixture
async def fastapi_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(settings_router)

    app.include_router(provider_router)
    app.include_router(tariff_router)
    app.include_router(review_router)
    app.include_router(search_history_router)

    setup_dishka(container, app)
    return app


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Create an async test client for FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client
