# Python CLI Application Makefile
# Composite lint-* targets for clean namespace

.PHONY: help lint lint-all lint-security lint-complexity lint-full format test test-coverage install clean

help: ## Show available targets
	@echo "Available targets:"
	@echo "  make lint              - Fast linting (Ruff)"
	@echo "  make lint-all          - Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)"
	@echo "  make lint-security     - Security scanning (Bandit + Safety + pip-audit)"
	@echo "  make lint-complexity   - Complexity analysis (Radon + Xenon)"
	@echo "  make lint-full         - ALL quality checks"
	@echo "  make format            - Auto-fix formatting and linting issues"
	@echo "  make test              - Run tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo "  make install           - Install dependencies"
	@echo "  make clean             - Clean cache and artifacts"

lint: ## Fast linting (Ruff - use during development)
	@echo "Running fast linting (Ruff)..."
	@poetry run ruff check src/ tests/
	@poetry run ruff format --check src/ tests/

lint-all: ## Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)
	@echo "Running comprehensive linting..."
	@poetry run ruff check src/ tests/
	@poetry run ruff format --check src/ tests/
	@poetry run pylint src/
	@poetry run flake8 src/ tests/
	@poetry run mypy src/

lint-security: ## Security scanning (Bandit + Safety + pip-audit)
	@echo "Running security scans..."
	@poetry run bandit -r src/ -q
	@poetry run safety check --json || true
	@poetry run pip-audit || true

lint-complexity: ## Complexity analysis (Radon + Xenon)
	@echo "Analyzing code complexity..."
	@poetry run radon cc src/ -a -s
	@poetry run radon mi src/ -s
	@poetry run xenon --max-absolute B --max-modules B --max-average A src/

lint-full: lint-all lint-security lint-complexity ## ALL quality checks
	@echo "✅ All linting checks complete!"

format: ## Auto-fix formatting and linting issues
	@poetry run ruff format src/ tests/
	@poetry run ruff check --fix src/ tests/

test: ## Run tests
	@poetry run pytest -v

test-coverage: ## Run tests with coverage
	@poetry run pytest --cov=src --cov-report=term --cov-report=html -v

install: ## Install dependencies
	@poetry install

clean: ## Clean cache and artifacts
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "✓ Cleaned cache and artifacts"
