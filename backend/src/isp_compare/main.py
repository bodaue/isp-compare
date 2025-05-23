from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from isp_compare.admin import setup_admin
from isp_compare.api import main_router
from isp_compare.core.config import Config, create_config
from isp_compare.core.di.main import create_container

if TYPE_CHECKING:
    from dishka import AsyncContainer


def setup_routers(app: FastAPI) -> None:
    app.include_router(main_router, prefix="/api")


def setup_middlewares(app: FastAPI, config: Config) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.jwt.secret_key.get_secret_value(),
    )
    origins = [
        "https://ispcompare.ru",
        "https://www.ispcompare.ru",
        "http://localhost:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await setup_admin(app)
    yield


def create_application() -> FastAPI:
    config: Config = create_config()
    app: FastAPI = FastAPI(
        title=config.app.title,
        debug=config.app.debug,
        lifespan=lifespan,
    )

    container: AsyncContainer = create_container(config)
    setup_dishka(container, app)

    setup_routers(app)
    setup_middlewares(app, config)

    return app
