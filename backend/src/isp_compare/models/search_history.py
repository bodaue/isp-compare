from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from isp_compare.models.base import Base, CreatedDateMixin, IdMixin

if TYPE_CHECKING:
    from isp_compare.models.user import User


class SearchHistory(IdMixin, CreatedDateMixin, Base):
    __tablename__ = "search_history"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship()

    search_params: Mapped[dict] = mapped_column(JSON, nullable=False)
