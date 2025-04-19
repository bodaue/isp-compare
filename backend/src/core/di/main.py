from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from core.config import Config
from core.di.providers.core import ConfigProvider
from core.di.providers.database import DatabaseProvider
from core.di.providers.repository import RepositoryProvider
from core.di.providers.service import ServiceProvider


def create_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        context={Config: config},
    )
