import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Generator
from typing import Any

import pytest
from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from isp_compare.admin import setup_admin
from isp_compare.api import main_router
from isp_compare.core.config import Config
from isp_compare.core.di.providers.core import ConfigProvider
from isp_compare.core.di.providers.repository import RepositoryProvider
from isp_compare.core.di.providers.service import ServiceProvider


@pytest.fixture(autouse=True, scope="session")
def event_loop() -> Generator[AbstractEventLoop, Any]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def container(config: Config, mock_database_provider: Provider) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        ConfigProvider(),
        mock_database_provider,
        RepositoryProvider(),
        ServiceProvider(),
        context={Config: config},
    )


@pytest.fixture
async def fastapi_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI()
    app.include_router(main_router, prefix="/api")

    setup_dishka(container, app)
    await setup_admin(app)
    return app
