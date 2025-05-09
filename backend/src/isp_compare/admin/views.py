from sqladmin import ModelView

from isp_compare.models.provider import Provider
from isp_compare.models.review import Review
from isp_compare.models.tariff import Tariff
from isp_compare.models.user import User


class ProviderAdmin(ModelView, model=Provider):
    column_list = [
        Provider.id,
        Provider.name,
        Provider.rating,
        Provider.website,
        Provider.created_at,
    ]
    column_searchable_list = [Provider.name]
    column_sortable_list = [Provider.name, Provider.rating, Provider.created_at]
    column_default_sort = ("created_at", True)

    form_columns = [
        Provider.name,
        Provider.description,
        Provider.website,
        Provider.logo_url,
    ]

    name = "Provider"
    name_plural = "Providers"
    icon = "fa-solid fa-building"


class TariffAdmin(ModelView, model=Tariff):
    column_list = [
        Tariff.id,
        Tariff.name,
        Tariff.provider,
        Tariff.price,
        Tariff.promo_price,
        Tariff.promo_period,
        Tariff.speed,
        Tariff.is_active,
    ]
    column_searchable_list = [Tariff.name]
    column_sortable_list = [Tariff.name, Tariff.price, Tariff.speed]
    column_default_sort = ("created_at", True)

    form_columns = [
        Tariff.provider,
        Tariff.name,
        Tariff.description,
        Tariff.price,
        Tariff.promo_price,  # добавить
        Tariff.promo_period,  # добавить
        Tariff.speed,
        Tariff.has_tv,
        Tariff.has_phone,
        Tariff.connection_cost,
        Tariff.is_active,
    ]

    name = "Tariff"
    name_plural = "Tariffs"
    icon = "fa-solid fa-list"


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.fullname,
        User.email,
        User.is_admin,
        User.created_at,
    ]
    column_searchable_list = [User.username, User.email, User.fullname]
    column_sortable_list = [User.username, User.created_at]
    column_default_sort = ("created_at", True)

    form_columns = [
        User.fullname,
        User.username,
        User.email,
        User.is_admin,
    ]

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class ReviewAdmin(ModelView, model=Review):
    column_list = [
        Review.id,
        Review.user,
        Review.provider,
        Review.rating,
        Review.created_at,
    ]
    column_searchable_list = [Review.comment]
    column_sortable_list = [Review.rating, Review.created_at]
    column_default_sort = ("created_at", True)

    form_columns = [
        Review.user,
        Review.provider,
        Review.rating,
        Review.comment,
    ]

    name = "Review"
    name_plural = "Reviews"
    icon = "fa-solid fa-star"
