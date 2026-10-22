from datetime import datetime, date
from typing import Optional
import uuid
from sqlalchemy import String, Float, Date, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reporting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    planned_progress: Mapped[float] = mapped_column(Float, nullable=False)
    actual_progress: Mapped[float] = mapped_column(Float, nullable=False)
    cumulative_expenditure: Mapped[float] = mapped_column(Float, nullable=False)
    reported_issues: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), default="PAIMANA_PORTAL")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="progress_updates")
