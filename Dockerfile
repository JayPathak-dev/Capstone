# ==============================================================================
# Multi-Stage Dockerfile for PAIMANA Intelligence Platform
# Stage 1: Build React Frontend
# Stage 2: Python 3.11 Runtime + ML Engine + FastAPI
# ==============================================================================

FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend, ml, and sample data
COPY backend/ ./backend/
COPY ml/ ./ml/
COPY sample_data/ ./sample_data/
COPY scripts/ ./scripts/
COPY pyproject.toml ./

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /build/dist ./frontend/dist

# Initialize tables & seed initial data
RUN python scripts/seed_database.py

# Expose port
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

# Start FastAPI application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
