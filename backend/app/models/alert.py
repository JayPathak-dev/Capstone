from datetime import datetime
from typing import Optional, Any
import uuid
import json
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # COST_ESCALATION, SCHEDULE_SLIPPAGE, PROGRESS_STAGNATION, MILESTONE_BREACH, VELOCITY_DISCREPANCY
    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    # LOW, MEDIUM, HIGH, CRITICAL
    severity: Mapped[str] = mapped_column(String(16), index=True, default="MEDIUM")

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)

    # NEW, ACKNOWLEDGED, RESOLVED, DISMISSED
    status: Mapped[str] = mapped_column(String(32), default="NEW", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), index=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="alerts")

    @property
    def evidence(self) -> dict:
        if self.evidence_raw:
            try:
                return json.loads(self.evidence_raw)
            except Exception:
                return {}
        return {}

    @evidence.setter
    def evidence(self, value: Any):
        if isinstance(value, (dict, list)):
            self.evidence_raw = json.dumps(value)
        elif isinstance(value, str):
            self.evidence_raw = value
        else:
            self.evidence_raw = None
