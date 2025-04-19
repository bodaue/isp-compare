from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class ApplicationConfig(BaseSettings, env_prefix="APPLICATION_"):
    title: str
    debug: bool = False


class JWTConfig(BaseSettings, env_prefix="JWT_"):
    secret_key: SecretStr
    algorithm: str
    access_token_expires_minutes: int
    refresh_token_expires_days: int = 7


class CookieConfig(BaseSettings, env_prefix="COOKIE_"):
    secure: bool
    refresh_token_key: str
    samesite: Literal["strict", "lax", "none"]
    path: str
    httponly: bool


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str

    enable_logging: bool = False

    def build_dsn(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(hide_password=False)


class RedisConfig(BaseSettings, env_prefix="REDIS_"):
    host: str
    port: int
    password: str


class Config(BaseModel):
    app: ApplicationConfig
    jwt: JWTConfig
    cookie: CookieConfig
    postgres: PostgresConfig
    redis: RedisConfig


def create_config() -> Config:
    return Config(
        app=ApplicationConfig(),
        jwt=JWTConfig(),
        cookie=CookieConfig(),
        postgres=PostgresConfig(),
        redis=RedisConfig(),
    )
