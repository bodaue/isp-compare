"""Add initial providers

Revision ID: 5ecf2e568cf7
Revises: 1c046fa5a56c
Create Date: 2025-05-18 21:10:05.803718

"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5ecf2e568cf7"
down_revision: str | None = "1c046fa5a56c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    providers_table = sa.table(
        "providers",
        sa.column("id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("website", sa.String),
        sa.column("phone", sa.String),
        sa.column("logo_url", sa.String),
        sa.column("rating", sa.Float),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    providers_data = [
        {
            "id": uuid4(),
            "name": "Ростелеком",
            "description": "Крупнейший российский провайдер цифровых услуг и решений."
            " Предоставляет услуги интернета, телевидения и телефонии"
            " по всей России.",
            "website": "https://volgograd.rt.ru",
            "phone": "8-800-1000-800",
            "logo_url": "https://upload.wikimedia.org/wikipedia/ru/archive/d/d9/20221223120328%21Логотип_компании_«Ростелеком».png",
            "rating": None,
        },
        {
            "id": uuid4(),
            "name": "Дом.ru",
            "description": "Федеральный телекоммуникационный оператор, предоставляющий"
            " услуги доступа в интернет, цифрового телевидения "
            "и телефонии.",
            "website": "https://volgograd.dom.ru",
            "phone": "7 (8442) 685-281",
            "logo_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQftxDPbtC6FOBBmdIHhhe4zOei4cbCxHXgzQ&s",
            "rating": None,
        },
        {
            "id": uuid4(),
            "name": "МТС",
            "description": "Ведущая российская компания по предоставлению цифровых,"
            " медийных и телекоммуникационных сервисов."
            " Домашний интернет и ТВ.",
            "website": "https://volgograd.mts.ru",
            "phone": "8-800-250-0890",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Logo_МТС_%282023%29.svg/2048px-Logo_МТС_%282023%29.svg.png",
            "rating": None,
        },
        {
            "id": uuid4(),
            "name": "Билайн",
            "description": "Российская телекоммуникационная компания."
            " Предоставляет услуги домашнего интернета,"
            " цифрового телевидения и телефонии.",
            "website": "https://volgograd.beeline.ru",
            "phone": "8 800 600-80-08",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/BeeLine_logo.png",
            "rating": None,
        },
    ]

    op.bulk_insert(providers_table, providers_data)


def downgrade() -> None:
    op.execute(
        """
        DELETE
        FROM providers
        WHERE name IN (
                       'Ростелеком',
                       'Дом.ru',
                       'МТС',
                       'Билайн'
            )
        """
    )
