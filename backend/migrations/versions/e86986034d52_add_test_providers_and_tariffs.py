"""Add test providers and tariffs

Revision ID: e86986034d52
Revises: a33c9b969062
Create Date: 2025-05-09 18:10:19.398725

"""

from collections.abc import Sequence
from decimal import Decimal
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e86986034d52"
down_revision: str | None = "a33c9b969062"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # Создаем идентификаторы для провайдеров
    rostelecom_id = uuid4()
    domru_id = uuid4()
    beeline_id = uuid4()
    mts_id = uuid4()

    # Добавляем провайдеров
    providers_table = sa.table(
        "providers",
        sa.column("id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("website", sa.String),
        sa.column("logo_url", sa.String),
        sa.column("rating", sa.Float),
    )

    op.bulk_insert(
        providers_table,
        [
            {
                "id": rostelecom_id,
                "name": "Ростелеком",
                "description": "Крупнейший российский провайдер "
                "цифровых услуг и решений",
                "website": "https://www.rostelecom.ru",
                "logo_url": "https://www.rostelecom.ru/images/logo.png",
                "rating": 4.2,
            },
            {
                "id": domru_id,
                "name": "Дом.ру",
                "description": "Федеральный провайдер телекоммуникационных услуг",
                "website": "https://www.domru.ru",
                "logo_url": "https://www.domru.ru/images/logo.png",
                "rating": 4.3,
            },
            {
                "id": beeline_id,
                "name": "Билайн",
                "description": "Телекоммуникационная компания, "
                "предоставляющая услуги интернета",
                "website": "https://www.beeline.ru",
                "logo_url": "https://www.beeline.ru/images/logo.png",
                "rating": 4.0,
            },
            {
                "id": mts_id,
                "name": "МТС",
                "description": "Российская телекоммуникационная компания",
                "website": "https://www.mts.ru",
                "logo_url": "https://www.mts.ru/images/logo.png",
                "rating": 4.1,
            },
        ],
    )

    # Добавляем тарифы
    tariffs_table = sa.table(
        "tariffs",
        sa.column("id", sa.Uuid),
        sa.column("provider_id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("price", sa.Numeric),
        sa.column("speed", sa.Integer),
        sa.column("has_tv", sa.Boolean),
        sa.column("has_phone", sa.Boolean),
        sa.column("connection_cost", sa.Numeric),
        sa.column("promo_price", sa.Numeric),
        sa.column("promo_period", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        tariffs_table,
        [
            # Тарифы Ростелеком
            {
                "id": uuid4(),
                "provider_id": rostelecom_id,
                "name": "Игровой 100",
                "description": "Оптимальный тариф для онлайн-игр",
                "price": Decimal("890"),
                "speed": 100,
                "has_tv": False,
                "has_phone": False,
                "connection_cost": Decimal("0"),
                "promo_price": Decimal("590"),
                "promo_period": 3,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": rostelecom_id,
                "name": "Технологичный 300",
                "description": "Высокоскоростной интернет для всей семьи",
                "price": Decimal("1590"),
                "speed": 300,
                "has_tv": True,
                "has_phone": False,
                "connection_cost": Decimal("0"),
                "promo_price": Decimal("990"),
                "promo_period": 6,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": rostelecom_id,
                "name": "Максимальный 500",
                "description": "Максимальная скорость с ТВ и телефонией",
                "price": Decimal("2490"),
                "speed": 500,
                "has_tv": True,
                "has_phone": True,
                "connection_cost": Decimal("0"),
                "promo_price": None,
                "promo_period": None,
                "is_active": True,
            },
            # Тарифы Дом.ру
            {
                "id": uuid4(),
                "provider_id": domru_id,
                "name": "Базовый 50",
                "description": "Доступный интернет для повседневных задач",
                "price": Decimal("690"),
                "speed": 50,
                "has_tv": False,
                "has_phone": False,
                "connection_cost": Decimal("500"),
                "promo_price": Decimal("490"),
                "promo_period": 2,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": domru_id,
                "name": "Домашний 100",
                "description": "Интернет и 150 ТВ-каналов",
                "price": Decimal("990"),
                "speed": 100,
                "has_tv": True,
                "has_phone": False,
                "connection_cost": Decimal("0"),
                "promo_price": None,
                "promo_period": None,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": domru_id,
                "name": "Премиум 500",
                "description": "Максимальная скорость и полный пакет услуг",
                "price": Decimal("1990"),
                "speed": 500,
                "has_tv": True,
                "has_phone": True,
                "connection_cost": Decimal("0"),
                "promo_price": Decimal("1490"),
                "promo_period": 3,
                "is_active": True,
            },
            # Тарифы Билайн
            {
                "id": uuid4(),
                "provider_id": beeline_id,
                "name": "Анлим 100",
                "description": "Безлимитный интернет для дома",
                "price": Decimal("790"),
                "speed": 100,
                "has_tv": False,
                "has_phone": False,
                "connection_cost": Decimal("1000"),
                "promo_price": Decimal("590"),
                "promo_period": 2,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": beeline_id,
                "name": "Фантастический Макс",
                "description": "Интернет 200 Мбит/с + ТВ",
                "price": Decimal("1090"),
                "speed": 200,
                "has_tv": True,
                "has_phone": False,
                "connection_cost": Decimal("0"),
                "promo_price": None,
                "promo_period": None,
                "is_active": True,
            },
            # Тарифы МТС
            {
                "id": uuid4(),
                "provider_id": mts_id,
                "name": "Тариф Красный",
                "description": "Популярный тариф для дома",
                "price": Decimal("890"),
                "speed": 100,
                "has_tv": False,
                "has_phone": False,
                "connection_cost": Decimal("0"),
                "promo_price": Decimal("590"),
                "promo_period": 3,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": mts_id,
                "name": "Тариф Черный",
                "description": "Премиальный тариф с максимальными возможностями",
                "price": Decimal("1590"),
                "speed": 300,
                "has_tv": True,
                "has_phone": True,
                "connection_cost": Decimal("0"),
                "promo_price": Decimal("990"),
                "promo_period": 6,
                "is_active": True,
            },
            {
                "id": uuid4(),
                "provider_id": mts_id,
                "name": "Спутниковый",
                "description": "Интернет через спутник для частного дома",
                "price": Decimal("3990"),
                "speed": 50,
                "has_tv": True,
                "has_phone": False,
                "connection_cost": Decimal("15000"),
                "promo_price": None,
                "promo_period": None,
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем все тарифы
    op.execute(
        "DELETE FROM tariffs WHERE provider_id IN "
        "(SELECT id FROM providers WHERE name IN ('Ростелеком', "
        "'Дом.ру', 'Билайн', 'МТС'))"
    )

    # Удаляем провайдеров
    op.execute(
        "DELETE FROM providers WHERE name IN ('Ростелеком', 'Дом.ру', 'Билайн', 'МТС')"
    )
