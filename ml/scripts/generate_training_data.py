import os
import random
import pandas as pd
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

SECTORS = [
    "Roads & Highways",
    "Railways",
    "Urban Mass Transit",
    "Power & Renewable Energy",
    "Water & Sanitation",
    "Ports & Shipping",
]

REGIONS = ["Northern", "Western", "Southern", "Eastern", "North-Eastern", "Central"]


def generate_synthetic_ml_dataset(n_samples: int = 1200) -> pd.DataFrame:
    """
    Generate a realistic, synthetic infrastructure training dataset with
    temporal feature extraction, avoiding data leakage.
    """
    rows = []

    for i in range(n_samples):
        project_code = f"INFRA-{2018 + (i % 6)}-{1000 + i}"
        sector = random.choice(SECTORS)
        region = random.choice(REGIONS)

        # Approved budget in ₹ Crores (log-normal distribution)
        approved_budget = round(float(np.random.lognormal(mean=7.5, sigma=1.0)), 2)
        approved_budget = max(50.0, min(120000.0, approved_budget))

        # Planned project duration in months (12 to 72 months)
        duration_months = random.randint(18, 72)

        # Elapsed project lifecycle fraction at time of evaluation T (0.15 to 0.90)
        time_elapsed_ratio = round(random.uniform(0.15, 0.95), 2)

        # Has revised budget been sanctioned?
        has_revised_budget = 1 if random.random() < 0.35 else 0
        revised_budget_ratio = (
            round(random.uniform(1.05, 1.35), 2) if has_revised_budget else 1.0
        )
        revised_budget = round(approved_budget * revised_budget_ratio, 2) if has_revised_budget else approved_budget

        # Planned progress at evaluation cutoff T (roughly correlates with time elapsed)
        planned_progress = min(100.0, max(5.0, round(time_elapsed_ratio * 100.0 * random.uniform(0.9, 1.1), 1)))

        # Actual physical progress at T
        # Projects vary from on-track to severe delays
        performance_bias = random.choice(["HEALTHY", "MODERATE_STRESS", "SEVERE_DISTRESS"])
        if performance_bias == "HEALTHY":
            actual_progress = min(100.0, max(2.0, round(planned_progress * random.uniform(0.92, 1.05), 1)))
            burn_factor = random.uniform(0.85, 1.08)
            overdue_milestones = random.choices([0, 1], weights=[0.85, 0.15])[0]
            max_milestone_delay = random.randint(0, 30) if overdue_milestones > 0 else 0
        elif performance_bias == "MODERATE_STRESS":
            actual_progress = min(100.0, max(2.0, round(planned_progress * random.uniform(0.70, 0.90), 1)))
            burn_factor = random.uniform(1.05, 1.25)
            overdue_milestones = random.choices([1, 2], weights=[0.7, 0.3])[0]
            max_milestone_delay = random.randint(30, 90)
        else:  # SEVERE_DISTRESS
            actual_progress = min(100.0, max(2.0, round(planned_progress * random.uniform(0.40, 0.68), 1)))
            burn_factor = random.uniform(1.25, 1.65)
            overdue_milestones = random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
            max_milestone_delay = random.randint(90, 240)

        # Actual expenditure incurred at cutoff T
        actual_expenditure = round(
            min(revised_budget * 1.5, max(10.0, (actual_progress / 100.0) * approved_budget * burn_factor)), 2
        )
        budget_utilization_ratio = round(actual_expenditure / approved_budget, 3)

        # Physical vs. Financial Gap
        physical_progress_gap = round(planned_progress - actual_progress, 2)
        financial_burn_pct = round((actual_expenditure / approved_budget) * 100.0, 2)
        financial_gap = round(financial_burn_pct - actual_progress, 2)

        # Velocity features (past quarter)
        recent_prog_delta_3m = round(max(0.5, random.uniform(1.0, 5.0) * (0.6 if performance_bias == "SEVERE_DISTRESS" else 1.0)), 2)
        recent_exp_delta_3m = round(max(0.5, random.uniform(2.0, 7.0)), 2)
        velocity_ratio = round(recent_prog_delta_3m / max(0.5, recent_exp_delta_3m), 3)

        # Ground-truth targets (simulated future outcome at actual project completion)
        # 1. Cost overrun ratio: (Final Cost / Approved Budget) - 1.0
        true_cost_overrun_pct = round(
            max(
                -0.05,
                (burn_factor - 1.0) * 0.75
                + (0.15 if has_revised_budget else 0.0)
                + (financial_gap / 150.0)
                + np.random.normal(0, 0.04),
            )
            * 100.0,
            2,
        )
        forecast_final_cost = round(approved_budget * (1.0 + (true_cost_overrun_pct / 100.0)), 2)
        cost_overrun_crores = round(forecast_final_cost - approved_budget, 2)

        # 2. Delay days target
        true_delay_days = max(
            0,
            int(
                (physical_progress_gap * 7.5)
                + (overdue_milestones * 45)
                + (max_milestone_delay * 0.4)
                + np.random.normal(0, 15)
            ),
        )
        delay_flag_60d = 1 if true_delay_days >= 60 else 0

        # 3. Target Risk Score (0-100)
        risk_score = round(
            min(
                100.0,
                max(
                    5.0,
                    (delay_flag_60d * 30.0)
                    + min(35.0, max(0.0, true_cost_overrun_pct * 1.2))
                    + min(20.0, max(0.0, physical_progress_gap * 0.8))
                    + min(15.0, overdue_milestones * 5.0),
                ),
            ),
            1,
        )

        rows.append({
            "project_code": project_code,
            "sector": sector,
            "region": region,
            "approved_budget": approved_budget,
            "revised_budget": revised_budget,
            "has_revised_budget": has_revised_budget,
            "actual_expenditure": actual_expenditure,
            "duration_months": duration_months,
            "time_elapsed_ratio": time_elapsed_ratio,
            "planned_progress": planned_progress,
            "actual_progress": actual_progress,
            "physical_progress_gap": physical_progress_gap,
            "budget_utilization_ratio": budget_utilization_ratio,
            "financial_gap": financial_gap,
            "recent_prog_delta_3m": recent_prog_delta_3m,
            "recent_exp_delta_3m": recent_exp_delta_3m,
            "velocity_ratio": velocity_ratio,
            "overdue_milestones": overdue_milestones,
            "max_milestone_delay": max_milestone_delay,
            # Target labels
            "target_cost_overrun_crores": cost_overrun_crores,
            "target_cost_overrun_pct": true_cost_overrun_pct,
            "target_delay_days": true_delay_days,
            "target_delay_flag_60d": delay_flag_60d,
            "target_risk_score": risk_score,
        })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    os.makedirs("ml/data/processed", exist_ok=True)
    df = generate_synthetic_ml_dataset(1500)
    output_path = "ml/data/processed/training_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic infrastructure records at {output_path}")
