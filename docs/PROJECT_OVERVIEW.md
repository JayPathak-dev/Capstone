# PAIMANA — AI-Powered Predictive Analytics and Early Warning System for Infrastructure Projects
**Smart India Hackathon Problem Statement SIH26103**

---

## 1. Executive Summary

Infrastructure mega-projects (highways, rail corridors, metro lines, port expansions, water supply systems, power grids) represent the lifeblood of national economic development. However, global and national experience demonstrates that infrastructure projects frequently suffer from severe **cost overruns (20–60% above sanctioned estimates)** and **schedule delays (6 to 36+ months)**.

Current systems like PAIMANA capture transactional monitoring records: expenditure vouchers, milestone check-offs, and monthly progress percentages. While essential, this backward-looking data only records *what has already occurred*. Project authorities and monitoring committees often discover delays and budget breaches months after the underlying issues began compounding.

**PAIMANA Intelligence** transforms conventional infrastructure monitoring from a reactive ledger into a **proactive, predictive early warning and decision intelligence platform**. It answers four fundamental questions for decision-makers:
1. **What is the current ground-truth status of each infrastructure project?**
2. **Which projects are likely to experience severe cost overruns or schedule delays?**
3. **What specific factors, bottlenecks, and anomalies are driving risk for each project?**
4. **What high-impact corrective actions should officials take before projects deteriorate further?**

---

## 2. Key Objectives & Scope

- **Predictive Risk Modeling**: Predict final cost variance, probability of cost overrun, and schedule delay in days using machine learning trained on historical project trajectories and leading indicators.
- **Explainable AI (XAI)**: Demystify predictions using feature contribution analysis (SHAP values and calibrated risk drivers) so senior officials understand *why* a project is flagged.
- **Automated Early Warning Signals**: Detect adverse patterns—such as physical progress stagnation despite continued financial drawdown, milestone slippages, and vendor velocity collapse—triggering prioritized, auditable alerts.
- **Similar-Project Benchmarking**: Empirically compare a project against historical peers in the same sector, budget tier, and geographic region.
- **Grounded AI Assistant**: An interactive natural-language assistant powered by governed tool calls that queries ground-truth project tables and ML models without hallucinations or unrestricted database execution.
- **Transparent Data Governance**: Comprehensive data validation engine for importing CSV records with duplicate checking, boundary validation, and audit logging.

---

## 3. Target User Personas

| Persona | Primary Needs & Responsibilities | Key Platform Features Utilized |
| :--- | :--- | :--- |
| **Department Secretary / Senior Bureaucrat** | Portfolio-level risk exposure, inter-sector performance, macro budget variances, critical early warnings | Overview Dashboard, Risk Intelligence Heatmap, Executive Summary |
| **Project Monitoring Officer (PMO)** | Monthly progress verification, milestone tracking, contractor performance, anomaly alerts | Project Explorer, Detailed Timeline & Milestones, Early Warning Center |
| **Project Director / Chief Engineer** | On-site milestone execution, root-cause diagnostics, benchmarking against peer projects | Project Deep Dive, Benchmarking Radar, Explainable Risk Drivers |
| **Financial Controller / Audit Officer** | Expenditure velocity vs. physical delivery, revised sanction tracking, cost overrun probability | Financial Progress Analytics, Cost Variance Forecasts, Audit Log |
| **Policy & Data Analyst** | Model performance inspection, feature importance, scenario analysis, data import validation | Model Performance Center, Data Management Studio, AI Assistant |

---

## 4. Key Performance Indicators (KPIs)

1. **Portfolio Health Index (PHI)**: Aggregate weighted health of all sanctioned infrastructure schemes.
2. **Cost Overrun Probability (COP)**: Model-estimated probability ($P \in [0, 1]$) of exceeding sanctioned capital outlay.
3. **Schedule Slippage Estimate (SSE)**: Quantified forecast of delay days beyond sanctioned completion date.
4. **Physical-to-Financial Velocity Ratio (PFVR)**: Ratio of monthly physical progress rate to financial burn rate; values $< 0.65$ indicate expenditure without commensurate physical assets.
5. **Milestone Criticality Index (MCI)**: Count and duration of delayed milestone dependencies on critical path.
