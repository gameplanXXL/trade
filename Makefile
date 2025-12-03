# Trading Platform - Makefile
# Usage: make start | make stop | make logs | make status

.PHONY: start stop logs status backend frontend db clean help

# Default target
.DEFAULT_GOAL := help

# pnpm path
PNPM_HOME := $(HOME)/.local/share/pnpm
PATH := $(PNPM_HOME):$(PATH)
export PATH

# =============================================================================
# Main Commands
# =============================================================================

## Start all services (stops first if running)
start: stop
	@echo "🚀 Starting Trading Platform..."
	@docker compose up -d postgres redis
	@echo "⏳ Waiting for databases..."
	@sleep 3
	@cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
	@sleep 2
	@cd frontend && $(PNPM_HOME)/pnpm dev --host 0.0.0.0 &
	@echo ""
	@echo "✅ Trading Platform started!"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Health:   http://localhost:8000/health"
	@echo ""
	@echo "Use 'make logs' to view logs or 'make stop' to stop all services"

## Stop all services
stop:
	@echo "🛑 Stopping Trading Platform..."
	@-pkill -f "uvicorn src.main:app" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
	@docker compose stop
	@echo "✅ All services stopped"

## View logs (docker services only)
logs:
	@docker compose logs -f

## Show status of all services
status:
	@echo "📊 Service Status:"
	@echo ""
	@echo "Docker Services:"
	@docker compose ps
	@echo ""
	@echo "Backend (uvicorn):"
	@-pgrep -f "uvicorn src.main:app" > /dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "Frontend (vite):"
	@-pgrep -f "vite" > /dev/null && echo "  ✅ Running" || echo "  ❌ Not running"

# =============================================================================
# Individual Services
# =============================================================================

## Start only database services
db:
	@docker compose up -d postgres redis
	@echo "✅ Database services started"

## Start only backend
backend: db
	@cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

## Start only frontend
frontend:
	@cd frontend && $(PNPM_HOME)/pnpm dev --host 0.0.0.0

# =============================================================================
# Development
# =============================================================================

## Run backend tests
test-backend:
	@cd backend && uv run pytest

## Run frontend tests
test-frontend:
	@cd frontend && $(PNPM_HOME)/pnpm test

## Run all tests
test: test-backend test-frontend

## Run linters
lint:
	@echo "🔍 Linting backend..."
	@cd backend && uv run ruff check src/
	@echo "🔍 Linting frontend..."
	@cd frontend && $(PNPM_HOME)/pnpm lint

## Clean up (remove containers, volumes, node_modules)
clean: stop
	@echo "🧹 Cleaning up..."
	@docker compose down -v
	@rm -rf frontend/node_modules frontend/dist
	@rm -rf backend/.venv
	@echo "✅ Cleanup complete"

# =============================================================================
# Help
# =============================================================================

## Show this help
help:
	@echo "Trading Platform - Available Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //' | while read line; do \
		target=$$(echo "$$line" | head -1); \
		echo "  make $$(grep -B1 "^## $$target" $(MAKEFILE_LIST) | head -1 | sed 's/:.*//') - $$target"; \
	done 2>/dev/null || true
	@echo ""
	@echo "Main commands:"
	@echo "  make start   - Start all services (backend, frontend, databases)"
	@echo "  make stop    - Stop all services"
	@echo "  make status  - Show status of all services"
	@echo "  make logs    - View docker logs"
	@echo ""
	@echo "Individual services:"
	@echo "  make backend  - Start only backend"
	@echo "  make frontend - Start only frontend"
	@echo "  make db       - Start only databases"
	@echo ""
	@echo "Development:"
	@echo "  make test    - Run all tests"
	@echo "  make lint    - Run linters"
	@echo "  make clean   - Clean up everything"
