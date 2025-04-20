from sqlalchemy.orm import Mapped, mapped_column

from isp_compare.models.base import Base, IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    fullname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    email: Mapped[str | None] = mapped_column(unique=True)
