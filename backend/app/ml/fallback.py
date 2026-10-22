from typing import Dict, Any, List, Tuple
from datetime import date


def calculate_calibrated_risk(
    approved_budget: float,
    revised_budget: float | None,
    actual_expenditure: float,
    planned_progress: float,
    actual_progress: float,
    planned_start_date: date,
    expected_completion_date: date,
    overdue_milestones_count: int = 0,
    max_milestone_delay_days: int = 0,
    recent_progress_delta_3m: float = 3.0,
    recent_expenditure_delta_3m: float = 5.0,
) -> Dict[str, Any]:
    """
    Calibrated heuristic risk evaluation engine.
    Ensures that even if ML model artifacts (.joblib) are absent,
    the application produces mathematically robust, explainable risk assessments.
    """
    effective_budget = revised_budget if (revised_budget and revised_budget > 0) else approved_budget
    burn_ratio = (actual_expenditure / effective_budget) if effective_budget > 0 else 0.0

    # 1. Physical vs Financial Gap
    progress_gap = max(0.0, planned_progress - actual_progress)
    financial_gap = max(0.0, (burn_ratio * 100.0) - actual_progress)

    # 2. Velocity Divergence
    velocity_ratio = 1.0
    if recent_expenditure_delta_3m > 0:
        velocity_ratio = recent_progress_delta_3m / max(0.1, recent_expenditure_delta_3m)

    # 3. Time elapsed
    today = date.today()
    total_duration_days = max(1, (expected_completion_date - planned_start_date).days)
    days_elapsed = max(0, (today - planned_start_date).days)
    time_elapsed_ratio = min(2.0, days_elapsed / total_duration_days)

    # 4. Probabilities calculation
    # Cost Overrun Probability
    cost_risk_base = min(1.0, max(0.0, (burn_ratio - (actual_progress / 100.0)) * 1.5))
    if revised_budget and revised_budget > approved_budget:
        cost_risk_base = min(1.0, cost_risk_base + 0.25)
    cost_overrun_prob = round(min(0.99, max(0.05, cost_risk_base)), 3)

    # Delay Probability
    delay_risk_base = min(1.0, max(0.0, (progress_gap / 50.0) + (overdue_milestones_count * 0.12)))
    if time_elapsed_ratio > 0.8 and actual_progress < 60.0:
        delay_risk_base = min(1.0, delay_risk_base + 0.3)
    delay_prob = round(min(0.99, max(0.05, delay_risk_base)), 3)

    # Predicted Delay Days
    if actual_progress > 5.0:
        estimated_total_days = total_duration_days * (100.0 / max(10.0, actual_progress)) * (time_elapsed_ratio if time_elapsed_ratio > 0.5 else 1.0)
        predicted_delay_days = max(0, int(estimated_total_days - total_duration_days))
    else:
        predicted_delay_days = int(overdue_milestones_count * 45 + progress_gap * 5)

    if max_milestone_delay_days > 0:
        predicted_delay_days = max(predicted_delay_days, int(max_milestone_delay_days * 1.2))

    # Expected Final Cost
    if actual_progress > 10.0:
        extrapolated_cost = (actual_expenditure / (actual_progress / 100.0))
        # Weight between budget and current pace
        expected_final_cost = round(0.4 * effective_budget + 0.6 * extrapolated_cost, 2)
    else:
        expected_final_cost = round(effective_budget * (1.0 + cost_overrun_prob * 0.35), 2)

    # Composite 0-100 Score
    # Weights: Cost (30%), Delay (30%), Gap (25%), Milestones (15%)
    gap_component = min(100.0, (progress_gap * 1.2) + (financial_gap * 0.8))
    milestone_component = min(100.0, overdue_milestones_count * 25.0 + (max_milestone_delay_days / 3.0))

    composite_score = (
        0.30 * (cost_overrun_prob * 100.0) +
        0.30 * (delay_prob * 100.0) +
        0.25 * gap_component +
        0.15 * milestone_component
    )

    composite_score = round(min(100.0, max(0.0, composite_score)), 1)

    # Categorize Risk Level
    if composite_score >= 75.0:
        risk_level = "CRITICAL"
    elif composite_score >= 50.0:
        risk_level = "HIGH"
    elif composite_score >= 30.0:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # Generate Explainability Factors
    top_factors: List[Dict[str, str]] = []
    actions: List[str] = []

    if progress_gap > 15.0:
        top_factors.append({
            "factor": "Physical Execution Deficit",
            "description": f"Actual physical progress ({actual_progress:.1f}%) lags sanctioned plan ({planned_progress:.1f}%) by {progress_gap:.1f}% points.",
            "impact": f"+{min(35.0, progress_gap * 1.1):.1f} risk points",
            "severity": "CRITICAL" if progress_gap > 25.0 else "HIGH"
        })
        actions.append(f"Institute bi-weekly contractor site reviews to remediate the {progress_gap:.1f}% physical slippage.")

    if financial_gap > 10.0:
        top_factors.append({
            "factor": "Financial Burn vs. Physical Asset Discrepancy",
            "description": f"Budget utilization ({burn_ratio * 100:.1f}%) is significantly higher than physical delivery ({actual_progress:.1f}%).",
            "impact": f"+{min(30.0, financial_gap * 0.9):.1f} risk points",
            "severity": "HIGH"
        })
        actions.append("Conduct an interim financial audit on booked vouchers versus physical work measured on site.")

    if overdue_milestones_count > 0:
        top_factors.append({
            "factor": "Critical Path Milestone Delays",
            "description": f"{overdue_milestones_count} scheduled milestone(s) are overdue, with max delay of {max_milestone_delay_days} days.",
            "impact": f"+{min(25.0, overdue_milestones_count * 8.5):.1f} risk points",
            "severity": "HIGH" if overdue_milestones_count >= 2 else "MEDIUM"
        })
        actions.append(f"Resolve contractor bottlenecks for {overdue_milestones_count} delayed milestone deliverables.")

    if velocity_ratio < 0.6:
        top_factors.append({
            "factor": "Declining Execution Velocity",
            "description": f"Physical progress rate has slowed to {velocity_ratio:.2f}x of financial burn over recent quarter.",
            "impact": "+14.0 risk points",
            "severity": "MEDIUM"
        })
        actions.append("Reassess contractor plant and equipment mobilization on active packages.")

    if not top_factors:
        top_factors.append({
            "factor": "Normal Execution Envelope",
            "description": "Progress and expenditure trajectories conform within acceptable contract tolerances.",
            "impact": "0 risk points",
            "severity": "LOW"
        })
        actions.append("Maintain routine monthly monitoring and milestone inspection schedule.")

    return {
        "cost_overrun_probability": cost_overrun_prob,
        "delay_probability": delay_prob,
        "expected_final_cost": expected_final_cost,
        "predicted_delay_days": predicted_delay_days,
        "risk_score": composite_score,
        "risk_level": risk_level,
        "model_version": "calibrated-heuristic-v1.0",
        "is_fallback": True,
        "explanation": {
            "top_factors": top_factors,
            "recommended_actions": actions,
            "metrics": {
                "burn_ratio": round(burn_ratio, 3),
                "progress_gap": round(progress_gap, 2),
                "financial_gap": round(financial_gap, 2),
                "overdue_milestones": overdue_milestones_count,
                "velocity_ratio": round(velocity_ratio, 3),
            }
        }
    }
