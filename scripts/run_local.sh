#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " Starting PAIMANA Infrastructure Intelligence Platform"
echo "=========================================================="

# Check virtualenv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r backend/requirements.txt
fi

# Seed database if not existing
if [ ! -f "paimana.db" ]; then
    echo "Seeding initial infrastructure dataset..."
    .venv/bin/python scripts/seed_database.py
fi

# Ensure frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo ""
echo "Starting FastAPI Backend on http://localhost:8000 ..."
.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting React Frontend on http://localhost:5173 ..."
cd frontend && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo ""
echo "=========================================================="
echo " PAIMANA Intelligence is running!"
echo " Frontend: http://localhost:5173"
echo " API Docs: http://localhost:8000/docs"
echo " Press Ctrl+C to stop services."
echo "=========================================================="

wait
