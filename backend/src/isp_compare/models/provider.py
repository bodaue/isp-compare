from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isp_compare.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from isp_compare.models.review import Review
    from isp_compare.models.tariff import Tariff


class Provider(IdMixin, TimestampMixin, Base):
    __tablename__ = "providers"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str]
    phone: Mapped[str]
    logo_url: Mapped[str | None]
    rating: Mapped[float | None]

    tariffs: Mapped[list["Tariff"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan"
    )
