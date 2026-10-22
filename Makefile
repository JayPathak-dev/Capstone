.PHONY: help setup dev seed test lint build clean docker-up docker-down

help:
	@echo "PAIMANA Intelligence Platform - Development Commands"
	@echo "  make setup      - Install Python and Node dependencies"
	@echo "  make seed       - Seed database with realistic infrastructure records"
	@echo "  make dev-backend- Start FastAPI server on port 8000"
	@echo "  make dev-frontend- Start Vite development server on port 5173"
	@echo "  make test       - Run all backend, ML, and frontend tests"
	@echo "  make build      - Build frontend production bundle"
	@echo "  make docker-up  - Start containerized app via Docker Compose"
	@echo "  make docker-down- Stop Docker containers"

setup:
	uv venv --python /opt/homebrew/bin/python3.11 .venv || python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

seed:
	.venv/bin/python scripts/seed_database.py

train-ml:
	.venv/bin/python ml/scripts/train_models.py

dev-backend:
	.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

test:
	.venv/bin/pytest backend/tests ml/tests -v
	cd frontend && npm run test

build:
	cd frontend && npm run build

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
