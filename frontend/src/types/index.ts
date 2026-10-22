export interface Project {
  id: string;
  project_code: string;
  project_name: string;
  sector: string;
  department: string;
  region: string;
  implementing_agency: string;
  approved_budget: number;
  revised_budget?: number | null;
  actual_expenditure: number;
  current_physical_progress: number;
  current_financial_progress: number;
  planned_start_date: string;
  expected_completion_date: string;
  project_status: string;
  current_risk_score: number;
  current_risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  predicted_delay_days: number;
  forecast_final_cost: number;
  latest_alert?: string | null;
}

export interface ProgressUpdate {
  id: string;
  project_id: string;
  reporting_date: string;
  planned_progress: number;
  actual_progress: number;
  cumulative_expenditure: number;
  reported_issues?: string | null;
  data_source: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  milestone_name: string;
  planned_date: string;
  actual_date?: string | null;
  status: 'PENDING' | 'ON_TRACK' | 'DELAYED' | 'COMPLETED' | 'MISSED';
  completion_percentage: number;
  order_index: number;
}

export interface Alert {
  id: string;
  project_id: string;
  project_code?: string;
  project_name?: string;
  sector?: string;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  description: string;
  evidence?: Record<string, any>;
  recommended_action: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  created_at: string;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  resolution_notes?: string | null;
}

export interface RiskFactor {
  factor: string;
  description: string;
  impact: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface RiskDetail {
  project_id: string;
  project_code: string;
  project_name: string;
  approved_budget: number;
  actual_expenditure: number;
  forecast_final_cost: number;
  forecast_cost_variance: number;
  predicted_delay_days: number;
  cost_overrun_probability: number;
  delay_probability: number;
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  model_version: string;
  is_fallback: boolean;
  explanation: {
    top_factors: RiskFactor[];
    recommended_actions: string[];
    metrics: Record<string, any>;
  };
}

export interface SectorMetric {
  sector: string;
  count: number;
  approved_budget: number;
  actual_expenditure: number;
  avg_physical_progress: number;
  avg_risk_score: number;
  high_risk_count: number;
}

export interface RegionMetric {
  region: string;
  count: number;
  approved_budget: number;
  actual_expenditure: number;
  avg_risk_score: number;
}

export interface MonthlyTrend {
  month: string;
  planned_progress: number;
  actual_progress: number;
  expenditure: number;
}

export interface DashboardSummary {
  total_projects: number;
  high_critical_risk_projects: number;
  predicted_cost_overrun_projects: number;
  predicted_delay_projects: number;
  total_approved_budget: number;
  total_revised_budget: number;
  total_actual_expenditure: number;
  total_forecast_final_cost: number;
  net_cost_variance: number;
  average_physical_progress: number;
  average_financial_progress: number;
  risk_distribution: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  sector_breakdown: SectorMetric[];
  region_breakdown: RegionMetric[];
  recent_alerts: Alert[];
  monthly_trends: MonthlyTrend[];
}

export interface PeerProject {
  project_id: string;
  project_code: string;
  project_name: string;
  sector: string;
  region: string;
  approved_budget: number;
  actual_expenditure: number;
  physical_progress: number;
  financial_progress: number;
  risk_score: number;
  risk_level: string;
  predicted_delay_days: number;
  similarity_score: number;
}

export interface BenchmarkingData {
  target_project: PeerProject;
  cohort_count: number;
  cohort_avg_budget: number;
  cohort_avg_progress: number;
  cohort_avg_risk_score: number;
  cohort_avg_delay_days: number;
  cohort_cost_overrun_rate: number;
  similar_projects: PeerProject[];
}

export interface ChatReferencedProject {
  project_id: string;
  project_code: string;
  project_name: string;
  sector: string;
  risk_score: number;
  risk_level: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tools_used: string[];
  referenced_projects: ChatReferencedProject[];
  suggested_followups: string[];
}
