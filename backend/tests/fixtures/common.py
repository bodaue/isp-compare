import pytest
from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

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
    return app
