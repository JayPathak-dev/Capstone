from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.alert import AlertResponse


class RiskDistribution(BaseModel):
    low: int = 0
    moderate: int = 0
    high: int = 0
    critical: int = 0


class SectorMetric(BaseModel):
    sector: str
    count: int
    approved_budget: float
    actual_expenditure: float
    avg_physical_progress: float
    avg_risk_score: float
    high_risk_count: int


class RegionMetric(BaseModel):
    region: str
    count: int
    approved_budget: float
    actual_expenditure: float
    avg_risk_score: float


class MonthlyTrend(BaseModel):
    month: str
    planned_progress: float
    actual_progress: float
    expenditure: float


class DashboardSummaryResponse(BaseModel):
    total_projects: int
    high_critical_risk_projects: int
    predicted_cost_overrun_projects: int
    predicted_delay_projects: int

    total_approved_budget: float
    total_revised_budget: float
    total_actual_expenditure: float
    total_forecast_final_cost: float
    net_cost_variance: float

    average_physical_progress: float
    average_financial_progress: float

    risk_distribution: RiskDistribution
    sector_breakdown: List[SectorMetric]
    region_breakdown: List[RegionMetric]
    recent_alerts: List[AlertResponse]
    monthly_trends: List[MonthlyTrend]
