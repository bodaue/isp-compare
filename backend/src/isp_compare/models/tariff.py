import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isp_compare.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from isp_compare.models.provider import Provider


class ConnectionType(enum.Enum):
    FTTH = "FTTH"
    ADSL = "ADSL"
    PON = "PON"
    ETHERNET = "ETHERNET"
    WIMAX = "WIMAX"
    LTE = "LTE"


class Tariff(IdMixin, TimestampMixin, Base):
    __tablename__ = "tariffs"

    provider_id: Mapped[UUID] = mapped_column(ForeignKey("providers.id"))
    provider: Mapped["Provider"] = relationship(back_populates="tariffs")

    name: Mapped[str] = mapped_column(String(255))

    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    speed: Mapped[int] = mapped_column(Integer)  # Мбит/с
    connection_type: Mapped[ConnectionType] = mapped_column(Enum(ConnectionType))

    has_tv: Mapped[bool] = mapped_column(Boolean, default=False)
    has_phone: Mapped[bool] = mapped_column(Boolean, default=False)
    additional_services: Mapped[dict | None] = mapped_column(JSON)

    connection_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    contract_period: Mapped[int | None] = mapped_column(Integer)  # в месяцах

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
