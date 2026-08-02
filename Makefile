.PHONY: help install setup start stop logs clean migrate test lint format build deploy

help:
	@echo "Career Assistant Platform - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install        Install all dependencies"
	@echo "  make setup          Complete setup with Docker"
	@echo ""
	@echo "Runtime Commands:"
	@echo "  make start          Start all services with Docker Compose"
	@echo "  make stop           Stop all services"
	@echo "  make logs           View all service logs"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-backend    Run backend in development mode"
	@echo "  make dev-frontend   Run frontend in development mode"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate        Run database migrations"
	@echo "  make migrate-new    Create new migration (msg='your message')"
	@echo "  make db-seed        Load sample data"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linting (backend + frontend)"
	@echo "  make lint-backend   Run backend linting"
	@echo "  make lint-frontend  Run frontend linting"
	@echo "  make format         Format all code"
	@echo "  make type-check     Run type checking"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test           Run all tests"
	@echo "  make test-backend   Run backend tests"
	@echo "  make test-frontend  Run frontend tests"
	@echo "  make test-cov       Run tests with coverage"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build          Build Docker images"
	@echo "  make deploy         Deploy to production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Clean up temporary files"
	@echo "  make clean-all      Remove everything including data"

# Setup Commands
install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✓ Dependencies installed"

setup: install
	@echo "Setting up development environment..."
	cp .env.example .env
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env.local
	docker-compose up -d
	docker-compose exec backend python -m alembic upgrade head
	@echo "✓ Setup complete! Visit http://localhost:3000"

# Runtime Commands
start:
	@echo "Starting services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	@echo "Stopping services..."
	docker-compose down
	@echo "✓ Services stopped"

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Development Commands
dev-backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

dev: dev-backend dev-frontend

# Database Commands
migrate:
	@echo "Running migrations..."
	docker-compose exec backend python -m alembic upgrade head
	@echo "✓ Migrations complete"

migrate-new:
	@echo "Creating new migration: $(msg)"
	docker-compose exec backend python -m alembic revision --autogenerate -m "$(msg)"
	@echo "✓ Migration created. Edit the file in backend/migrations/versions/"

db-seed:
	@echo "Loading sample data..."
	docker-compose exec backend python scripts/seed_data.py
	@echo "✓ Sample data loaded"

# Code Quality
lint: lint-backend lint-frontend
	@echo "✓ Linting complete"

lint-backend:
	@echo "Linting backend..."
	cd backend && black --check app/ || true
	cd backend && flake8 app/ || true

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint || true

format:
	@echo "Formatting code..."
	cd backend && black app/
	cd frontend && npm run format
	@echo "✓ Code formatted"

type-check:
	@echo "Type checking..."
	cd backend && mypy app/ || true
	cd frontend && npm run type-check || true
	@echo "✓ Type checking complete"

# Testing Commands
test: test-backend test-frontend
	@echo "✓ All tests complete"

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest --tb=short
	@echo "✓ Backend tests complete"

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test -- --passWithNoTests
	@echo "✓ Frontend tests complete"

test-cov:
	@echo "Running tests with coverage..."
	cd backend && pytest --cov=app --cov-report=html
	@echo "Coverage report: backend/htmlcov/index.html"

# Build & Deploy
build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✓ Build complete"

build-backend:
	@echo "Building backend image..."
	docker-compose build backend
	@echo "✓ Backend image built"

build-frontend:
	@echo "Building frontend image..."
	docker-compose build frontend
	@echo "✓ Frontend image built"

deploy:
	@echo "Deploying to production..."
	git push
	@echo "✓ Deploy triggered (check CI/CD pipeline)"

# Cleanup Commands
clean:
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name '.next' -delete
	rm -rf frontend/node_modules/.cache
	@echo "✓ Cleanup complete"

clean-all: clean
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf backend/venv frontend/node_modules .env backend/.env frontend/.env.local; \
		echo "✓ Everything cleaned"; \
	else \
		echo "✗ Cancelled"; \
	fi

# Utility Commands
shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

psql:
	docker-compose exec postgres psql -U career_ai_user -d career_ai_db

ps:
	docker-compose ps

status:
	@echo "Service Status:"
	docker-compose ps

ps-all:
	@echo "All Services:"
	docker ps -a

