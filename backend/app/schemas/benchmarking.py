from typing import List, Optional
from pydantic import BaseModel


class PeerProjectComparison(BaseModel):
    project_id: str
    project_code: str
    project_name: str
    sector: str
    region: str
    approved_budget: float
    actual_expenditure: float
    physical_progress: float
    financial_progress: float
    risk_score: float
    risk_level: str
    predicted_delay_days: int
    similarity_score: float  # 0.0 to 1.0


class BenchmarkingResponse(BaseModel):
    target_project: PeerProjectComparison
    cohort_count: int
    cohort_avg_budget: float
    cohort_avg_progress: float
    cohort_avg_risk_score: float
    cohort_avg_delay_days: float
    cohort_cost_overrun_rate: float
    similar_projects: List[PeerProjectComparison]
