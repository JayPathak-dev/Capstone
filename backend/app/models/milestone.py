from datetime import datetime, date
from typing import Optional
import uuid
from sqlalchemy import String, Float, Date, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    milestone_name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status: PENDING, ON_TRACK, DELAYED, COMPLETED, MISSED
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="milestones")
