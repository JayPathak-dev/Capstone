# PAIMANA Engineering Decisions & Trade-off Analysis (ADR)

---

## ADR 01: Modular Monolith vs. Distributed Microservices
- **Decision**: Adopt a modular monolith architecture (single FastAPI backend + single React Vite frontend) instead of multiple microservices.
- **Context**: Hackathon prototype requiring rapid iteration, seamless local setup, and zero distributed failure modes while maintaining clean service boundaries.
- **Trade-offs**: Single deployment unit and simpler debugging, while internal service modules (`projects`, `predictions`, `alerts`, `assistant`) maintain decoupled interfaces that can later be extracted into independent services if scaling demands it.

---

## ADR 02: Dual Database Strategy (SQLite for Dev, PostgreSQL for Production)
- **Decision**: Use SQLAlchemy 2.0 with driver abstraction allowing zero-config local runs with SQLite (`sqlite:///./paimana.db`) and seamless PostgreSQL compatibility for production (`DATABASE_URL=postgresql://...`).
- **Context**: Evaluators, judges, and developers need to test the project in seconds without requiring a local PostgreSQL daemon or Docker container running.
- **Trade-offs**: Avoid database-specific SQL dialect features (e.g., PostgreSQL-only JSON operators) in favor of standard SQLAlchemy ORM constructs.

---

## ADR 03: Governed Tool Calling vs. Text-to-SQL for AI Assistant
- **Decision**: Restrict the AI assistant to explicit, typed Python tool functions (`get_project_details`, `list_high_risk_projects`, etc.) rather than allowing LLM-generated raw SQL.
- **Context**: LLM text-to-SQL generation is prone to SQL injection, hallucinations of non-existent columns, Cartesian product queries that crash the database, and unexplainable answers.
- **Trade-offs**: Tools cover defined query patterns rather than arbitrary SQL, but deliver 100% deterministic, secure, and verifiable responses with traceable evidence.

---

## ADR 04: Scikit-Learn Gradient Boosting with Interpretable Tree Contributions
- **Decision**: Train Gradient Boosting models with Scikit-Learn (`HistGradientBoostingRegressor` / `RandomForestClassifier`), coupled with feature importance and SHAP explanations.
- **Context**: Deep neural networks require massive sample sizes and GPU acceleration while offering poor tabular data performance and opaque explainability. Gradient boosted trees are standard for tabular project records.
- **Trade-offs**: Robust performance on tabular datasets with tens of thousands of records, fast CPU inference (<15ms), and immediate feature contribution explainability.

---

## ADR 05: Fail-Safe Fallback Risk Engine
- **Decision**: Implement a calibrated rule-based risk calculation engine that automatically activates if serialized ML model weights are absent.
- **Context**: Missing model weight files during initial cloning or container bootstrapping must never cause an unhandled 500 error or crash the application.
- **Trade-offs**: Guarantees system resilience and clear disclosure: the UI explicitly reports whether the score was produced by `ML_MODEL_V1` or `CALIBRATED_FALLBACK_V1`.
