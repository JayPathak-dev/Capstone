from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.progress_update import ProgressUpdateResponse
from backend.app.schemas.milestone import MilestoneResponse
from backend.app.schemas.alert import AlertResponse


class ProjectBase(BaseModel):
    project_code: str
    project_name: str
    sector: str
    department: str
    region: str
    implementing_agency: str
    approved_budget: float = Field(..., gt=0.0)
    revised_budget: Optional[float] = None
    planned_start_date: date
    expected_completion_date: date
    actual_completion_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    actual_expenditure: float = 0.0
    current_physical_progress: float = 0.0
    current_financial_progress: float = 0.0
    project_status: str = "IN_PROGRESS"


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    revised_budget: Optional[float] = None
    actual_expenditure: Optional[float] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    current_physical_progress: Optional[float] = None
    current_financial_progress: Optional[float] = None
    project_status: Optional[str] = None


class ProjectListItem(BaseModel):
    id: str
    project_code: str
    project_name: str
    sector: str
    department: str
    region: str
    implementing_agency: str
    approved_budget: float
    revised_budget: Optional[float] = None
    actual_expenditure: float
    current_physical_progress: float
    current_financial_progress: float
    planned_start_date: date
    expected_completion_date: date
    project_status: str
    current_risk_score: float
    current_risk_level: str
    predicted_delay_days: int
    forecast_final_cost: float
    latest_alert: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProjectListItem]


class ProjectDetailResponse(ProjectListItem):
    progress_updates: List[ProgressUpdateResponse] = []
    milestones: List[MilestoneResponse] = []
    alerts: List[AlertResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
