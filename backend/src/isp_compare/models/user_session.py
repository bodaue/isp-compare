from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from isp_compare.models.base import Base, CreatedDateMixin, IdMixin


class UserSession(IdMixin, CreatedDateMixin, Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[str] = mapped_column(String(255), unique=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_clicks: Mapped[int] = mapped_column(default=0)
    click_path: Mapped[list] = mapped_column(JSON)
    user_path: Mapped[list] = mapped_column(JSON)
    goal_reached: Mapped[bool] = mapped_column(default=False)
    session_duration: Mapped[int | None]
