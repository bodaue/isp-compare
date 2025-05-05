import os

import pytest
from pydantic import SecretStr

from isp_compare.core.config import (
    ApplicationConfig,
    Config,
    CookieConfig,
    JWTConfig,
    PostgresConfig,
    RedisConfig,
)


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
    return JWTConfig(
        secret_key=SecretStr("test_secret_key"),
        algorithm="HS256",
        access_token_expires_minutes=30,
        refresh_token_expires_days=7,
    )


@pytest.fixture(scope="session")
def cookie_config() -> CookieConfig:
    return CookieConfig(
        secure=False,
        refresh_token_key="refresh_token",  # noqa: S106
        samesite="lax",
        path="/",
        httponly=True,
    )


@pytest.fixture(scope="session")
def app_config() -> ApplicationConfig:
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
    return Config(
        app=app_config,
        jwt=jwt_config,
        cookie=cookie_config,
        postgres=postgres_config,
        redis=redis_config,
    )
