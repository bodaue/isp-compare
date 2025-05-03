from typing import TYPE_CHECKING

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from isp_compare.api.v1.auth import router as auth_router
from isp_compare.api.v1.provider import router as provider_router
from isp_compare.api.v1.review import router as review_router
from isp_compare.api.v1.search_history import router as search_history_router
from isp_compare.api.v1.tariff import router as tariff_router
from isp_compare.api.v1.user import router as settings_router
from isp_compare.core.config import Config, create_config
from isp_compare.core.di.main import create_container

if TYPE_CHECKING:
    from dishka import AsyncContainer


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(settings_router)

    app.include_router(provider_router)
    app.include_router(tariff_router)
    app.include_router(review_router)
    app.include_router(search_history_router)


def create_application() -> FastAPI:
    config: Config = create_config()
    app: FastAPI = FastAPI(title=config.app.title, debug=config.app.debug)

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, specify the exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container: AsyncContainer = create_container(config)
    setup_dishka(container, app)

    setup_routers(app)

    return app
