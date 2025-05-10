"""Add test tariffs

Revision ID: e3f38065dede
Revises: 67780e890d7c
Create Date: 2025-05-10 12:26:03.474343

"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e3f38065dede"
down_revision: str | None = "67780e890d7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Получаем ID существующих провайдеров
    connection = op.get_bind()
    providers_result = connection.execute(
        sa.text("SELECT id, name FROM providers")
    ).fetchall()

    # Создаем словарь для удобного доступа к ID провайдеров
    provider_ids = {row[1]: row[0] for row in providers_result}

    tariffs_table = sa.table(
        "tariffs",
        sa.column("id", sa.Uuid),
        sa.column("provider_id", sa.Uuid),
        sa.column("name", sa.String(255)),
        sa.column("description", sa.Text),
        sa.column("price", sa.Numeric(10, 2)),
        sa.column("speed", sa.Integer),
        sa.column("has_tv", sa.Boolean),
        sa.column("has_phone", sa.Boolean),
        sa.column("connection_cost", sa.Numeric(10, 2)),
        sa.column("promo_price", sa.Numeric(10, 2)),
        sa.column("promo_period", sa.Integer),
        sa.column("is_active", sa.Boolean),
        sa.column("url", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    # Тарифы для Ростелеком
    rostelecom_tariffs = [
        {
            "id": uuid4(),
            "provider_id": provider_ids["Ростелеком"],
            "name": "Интернет 100",
            "description": "Базовый тариф для домашнего интернета",
            "price": 550,
            "speed": 100,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": None,
            "promo_period": None,
            "is_active": True,
            "url": "https://volgograd.rt.ru/internet/tariffs",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Ростелеком"],
            "name": "Интернет + ТВ 200",
            "description": "Интернет и цифровое телевидение",
            "price": 990,
            "speed": 200,
            "has_tv": True,
            "has_phone": False,
            "connection_cost": 199,
            "promo_price": 790,
            "promo_period": 3,
            "is_active": True,
            "url": "https://volgograd.rt.ru/packages",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Ростелеком"],
            "name": "Максимальный 500",
            "description": "Максимальная скорость и полный пакет услуг",
            "price": 1990,
            "speed": 500,
            "has_tv": True,
            "has_phone": True,
            "connection_cost": 0,
            "promo_price": 1490,
            "promo_period": 6,
            "is_active": True,
            "url": "https://volgograd.rt.ru/internet/maximum",
        },
    ]

    # Тарифы для Дом.ru
    dom_ru_tariffs = [
        {
            "id": uuid4(),
            "provider_id": provider_ids["Дом.ru"],
            "name": "Стартовый",
            "description": "Оптимальный тариф для интернет-серфинга",
            "price": 499,
            "speed": 60,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 300,
            "promo_price": 299,
            "promo_period": 2,
            "is_active": True,
            "url": "https://volgograd.dom.ru/internet/tariff-starter",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Дом.ru"],
            "name": "Игровой",
            "description": "Высокая скорость для онлайн-игр",
            "price": 799,
            "speed": 300,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": None,
            "promo_period": None,
            "is_active": True,
            "url": "https://volgograd.dom.ru/internet/gaming",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Дом.ru"],
            "name": "Всё включено",
            "description": "Интернет, ТВ и телефония",
            "price": 1299,
            "speed": 300,
            "has_tv": True,
            "has_phone": True,
            "connection_cost": 0,
            "promo_price": 999,
            "promo_period": 3,
            "is_active": True,
            "url": "https://volgograd.dom.ru/pakety",
        },
    ]

    # Тарифы для МегаФон
    megafon_tariffs = [
        {
            "id": uuid4(),
            "provider_id": provider_ids["МегаФон"],
            "name": "МегаФон Интернет M",
            "description": "Базовый тариф для дома",
            "price": 599,
            "speed": 100,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 500,
            "promo_price": 399,
            "promo_period": 2,
            "is_active": True,
            "url": "https://volgograd.megafon.ru/internet/dom",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["МегаФон"],
            "name": "МегаФон Интернет L",
            "description": "Быстрый интернет для всей семьи",
            "price": 899,
            "speed": 300,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": None,
            "promo_period": None,
            "is_active": True,
            "url": "https://volgograd.megafon.ru/internet/l",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["МегаФон"],
            "name": "МегаФон Объединяй",
            "description": "Интернет и ТВ в одном пакете",
            "price": 1390,
            "speed": 500,
            "has_tv": True,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": 990,
            "promo_period": 6,
            "is_active": True,
            "url": "https://volgograd.megafon.ru/obiedinya",
        },
    ]

    # Тарифы для МТС
    mts_tariffs = [
        {
            "id": uuid4(),
            "provider_id": provider_ids["МТС"],
            "name": "Интернет для дома 100",
            "description": "Надёжный интернет на умеренной скорости",
            "price": 490,
            "speed": 100,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 299,
            "promo_price": None,
            "promo_period": None,
            "is_active": True,
            "url": "https://volgograd.mts.ru/personal/mobilnaya-svyaz/dom/domashnie-internet-tv",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["МТС"],
            "name": "Спутник ТВ + Интернет",
            "description": "Интернет и спутниковое ТВ",
            "price": 1090,
            "speed": 200,
            "has_tv": True,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": 790,
            "promo_period": 3,
            "is_active": True,
            "url": "https://volgograd.mts.ru/personal/tv-internet-dom",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["МТС"],
            "name": "Тариф №1",
            "description": "Максимальная скорость и все сервисы",
            "price": 1890,
            "speed": 600,
            "has_tv": True,
            "has_phone": True,
            "connection_cost": 0,
            "promo_price": 1290,
            "promo_period": 4,
            "is_active": True,
            "url": "https://volgograd.mts.ru/personal/tarif-1",
        },
    ]

    # Тарифы для Билайн
    beeline_tariffs = [
        {
            "id": uuid4(),
            "provider_id": provider_ids["Билайн"],
            "name": "Интернет Старт",
            "description": "Простой тариф для базовых потребностей",
            "price": 449,
            "speed": 70,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": 299,
            "promo_period": 2,
            "is_active": True,
            "url": "https://volgograd.beeline.ru/customers/products/home/internet/start",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Билайн"],
            "name": "Интернет Хайт",
            "description": "Высокая скорость для работы и развлечений",
            "price": 699,
            "speed": 200,
            "has_tv": False,
            "has_phone": False,
            "connection_cost": 0,
            "promo_price": None,
            "promo_period": None,
            "is_active": True,
            "url": "https://volgograd.beeline.ru/customers/products/home/high",
        },
        {
            "id": uuid4(),
            "provider_id": provider_ids["Билайн"],
            "name": "ВСЁмоё 3 в 1",
            "description": "Интернет, ТВ и домашний телефон",
            "price": 1499,
            "speed": 300,
            "has_tv": True,
            "has_phone": True,
            "connection_cost": 0,
            "promo_price": 999,
            "promo_period": 6,
            "is_active": True,
            "url": "https://volgograd.beeline.ru/customers/products/vse-moe",
        },
    ]

    # Объединяем все тарифы
    all_tariffs = (
        rostelecom_tariffs
        + dom_ru_tariffs
        + megafon_tariffs
        + mts_tariffs
        + beeline_tariffs
    )

    # Вставляем тарифы в таблицу
    op.bulk_insert(tariffs_table, all_tariffs)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем все добавленные тарифы
    op.execute(
        """
        DELETE
        FROM tariffs
        WHERE name IN (
                       'Интернет 100',
                       'Интернет + ТВ 200',
                       'Максимальный 500',
                       'Стартовый',
                       'Игровой',
                       'Всё включено',
                       'МегаФон Интернет M',
                       'МегаФон Интернет L',
                       'МегаФон Объединяй',
                       'Интернет для дома 100',
                       'Спутник ТВ + Интернет',
                       'Тариф №1',
                       'Интернет Старт',
                       'Интернет Хайт',
                       'ВСЁмоё 3 в 1'
            )
        """
    )
