# PAIMANA Machine Learning & Predictive Analytics Methodology

---

## 1. Problem Formulation & Prediction Targets

Infrastructure project monitoring involves temporal sequences of progress and expenditure alongside static project characteristics. Rather than treating this as a single black box, PAIMANA formulates four distinct, complementary predictive tasks:

1. **Target 1: Cost Overrun Magnitude (Regression)**
   - Target variable: $y_{\text{cost}} = \text{Final Cost} - \text{Approved Budget}$ (in ₹ Crores), or cost overrun ratio $\frac{\text{Final Cost}}{\text{Approved Budget}} - 1.0$.
   - Objective: Predict expected final expenditure using project characteristics and trailing 3-6 month execution velocities.

2. **Target 2: Project Schedule Slippage (Classification & Regression)**
   - Target variable 2a: $y_{\text{delay\_flag}} \in \{0, 1\}$ (Binary classification: whether project completion exceeds sanctioned completion date by $> 60$ days).
   - Target variable 2b: $y_{\text{delay\_days}} \in \mathbb{N}$ (Regression: estimated number of delay days).

3. **Target 3: Composite Risk Scoring (0–100 Scale)**
   - Objective: A calibrated, single-glance composite score that combines cost risk, delay probability, milestone fragility, and velocity divergence.

4. **Target 4: Explainability & Feature Attributions**
   - Objective: For every prediction, generate quantitative feature contributions (SHAP values / linear tree contributions) detailing the top 3-5 drivers (e.g., "Physical progress lagging planned by 24%", "Budget burn rate 1.8x higher than physical completion velocity").

---

## 2. Feature Engineering Pipeline

To prevent **data leakage**, all features are strictly computed from information available *at or before the prediction cutoff date $T$*. Future dates, subsequent expenditures, and later progress entries are strictly excluded during feature extraction.

### Core Feature Vector ($x \in \mathbb{R}^d$)

| Feature Name | Description | Rationale |
| :--- | :--- | :--- |
| `budget_utilization_ratio` | $\frac{\text{actual\_expenditure}}{\text{approved\_budget}}$ | High burn with low progress indicates financial drainage. |
| `physical_progress_gap` | $\text{planned\_progress} - \text{actual\_progress}$ | Direct schedule gap in percentage points. |
| `progress_velocity_ratio` | $\frac{\Delta \text{actual\_progress}_{3m}}{\Delta \text{planned\_progress}_{3m}}$ | Pace of current work relative to plan over last quarter. |
| `financial_to_physical_velocity` | $\frac{\Delta \text{expenditure\_pct}_{3m}}{\Delta \text{actual\_progress}_{3m} + \epsilon}$ | Detects expenditure without commensurate physical output. |
| `milestone_overdue_count` | Count of milestones where `planned_date < T` and `status != 'COMPLETED'`. | Leading indicator of critical path breakdown. |
| `milestone_delay_avg_days` | Mean delay in days across overdue milestones. | Measures structural severity of contractor bottlenecks. |
| `time_elapsed_ratio` | $\frac{T - \text{planned\_start}}{\text{planned\_completion} - \text{planned\_start}}$ | Normalized project lifecycle stage. |
| `revised_budget_flag` | $1$ if `revised_budget > approved_budget` else $0$ | Existing administrative cost revision history. |
| `sector_encoded` | One-hot / Target encoded infrastructure sector | Highways vs. Railways vs. Metro have different capital risk profiles. |
| `region_encoded` | Categorical encoding of geographic region | Hilly/North-East terrain historically shows higher weather-related delay. |
| `reporting_freshness_days` | Days since last filed monthly progress update | Stale reporting strongly correlates with unmanaged project trouble. |

---

## 3. Modeling Algorithms & Benchmarks

1. **Baseline Models (Interpretable Benchmarks)**
   - Regression: Ordinary Least Squares (OLS) with L2 Ridge Regularization.
   - Classification: Calibrated Logistic Regression.
2. **Production Ensemble Models**
   - Cost Regression: Gradient Boosting Regressor (LightGBM / Scikit-Learn GradientBoostingRegressor) with Huber loss for robustness against extreme outlier project costs.
   - Delay Classification: Random Forest / Gradient Boosting Classifier with Platt scaling probability calibration.
3. **Calibrated Fallback Engine**
   - If model artifact files are missing or corrupted, a rule-based inference engine calculates risk scores from validated business thresholds (variance gap, milestone ratio, velocity divergence). This guarantees the application never crashes or presents unverified ML predictions.

---

## 4. Model Evaluation & Validation Strategy

- **Time-Aware & Group-K-Fold Validation**: Projects are grouped by `project_code` so updates from the same project never appear in both train and test folds. Time-split validation simulates training on historic projects (e.g., 2018–2022) and evaluating on future projects (2023–2024).
- **Metrics for Regression**:
  - Mean Absolute Error (MAE in ₹ Crores).
  - Root Mean Squared Error (RMSE).
  - Mean Absolute Percentage Error (MAPE).
- **Metrics for Classification**:
  - Area Under ROC Curve (ROC-AUC).
  - Precision-Recall AUC (PR-AUC) — vital for imbalanced delays.
  - Brier Score (measuring probability calibration quality).

---

## 5. Composite Risk Score Definition (0 to 100)

The composite risk score is defined as:
$$\text{RiskScore} = \min\left(100, \max\left(0, w_1 \cdot (P_{\text{cost}} \times 100) + w_2 \cdot (P_{\text{delay}} \times 100) + w_3 \cdot \text{GapScore} + w_4 \cdot \text{MilestoneFragility}\right)\right)$$
Where:
- $w_1 = 0.30$ (Cost Overrun Risk)
- $w_2 = 0.30$ (Schedule Delay Risk)
- $w_3 = 0.25$ (Physical-vs-Financial Gap)
- $w_4 = 0.15$ (Overdue Milestone Fragility)

### Risk Bands
- **Low**: $0.00 \le \text{Score} < 30.00$ (Green)
- **Moderate**: $30.00 \le \text{Score} < 50.00$ (Amber/Yellow)
- **High**: $50.00 \le \text{Score} < 75.00$ (Orange)
- **Critical**: $75.00 \le \text{Score} \le 100.00$ (Red)
