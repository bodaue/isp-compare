from typing import TYPE_CHECKING

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from isp_compare.admin.auth import AdminAuth
from isp_compare.admin.views import (
    ProviderAdmin,
    ReviewAdmin,
    TariffAdmin,
    UserAdmin,
    UserAnalyticsAdmin,
)
from isp_compare.core.config import JWTConfig

if TYPE_CHECKING:
    from dishka import AsyncContainer


async def setup_admin(app: FastAPI) -> None:
    container: AsyncContainer = app.state.dishka_container

    session_maker: async_sessionmaker[AsyncSession] = await container.get(
        async_sessionmaker[AsyncSession]
    )
    jwt_config: JWTConfig = await container.get(JWTConfig)

    auth_backend = AdminAuth(
        secret_key=jwt_config.secret_key.get_secret_value(),
        jwt_config=jwt_config,
    )

    admin = Admin(
        app,
        session_maker=session_maker,
        title="ISP Compare Admin",
        authentication_backend=auth_backend,
        base_url="/admin",
    )

    admin.add_view(ProviderAdmin)
    admin.add_view(TariffAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(UserAnalyticsAdmin)
