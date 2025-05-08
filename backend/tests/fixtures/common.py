import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Generator
from typing import Any

import pytest
from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from isp_compare.admin import setup_admin
from isp_compare.api.v1.auth import router as auth_router
from isp_compare.api.v1.provider import router as provider_router
from isp_compare.api.v1.review import router as review_router
from isp_compare.api.v1.search_history import router as search_history_router
from isp_compare.api.v1.tariff import router as tariff_router
from isp_compare.api.v1.user import router as settings_router
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
    app.include_router(auth_router)
    app.include_router(settings_router)

    app.include_router(provider_router)
    app.include_router(tariff_router)
    app.include_router(review_router)
    app.include_router(search_history_router)

    setup_dishka(container, app)
    await setup_admin(app)
    return app
