from fastapi import FastAPI
from sqladmin import Admin

from isp_compare.admin.auth import AdminAuth
from isp_compare.admin.views import ProviderAdmin, ReviewAdmin, TariffAdmin, UserAdmin
from isp_compare.core.config import Config
from isp_compare.core.di.providers.database import DatabaseProvider
from isp_compare.services.password_hasher import PasswordHasher


def setup_admin(app: FastAPI, config: Config) -> None:
    db_provider = DatabaseProvider()
    engine = db_provider.engine(config.postgres)
    session_maker = db_provider.session_maker(engine)

    password_hasher = PasswordHasher()

    # Create auth backend
    auth_backend = AdminAuth(
        secret_key=config.jwt.secret_key.get_secret_value(),
        session_maker=session_maker,
        jwt_config=config.jwt,
        password_hasher=password_hasher,
    )

    admin = Admin(
        app,
        engine,
        title="ISP Compare Admin",
        authentication_backend=auth_backend,
        base_url="/admin",
    )

    admin.add_view(ProviderAdmin)
    admin.add_view(TariffAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(ReviewAdmin)
