from typing import TYPE_CHECKING

from api.v1.auth import router as auth_router
from api.v1.user import router as settings_router
from core.config import Config, create_config
from core.di.main import create_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from dishka import AsyncContainer


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(settings_router)


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
