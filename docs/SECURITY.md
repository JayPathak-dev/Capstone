# PAIMANA Security, Privacy & Reliability Specification

---

## 1. Threat Model & Trust Boundaries

The system processes public infrastructure project records, financial sanctions, and predictive assessments. Security controls protect against data tampering, unauthorized modifications, denial-of-service, and AI hallucination attacks.

### Trust Boundaries
1. **Public Web Browser <-> API Gateway**: Untrusted input boundary. All inputs must pass Pydantic schema validation.
2. **API Services <-> Persistence Layer**: Strict parameterization via SQLAlchemy ORM; direct raw SQL string interpolation is prohibited.
3. **AI Assistant <-> Database**: LLM is never given direct SQL execution privileges. All data access occurs through typed, read-only Python tool calls with bounds checking.
4. **File Import Boundary**: CSV uploads are validated against schema, max file size limits (10 MB), and rate limiting before transactional commit.

---

## 2. Authentication & Authorization (RBAC)

The system supports role-based access control with predefined roles:

| Role | Permissions |
| :--- | :--- |
| **Viewer / Official** | Read-only access to dashboards, project explorer, risk reports, assistant queries. |
| **Project Officer** | Can acknowledge/resolve assigned alerts and submit monthly progress updates. |
| **System Administrator** | Can import CSV datasets, trigger model retraining, and configure system thresholds. |

---

## 3. Data Protection & Hygiene

- **Secret Management**: Passwords, API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`), and database credentials must only be injected via environment variables. Committed `.env` files are blocked via `.gitignore`.
- **CORS Policy**: Configurable origin whitelist (e.g., `http://localhost:5173`) prevents unauthorized cross-origin browser requests.
- **SQL Injection Prevention**: 100% of database queries utilize SQLAlchemy 2.0 select and filter expressions with automatic parameter binding.
- **Input Sanitization**: CSV parser strictly sanitizes headers and string values to prevent CSV formula injection (e.g., values starting with `=`, `@`, `+`, `-`).
- **Audit Logging**: Sensitive operations (data ingestion, alert acknowledgment, alert resolution, manual risk reassessment) write an immutable audit trail entry.

---

## 4. AI Guardrails & Prompt Injection Defense

- **Separation of Instructions and Data**: System prompts explicitly designate user input and retrieved project data into clearly delineated context wrappers (`<PROJECT_CONTEXT>...</PROJECT_CONTEXT>`).
- **Hallucination Prevention**: Assistant system prompt enforces strict citation: if project data is not returned by a tool, the assistant must state "Data not found in current PAIMANA records" rather than guessing.
- **Decision Support Only**: Assistant responses include disclaimer: "This output is AI-assisted decision support. All administrative decisions must be confirmed with primary official records."
