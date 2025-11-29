# ===========================================
# NeuroCron Makefile
# ===========================================

.PHONY: help install dev build up down restart logs shell db-migrate db-upgrade db-downgrade test lint format clean

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help
	@echo "$(CYAN)NeuroCron - The Autonomous Marketing Brain$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ===========================================
# Development
# ===========================================

install: ## Install all dependencies
	@echo "$(CYAN)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(CYAN)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)Dependencies installed!$(NC)"

dev: ## Start development environment
	@echo "$(CYAN)Starting development environment...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "Frontend: http://localhost:3100"
	@echo "Backend API: http://localhost:8100"
	@echo "API Docs: http://localhost:8100/docs"

dev-backend: ## Start backend in development mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8100

dev-frontend: ## Start frontend in development mode
	cd frontend && npm run dev

# ===========================================
# Docker
# ===========================================

build: ## Build all Docker images
	@echo "$(CYAN)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)Build complete!$(NC)"

up: ## Start all services
	@echo "$(CYAN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"

down: ## Stop all services
	@echo "$(CYAN)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: down up ## Restart all services

logs: ## View logs (use service=<name> for specific service)
	docker-compose logs -f $(service)

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

# ===========================================
# Database
# ===========================================

db-create: ## Create database
	@echo "$(CYAN)Creating database...$(NC)"
	docker-compose exec postgres createdb -U neurocron neurocron_db || true
	@echo "$(GREEN)Database created!$(NC)"

db-migrate: ## Create new migration (use msg="migration message")
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade: ## Apply all migrations
	@echo "$(CYAN)Applying migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)Migrations applied!$(NC)"

db-downgrade: ## Rollback last migration
	cd backend && alembic downgrade -1

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(YELLOW)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose exec postgres dropdb -U neurocron neurocron_db || true
	docker-compose exec postgres createdb -U neurocron neurocron_db
	cd backend && alembic upgrade head
	@echo "$(GREEN)Database reset complete!$(NC)"

# ===========================================
# Testing
# ===========================================

test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	cd backend && pytest -v
	cd frontend && npm test
	@echo "$(GREEN)Tests complete!$(NC)"

test-backend: ## Run backend tests
	cd backend && pytest -v --cov=app --cov-report=html

test-frontend: ## Run frontend tests
	cd frontend && npm test

# ===========================================
# Code Quality
# ===========================================

lint: ## Run linters
	@echo "$(CYAN)Running linters...$(NC)"
	cd backend && ruff check .
	cd frontend && npm run lint
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(CYAN)Formatting code...$(NC)"
	cd backend && ruff format .
	cd frontend && npm run format
	@echo "$(GREEN)Formatting complete!$(NC)"

type-check: ## Run type checking
	cd backend && mypy app
	cd frontend && npm run type-check

# ===========================================
# Celery
# ===========================================

celery-worker: ## Start Celery worker
	cd backend && celery -A app.workers.celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	cd backend && celery -A app.workers.celery_app beat --loglevel=info

celery-flower: ## Start Celery Flower monitoring
	cd backend && celery -A app.workers.celery_app flower --port=5555

# ===========================================
# Production
# ===========================================

prod-build: ## Build for production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Start production environment
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-deploy: ## Deploy to production
	@echo "$(CYAN)Deploying to production...$(NC)"
	git pull origin main
	make prod-build
	make prod-up
	make db-upgrade
	@echo "$(GREEN)Deployment complete!$(NC)"

# ===========================================
# Utilities
# ===========================================

clean: ## Clean up build artifacts and caches
	@echo "$(CYAN)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

setup-ssl: ## Setup SSL certificates with Certbot
	certbot --nginx -d neurocron.com -d www.neurocron.com -d api.neurocron.com

generate-secret: ## Generate a secure secret key
	@python -c "import secrets; print(secrets.token_urlsafe(64))"

