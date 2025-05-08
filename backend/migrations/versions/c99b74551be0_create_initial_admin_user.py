"""Create initial admin user

Revision ID: c99b74551be0
Revises: ac24564c3154
Create Date: 2025-05-08 15:53:04.275118

"""

import os
from collections.abc import Sequence
from uuid import uuid4

import bcrypt
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c99b74551be0"
down_revision: str | None = "ac24564c3154"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid),
        sa.column("fullname", sa.String),
        sa.column("username", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("email", sa.String),
        sa.column("is_admin", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    admin_username = "admin"
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD", "AdminPassword123")
    admin_email = "admin@isp-compare.ru"
    admin_fullname = "Системный администратор"

    hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()

    op.bulk_insert(
        users_table,
        [
            {
                "id": uuid4(),
                "fullname": admin_fullname,
                "username": admin_username,
                "hashed_password": hashed_password,
                "email": admin_email,
                "is_admin": True,
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM users WHERE username = 'admin' AND email = 'admin@isp-compare.ru'"
    )
