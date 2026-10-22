from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RiskFactor(BaseModel):
    factor: str
    description: str
    impact: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL


class RiskExplanation(BaseModel):
    top_factors: List[RiskFactor] = []
    recommended_actions: List[str] = []
    metrics: Dict[str, Any] = {}


class RiskAssessmentResponse(BaseModel):
    id: str
    project_id: str
    assessment_date: datetime
    cost_overrun_probability: float
    delay_probability: float
    expected_final_cost: float
    predicted_delay_days: int
    risk_score: float
    risk_level: str
    model_version: str
    is_fallback: bool
    explanation: Optional[RiskExplanation] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectRiskDetailResponse(BaseModel):
    project_id: str
    project_code: str
    project_name: str
    approved_budget: float
    actual_expenditure: float
    forecast_final_cost: float
    forecast_cost_variance: float
    predicted_delay_days: int
    cost_overrun_probability: float
    delay_probability: float
    risk_score: float
    risk_level: str
    model_version: str
    is_fallback: bool
    explanation: RiskExplanation
