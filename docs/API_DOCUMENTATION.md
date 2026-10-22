# PAIMANA REST API Documentation

Base URL: `/api/v1`
Interactive Swagger Docs: `http://localhost:8000/docs`
ReDoc Specification: `http://localhost:8000/redoc`

---

## 1. System & Health Endpoints

### `GET /health`
Returns system status, database connectivity, and ML engine status.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected",
  "ml_engine": "loaded",
  "model_version": "gbdt-risk-v1.0"
}
```

---

## 2. Dashboard & Analytics Endpoints

### `GET /dashboard/summary`
Returns high-level portfolio KPIs, budget utilization, risk distribution, and urgent alerts.
- **Query Parameters**:
  - `sector` (optional string): Filter by sector
  - `region` (optional string): Filter by region
- **Response `200 OK`**:
```json
{
  "total_projects": 48,
  "high_critical_risk_projects": 11,
  "predicted_cost_overrun_projects": 14,
  "predicted_delay_projects": 18,
  "total_approved_budget": 128450.00,
  "total_actual_expenditure": 68320.50,
  "total_forecast_final_cost": 149800.20,
  "average_physical_progress": 54.3,
  "risk_distribution": {
    "low": 19,
    "moderate": 18,
    "high": 8,
    "critical": 3
  },
  "sector_breakdown": [
    {
      "sector": "Roads & Highways",
      "count": 16,
      "approved_budget": 45000.0,
      "expenditure": 27000.0,
      "avg_risk_score": 42.1
    }
  ]
}
```

---

## 3. Project Management Endpoints

### `GET /projects`
Retrieve paginated, searchable, and filtered project records.
- **Query Parameters**:
  - `search` (string): Fuzzy match on code or name
  - `sector` (string): Filter by sector
  - `region` (string): Filter by region
  - `risk_level` (string): Filter by `LOW`, `MODERATE`, `HIGH`, `CRITICAL`
  - `status` (string): Filter by `IN_PROGRESS`, `DELAYED`, `COMPLETED`, `STALLED`
  - `skip` (int, default 0)
  - `limit` (int, default 20)
  - `sort_by` (string, default `risk_score`)
  - `sort_order` (string: `asc` or `desc`)

### `GET /projects/{project_id}`
Detailed project dossier including budget revisions, timelines, latest risk assessment, and active alerts.

### `POST /projects`
Create a new infrastructure project sanction.

### `PATCH /projects/{project_id}`
Update project details, physical progress, or revised budget.

### `GET /projects/{project_id}/timeline`
Monthly time-series progress updates and milestone execution history.

---

## 4. Risk Prediction & Explainability Endpoints

### `GET /projects/{project_id}/risk`
Retrieve current ML risk evaluation, delay prediction, forecast cost, and SHAP feature drivers.
- **Response `200 OK`**:
```json
{
  "project_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "project_code": "NHAI-2024-EXP-08",
  "risk_score": 78.4,
  "risk_level": "CRITICAL",
  "cost_overrun_probability": 0.84,
  "delay_probability": 0.91,
  "expected_final_cost": 5420.00,
  "approved_budget": 4200.00,
  "forecast_cost_variance": 1220.00,
  "predicted_delay_days": 184,
  "model_version": "gbdt-risk-v1.0",
  "is_fallback": false,
  "explanation": {
    "top_factors": [
      {
        "factor": "Physical-Financial Divergence",
        "description": "Financial burn is 76% of budget while physical progress is only 42%",
        "impact": "+24.5 risk points"
      },
      {
        "factor": "Critical Milestone Slippage",
        "description": "3 consecutive bridge foundation milestones are overdue by >90 days",
        "impact": "+18.2 risk points"
      }
    ],
    "recommended_actions": [
      "Convene joint review with National Highways Authority contractor",
      "Expedite Right of Way (RoW) clearance for Km 140-185 package",
      "Withhold mobilization advance until physical milestone 4 verification"
    ]
  }
}
```

### `POST /projects/{project_id}/predict`
Trigger an on-demand real-time re-evaluation of project risk using the latest monitoring data.

---

## 5. Early Warnings & Alerts Endpoints

### `GET /alerts`
List triggered early warnings with filtering by `severity`, `status`, and `project_id`.

### `PATCH /alerts/{alert_id}`
Acknowledge or resolve an early warning alert with notes.
- **Request Body**:
```json
{
  "status": "ACKNOWLEDGED",
  "resolution_notes": "Project Director notified; site inspection scheduled for Monday."
}
```

---

## 6. Peer Benchmarking Endpoints

### `GET /benchmarking`
Compare a target project against peer cohort in same sector, budget tier, and terrain region.
- **Query Parameters**:
  - `project_id` (required string): Target project ID
  - `cohort_size` (int, default 5): Number of closest peer projects to benchmark

---

## 7. AI Assistant Endpoint

### `POST /assistant/chat`
Ask natural-language questions to the grounded project intelligence assistant.
- **Request Body**:
```json
{
  "message": "Which 3 highway projects have the highest predicted delay and why?",
  "conversation_id": "optional-uuid"
}
```
- **Response `200 OK`**:
```json
{
  "response": "Based on verified PAIMANA monitoring records, the 3 highest risk highway projects are...",
  "tools_used": ["list_high_risk_projects", "summarize_risk_factors"],
  "referenced_projects": [
    {"project_code": "NHAI-2024-EXP-08", "name": "Delhi-Dehradun Expressway Package 2", "risk_score": 78.4}
  ]
}
```

---

## 8. Data Ingestion Endpoints

### `POST /data/import/preview`
Upload CSV file for dry-run validation, column mapping check, and anomaly preview.

### `POST /data/import/commit`
Commit validated records to the database with transaction isolation.
