# Multi-stage build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app
COPY backend/alembic.ini .
COPY backend/migrations ./migrations

# Copy built frontend from builder
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY frontend/package.json ./frontend/

WORKDIR /app

# Expose ports
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
