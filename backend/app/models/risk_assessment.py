from datetime import datetime
from typing import Optional, Any
import uuid
import json
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    assessment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )

    cost_overrun_probability: Mapped[float] = mapped_column(Float, default=0.0)
    delay_probability: Mapped[float] = mapped_column(Float, default=0.0)
    expected_final_cost: Mapped[float] = mapped_column(Float, default=0.0)
    predicted_delay_days: Mapped[int] = mapped_column(Integer, default=0)

    risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    # LOW, MODERATE, HIGH, CRITICAL
    risk_level: Mapped[str] = mapped_column(String(16), default="LOW", index=True)

    model_version: Mapped[str] = mapped_column(String(64), default="fallback-v1")
    is_fallback: Mapped[bool] = mapped_column(default=False)

    explanation_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="risk_assessments")

    @property
    def explanation(self) -> dict:
        if self.explanation_raw:
            try:
                return json.loads(self.explanation_raw)
            except Exception:
                return {}
        return {}

    @explanation.setter
    def explanation(self, value: Any):
        if isinstance(value, (dict, list)):
            self.explanation_raw = json.dumps(value)
        elif isinstance(value, str):
            self.explanation_raw = value
        else:
            self.explanation_raw = None
