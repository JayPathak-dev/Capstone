import os
import json
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np

from backend.app.core.config import settings
from backend.app.ml.fallback import calculate_calibrated_risk

_COST_MODEL = None
_DELAY_MODEL = None
_DELAY_DAYS_MODEL = None
_METADATA = None


def load_models():
    """Load serialized ML pipelines from artifacts directory if present."""
    global _COST_MODEL, _DELAY_MODEL, _DELAY_DAYS_MODEL, _METADATA
    cost_path = os.path.join(settings.ML_MODEL_DIR, "cost_regressor.joblib")
    delay_path = os.path.join(settings.ML_MODEL_DIR, "delay_classifier.joblib")
    delay_days_path = os.path.join(settings.ML_MODEL_DIR, "delay_days_regressor.joblib")
    meta_path = os.path.join(settings.ML_MODEL_DIR, "baseline_model_metadata.json")

    if os.path.exists(cost_path) and os.path.exists(delay_path):
        try:
            _COST_MODEL = joblib.load(cost_path)
            _DELAY_MODEL = joblib.load(delay_path)
            if os.path.exists(delay_days_path):
                _DELAY_DAYS_MODEL = joblib.load(delay_days_path)
            if os.path.exists(meta_path):
                with open(meta_path, "r") as f:
                    _METADATA = json.load(f)
            return True
        except Exception:
            _COST_MODEL = None
            _DELAY_MODEL = None
            return False
    return False


def predict_project_risk(
    project_dict: Dict[str, Any],
    planned_progress: float,
    actual_progress: float,
    overdue_milestones_count: int = 0,
    max_milestone_delay_days: int = 0,
    recent_prog_delta_3m: float = 3.0,
    recent_exp_delta_3m: float = 5.0,
) -> Dict[str, Any]:
    """
    Produce a complete, explainable risk prediction.
    If ML artifacts are loaded, evaluates gradient boosted models.
    Otherwise, transparently utilizes the calibrated fallback engine.
    """
    global _COST_MODEL, _DELAY_MODEL

    if _COST_MODEL is None or _DELAY_MODEL is None:
        if not load_models():
            # Use resilient calibrated heuristic fallback
            return calculate_calibrated_risk(
                approved_budget=project_dict["approved_budget"],
                revised_budget=project_dict.get("revised_budget"),
                actual_expenditure=project_dict["actual_expenditure"],
                planned_progress=planned_progress,
                actual_progress=actual_progress,
                planned_start_date=project_dict["planned_start_date"],
                expected_completion_date=project_dict["expected_completion_date"],
                overdue_milestones_count=overdue_milestones_count,
                max_milestone_delay_days=max_milestone_delay_days,
                recent_progress_delta_3m=recent_prog_delta_3m,
                recent_expenditure_delta_3m=recent_exp_delta_3m,
            )

    try:
        # Construct feature vector
        effective_budget = project_dict.get("revised_budget") or project_dict["approved_budget"]
        has_revised = 1 if (project_dict.get("revised_budget") and project_dict["revised_budget"] > project_dict["approved_budget"]) else 0
        budget_util_ratio = round(project_dict["actual_expenditure"] / max(1.0, project_dict["approved_budget"]), 3)
        phys_gap = round(planned_progress - actual_progress, 2)
        burn_pct = round((project_dict["actual_expenditure"] / max(1.0, effective_budget)) * 100.0, 2)
        fin_gap = round(burn_pct - actual_progress, 2)
        vel_ratio = round(recent_prog_delta_3m / max(0.1, recent_exp_delta_3m), 3)

        total_days = max(1, (project_dict["expected_completion_date"] - project_dict["planned_start_date"]).days)
        duration_months = max(6, int(total_days / 30.4))
        from datetime import date
        days_elapsed = max(0, (date.today() - project_dict["planned_start_date"]).days)
        time_elapsed_ratio = min(2.0, round(days_elapsed / total_days, 2))

        feature_row = {
            "sector": project_dict["sector"],
            "region": project_dict["region"],
            "approved_budget": project_dict["approved_budget"],
            "has_revised_budget": has_revised,
            "duration_months": duration_months,
            "time_elapsed_ratio": time_elapsed_ratio,
            "planned_progress": planned_progress,
            "actual_progress": actual_progress,
            "physical_progress_gap": phys_gap,
            "budget_utilization_ratio": budget_util_ratio,
            "financial_gap": fin_gap,
            "recent_prog_delta_3m": recent_prog_delta_3m,
            "recent_exp_delta_3m": recent_exp_delta_3m,
            "velocity_ratio": vel_ratio,
            "overdue_milestones": overdue_milestones_count,
            "max_milestone_delay": max_milestone_delay_days,
        }
        df_feat = pd.DataFrame([feature_row])

        # 1. Regress cost overrun in ₹ Crores
        pred_cost_overrun_crores = float(_COST_MODEL.predict(df_feat)[0])
        pred_cost_overrun_crores = max(0.0, pred_cost_overrun_crores)
        expected_final_cost = round(project_dict["approved_budget"] + pred_cost_overrun_crores, 2)

        # 2. Classify delay probability (>60 days)
        delay_prob = float(_DELAY_MODEL.predict_proba(df_feat)[0][1])
        delay_prob = round(delay_prob, 3)

        # 3. Predict delay days
        if _DELAY_DAYS_MODEL is not None:
            pred_delay_days = max(0, int(_DELAY_DAYS_MODEL.predict(df_feat)[0]))
        else:
            pred_delay_days = max(0, int(phys_gap * 6.5 + overdue_milestones_count * 40))

        # Cost Overrun Probability
        cost_overrun_prob = min(0.99, max(0.05, round(pred_cost_overrun_crores / max(50.0, project_dict["approved_budget"] * 0.25), 3)))

        # Composite calibrated risk score
        cost_score = min(100.0, (pred_cost_overrun_crores / max(10.0, project_dict["approved_budget"])) * 150.0)
        delay_score = delay_prob * 100.0
        gap_score = min(100.0, max(0.0, phys_gap * 1.5 + fin_gap * 0.8))
        milestone_score = min(100.0, overdue_milestones_count * 30.0)

        composite_score = round(
            min(100.0, max(5.0, 0.30 * cost_score + 0.35 * delay_score + 0.20 * gap_score + 0.15 * milestone_score)),
            1,
        )

        if composite_score >= 75.0:
            risk_level = "CRITICAL"
        elif composite_score >= 50.0:
            risk_level = "HIGH"
        elif composite_score >= 30.0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Explainability Factor Attributions
        factors = []
        actions = []

        if phys_gap > 10.0:
            factors.append({
                "factor": "Physical Progress Deficit",
                "description": f"Physical execution ({actual_progress:.1f}%) lags planned target ({planned_progress:.1f}%) by {phys_gap:.1f}%.",
                "impact": f"+{min(35.0, phys_gap * 1.2):.1f} risk pts",
                "severity": "CRITICAL" if phys_gap > 25.0 else "HIGH",
            })
            actions.append("Direct concessionaire to deploy parallel construction shifts on delayed work fronts.")

        if fin_gap > 10.0:
            factors.append({
                "factor": "Expenditure-to-Physical Decoupling",
                "description": f"Budget burn ({burn_pct:.1f}%) significantly exceeds physical works delivered ({actual_progress:.1f}%).",
                "impact": f"+{min(30.0, fin_gap * 0.9):.1f} risk pts",
                "severity": "HIGH",
            })
            actions.append("Withhold subsequent mobilization disbursements until verified physical measurement on site.")

        if overdue_milestones_count > 0:
            factors.append({
                "factor": "Contractual Milestone Bottleneck",
                "description": f"{overdue_milestones_count} critical path milestone(s) are overdue by up to {max_milestone_delay_days} days.",
                "impact": f"+{min(25.0, overdue_milestones_count * 10.0):.1f} risk pts",
                "severity": "HIGH" if overdue_milestones_count >= 2 else "MEDIUM",
            })
            actions.append("Convene emergency milestone review with Department Chief Engineer.")

        if vel_ratio < 0.65:
            factors.append({
                "factor": "Trailing Quarter Velocity Collapse",
                "description": f"Execution velocity ratio ({vel_ratio:.2f}) indicates contractor deceleration.",
                "impact": "+12.5 risk pts",
                "severity": "MEDIUM",
            })
            actions.append("Conduct manpower and construction machinery audit across packages.")

        if not factors:
            factors.append({
                "factor": "Stable Execution Trajectory",
                "description": "Project variance parameters remain within sanctioned contractual tolerances.",
                "impact": "0 risk pts",
                "severity": "LOW",
            })
            actions.append("Maintain routine monthly monitoring cycles.")

        return {
            "cost_overrun_probability": cost_overrun_prob,
            "delay_probability": delay_prob,
            "expected_final_cost": expected_final_cost,
            "predicted_delay_days": pred_delay_days,
            "risk_score": composite_score,
            "risk_level": risk_level,
            "model_version": "gbdt-risk-v1.0",
            "is_fallback": False,
            "explanation": {
                "top_factors": factors,
                "recommended_actions": actions,
                "metrics": {
                    "budget_utilization_ratio": budget_util_ratio,
                    "physical_progress_gap": phys_gap,
                    "financial_gap": fin_gap,
                    "velocity_ratio": vel_ratio,
                    "overdue_milestones": overdue_milestones_count,
                },
            },
        }
    except Exception:
        # Fallback to calibrated heuristic if any unexpected failure occurs
        return calculate_calibrated_risk(
            approved_budget=project_dict["approved_budget"],
            revised_budget=project_dict.get("revised_budget"),
            actual_expenditure=project_dict["actual_expenditure"],
            planned_progress=planned_progress,
            actual_progress=actual_progress,
            planned_start_date=project_dict["planned_start_date"],
            expected_completion_date=project_dict["expected_completion_date"],
            overdue_milestones_count=overdue_milestones_count,
            max_milestone_delay_days=max_milestone_delay_days,
            recent_progress_delta_3m=recent_prog_delta_3m,
            recent_expenditure_delta_3m=recent_exp_delta_3m,
        )
