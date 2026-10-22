# PAIMANA Deployment & Operations Guide

---

## 1. Local Development Quickstart

### Prerequisites
- Python 3.11+ (or uv)
- Node.js 18+ & npm
- Git

### 1-Minute Local Setup
```bash
# 1. Clone & Enter Directory
git clone https://github.com/JayPathak-dev/Capstone.git
cd Capstone

# 2. Setup Python Virtual Environment (using uv or python3 -m venv)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Seed Database with Realistic Infrastructure Sample Data
python scripts/seed_database.py

# 4. Start FastAPI Backend (Port 8000)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. In a second terminal, setup & run React Frontend (Port 5173)
cd frontend
npm install
npm run dev
```

Visit the dashboard at `http://localhost:5173` and API docs at `http://localhost:8000/docs`.

---

## 2. Docker & Containerized Deployment

A multi-stage `Dockerfile` and `docker-compose.yml` are provided for one-command containerized execution:

```bash
# Build and run backend, frontend, and PostgreSQL services
docker-compose up --build -d
```

Services:
- **Frontend SPA**: `http://localhost:3000` (Nginx serving production bundle)
- **FastAPI API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`

---

## 3. Production Environment Variables Reference

| Variable Name | Default Value | Production Recommendation |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Set to `production` |
| `DEBUG` | `True` | Set to `False` |
| `SECRET_KEY` | `change-this...` | Cryptographically generated 64-char hex string |
| `DATABASE_URL` | `sqlite:///./paimana.db` | Managed PostgreSQL instance URL (`postgresql://user:pass@host/db`) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Strict list of deployed frontend domain names |
| `LLM_PROVIDER` | `mock` | `gemini` (requires `GEMINI_API_KEY`) or `openai` |
| `GEMINI_API_KEY` | (empty) | Injected via secure cloud secret manager |
