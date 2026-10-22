import os
import pytest
from datetime import date
from backend.app.ml.fallback import calculate_calibrated_risk
from backend.app.ml.inference import predict_project_risk


def test_calibrated_fallback_bounds():
    """Verify calibrated fallback score is strictly between 0 and 100 with valid probabilities."""
    res = calculate_calibrated_risk(
        approved_budget=2000.0,
        revised_budget=2400.0,
        actual_expenditure=1800.0,
        planned_progress=75.0,
        actual_progress=45.0,
        planned_start_date=date(2022, 1, 1),
        expected_completion_date=date(2025, 1, 1),
        overdue_milestones_count=2,
        max_milestone_delay_days=90,
    )

    assert 0.0 <= res["risk_score"] <= 100.0
    assert 0.0 <= res["cost_overrun_probability"] <= 1.0
    assert 0.0 <= res["delay_probability"] <= 1.0
    assert res["predicted_delay_days"] >= 0
    assert res["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert res["is_fallback"] is True
    assert len(res["explanation"]["top_factors"]) > 0


def test_ml_inference_execution():
    """Verify ML inference using trained pipeline or fallback produces valid schema."""
    p_dict = {
        "approved_budget": 5000.0,
        "revised_budget": 5500.0,
        "actual_expenditure": 3500.0,
        "planned_start_date": date(2022, 1, 1),
        "expected_completion_date": date(2025, 12, 31),
        "sector": "Roads & Highways",
        "region": "Northern",
    }
    res = predict_project_risk(
        project_dict=p_dict,
        planned_progress=60.0,
        actual_progress=52.0,
        overdue_milestones_count=1,
        max_milestone_delay_days=45,
    )

    assert 0.0 <= res["risk_score"] <= 100.0
    assert 0.0 <= res["cost_overrun_probability"] <= 1.0
    assert 0.0 <= res["delay_probability"] <= 1.0
    assert res["expected_final_cost"] > 0
    assert res["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert "explanation" in res
    assert "top_factors" in res["explanation"]
    assert "recommended_actions" in res["explanation"]


def test_missing_model_fallback_graceful():
    """Verify that if models are missing, the inference function returns a clean fallback without crashing."""
    p_dict = {
        "approved_budget": 1000.0,
        "revised_budget": None,
        "actual_expenditure": 200.0,
        "planned_start_date": date(2023, 1, 1),
        "expected_completion_date": date(2026, 1, 1),
        "sector": "Water & Sanitation",
        "region": "Central",
    }
    # Test with normal call
    res = predict_project_risk(
        project_dict=p_dict,
        planned_progress=25.0,
        actual_progress=22.0,
    )
    assert res["risk_score"] < 40.0
    assert res["risk_level"] in ("LOW", "MODERATE")
