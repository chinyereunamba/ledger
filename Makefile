.PHONY: dev install clean api frontend help docker-build docker-up docker-down docker-logs test lint format

# Default target
dev: ## Run both API and frontend servers
	@echo "🚀 Starting QuickLedger development servers..."
	@make -j2 api frontend

api: ## Run the FastAPI backend server
	@echo "🔧 Starting API server on http://localhost:8000"
	@cd src/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run the frontend development server
	@echo "🌐 Starting frontend server on http://localhost:3000"
	@cd frontend && python3 -m http.server 3000

install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt

install-poetry: ## Install dependencies using Poetry
	@echo "📦 Installing dependencies with Poetry..."
	@poetry install

test: ## Run test suite
	@echo "🧪 Running tests..."
	@pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	@pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	@echo "🔍 Running linters..."
	@ruff check src/ tests/ || true
	@echo "✅ Linting complete"

format: ## Format code
	@echo "✨ Formatting code..."
	@black src/ tests/ scripts/*.py || true
	@ruff format src/ tests/ scripts/*.py || true
	@echo "✅ Formatting complete"

clean: ## Clean up cache files
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" ! -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" ! -path "./.venv/*" -delete 2>/dev/null || true
	@find . -name "*.pyo" ! -path "./.venv/*" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	@docker-compose -f docker/docker-compose.yml build

docker-up: ## Start Docker containers
	@echo "🐳 Starting Docker containers..."
	@docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop Docker containers
	@echo "🐳 Stopping Docker containers..."
	@docker-compose -f docker/docker-compose.yml down

docker-logs: ## View Docker logs
	@docker-compose -f docker/docker-compose.yml logs -f

help: ## Show this help message
	@echo "QuickLedger Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
