from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MilestoneBase(BaseModel):
    milestone_name: str
    planned_date: date
    actual_date: Optional[date] = None
    status: str = Field(default="PENDING")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    order_index: int = Field(default=0)


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneResponse(MilestoneBase):
    id: str
    project_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
