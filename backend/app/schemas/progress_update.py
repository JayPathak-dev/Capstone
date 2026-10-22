from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProgressUpdateBase(BaseModel):
    reporting_date: date
    planned_progress: float = Field(..., ge=0.0, le=100.0)
    actual_progress: float = Field(..., ge=0.0, le=100.0)
    cumulative_expenditure: float = Field(..., ge=0.0)
    reported_issues: Optional[str] = None
    data_source: Optional[str] = "PAIMANA_PORTAL"


class ProgressUpdateCreate(ProgressUpdateBase):
    pass


class ProgressUpdateResponse(ProgressUpdateBase):
    id: str
    project_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
