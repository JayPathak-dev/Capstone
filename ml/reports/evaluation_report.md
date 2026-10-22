# PAIMANA Machine Learning Model Evaluation Report
**Model Version**: `gbdt-risk-v1.0`
**Evaluation Date**: `2026-10-22T20:40:07.160024`

---

## 1. Cost Overrun Regression Evaluation

| Model Architecture | MAE (₹ Crores) | RMSE (₹ Crores) | $R^2$ Score |
| :--- | :--- | :--- | :--- |
| **Baseline (Ridge)** | ₹ 456.23 Cr | ₹ 861.45 Cr | 0.812 |
| **Production (HistGradientBoosting)** | **₹ 190.69 Cr** | **₹ 634.31 Cr** | **0.792** |

---

## 2. Schedule Delay (>60 Days) Classification Evaluation

| Model Architecture | ROC-AUC | F1-Score | Precision | Recall |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (Logistic Regression)** | 0.999 | 0.771 | 0.785 | 0.758 |
| **Production (HistGBDT)** | **0.998** | **0.991** | **0.991** | **0.991** |

---

## 3. Top Feature Importances & Attributions
- `budget_utilization_ratio`: Primary driver of cost risk (+0.34 correlation).
- `physical_progress_gap`: Strongest leading indicator of schedule delay (+0.41 correlation).
- `overdue_milestones`: Multiplier effect on catastrophic slippage (+0.28 correlation).
- `velocity_ratio`: Early warning signal of contractor deceleration.
