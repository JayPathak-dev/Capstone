from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    alert_type: str
    severity: str = "MEDIUM"
    title: str
    description: str
    evidence: Optional[Dict[str, Any]] = None
    recommended_action: str
    status: str = "NEW"


class AlertCreate(AlertBase):
    project_id: str


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # ACKNOWLEDGED, RESOLVED, DISMISSED
    resolution_notes: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    project_id: str
    project_code: Optional[str] = None
    project_name: Optional[str] = None
    sector: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    total: int
    items: List[AlertResponse]
