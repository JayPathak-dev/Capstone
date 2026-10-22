from datetime import datetime, date
from typing import Optional, List
import uuid
from sqlalchemy import String, Float, Date, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(128), nullable=False)
    region: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    implementing_agency: Mapped[str] = mapped_column(String(128), nullable=False)

    approved_budget: Mapped[float] = mapped_column(Float, nullable=False)
    revised_budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_expenditure: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    current_physical_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_financial_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Status: SANCTIONED, IN_PROGRESS, DELAYED, STALLED, COMPLETED
    project_status: Mapped[str] = mapped_column(String(32), default="IN_PROGRESS", index=True)

    # Current risk metrics cache for fast querying
    current_risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    current_risk_level: Mapped[str] = mapped_column(String(16), default="LOW", index=True)
    predicted_delay_days: Mapped[int] = mapped_column(Float, default=0)
    forecast_final_cost: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
    )

    # Relationships
    progress_updates: Mapped[List["ProgressUpdate"]] = relationship(
        "ProgressUpdate", back_populates="project", cascade="all, delete-orphan", order_by="ProgressUpdate.reporting_date"
    )
    milestones: Mapped[List["Milestone"]] = relationship(
        "Milestone", back_populates="project", cascade="all, delete-orphan", order_by="Milestone.order_index"
    )
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(
        "RiskAssessment", back_populates="project", cascade="all, delete-orphan", order_by="desc(RiskAssessment.assessment_date)"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="project", cascade="all, delete-orphan", order_by="desc(Alert.created_at)"
    )
