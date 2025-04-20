from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from isp_compare.core.config import Config
from isp_compare.core.di.providers.core import ConfigProvider
from isp_compare.core.di.providers.database import DatabaseProvider
from isp_compare.core.di.providers.repository import RepositoryProvider
from isp_compare.core.di.providers.service import ServiceProvider


def create_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        context={Config: config},
    )
