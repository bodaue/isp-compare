from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isp_compare.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from isp_compare.models.provider import Provider


class Tariff(IdMixin, TimestampMixin, Base):
    __tablename__ = "tariffs"

    provider_id: Mapped[UUID] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE")
    )
    provider: Mapped["Provider"] = relationship(back_populates="tariffs")

    name: Mapped[str] = mapped_column(String(255))

    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    speed: Mapped[int]  # Мбит/с

    has_tv: Mapped[bool] = mapped_column(default=False)
    has_phone: Mapped[bool] = mapped_column(default=False)

    connection_cost: Mapped[float | None] = mapped_column(Numeric(10, 2))

    promo_price: Mapped[float | None] = mapped_column(Numeric(10, 2))  # Цена по акции
    promo_period: Mapped[int | None]  # Срок акции в месяцах

    is_active: Mapped[bool] = mapped_column(default=True)
    url: Mapped[str | None]
