# Python CLI Application Makefile
# Composite lint-* targets for clean namespace

.PHONY: help init install activate venv-info lint lint-all lint-security lint-complexity lint-placement lint-full format test test-coverage clean

help: ## Show available targets
	@echo "Available targets:"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  make init              - Initial setup (install deps + show activation instructions)"
	@echo "  make install           - Install/update dependencies"
	@echo "  make activate          - Show command to activate virtualenv"
	@echo "  make venv-info         - Show virtualenv path and activation command"
	@echo ""
	@echo "Linting & Quality:"
	@echo "  make lint              - Fast linting (Ruff)"
	@echo "  make lint-all          - Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)"
	@echo "  make lint-security     - Security scanning (Bandit + Safety + pip-audit)"
	@echo "  make lint-complexity   - Complexity analysis (Radon + Xenon)"
	@echo "  make lint-placement    - File placement linting (dogfooding our own linter)"
	@echo "  make lint-full         - ALL quality checks"
	@echo "  make format            - Auto-fix formatting and linting issues"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             - Clean cache and artifacts"

lint: ## Fast linting (Ruff - use during development)
	@echo "Running fast linting (Ruff)..."
	@poetry run ruff check src/ tests/
	@poetry run ruff format --check src/ tests/

lint-all: ## Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)
	@echo "=== Running Ruff (linter) ==="
	@poetry run ruff check src/ tests/
	@echo "✓ Ruff checks passed"
	@echo ""
	@echo "=== Running Ruff (formatter) ==="
	@poetry run ruff format --check src/ tests/
	@echo "✓ Ruff formatting passed"
	@echo ""
	@echo "=== Running Pylint ==="
	@poetry run pylint src/
	@echo "✓ Pylint passed"
	@echo ""
	@echo "=== Running Flake8 ==="
	@poetry run flake8 src/ tests/
	@echo "✓ Flake8 passed"
	@echo ""
	@echo "=== Running MyPy (type checking) ==="
	@poetry run mypy src/
	@echo "✓ MyPy passed"

lint-security: ## Security scanning (Bandit + Safety + pip-audit)
	@echo ""
	@echo "=== Running Bandit (security linter) ==="
	@poetry run bandit -r src/ -q
	@echo "✓ Bandit passed"
	@echo ""
	@echo "=== Running Safety (dependency vulnerabilities) ==="
	@poetry run safety scan --output json || true
	@echo ""
	@echo "=== Running pip-audit (dependency audit) ==="
	@poetry run pip-audit || true

lint-complexity: ## Complexity analysis (Radon + Xenon)
	@echo ""
	@echo "=== Analyzing code complexity (Radon) ==="
	@poetry run radon cc src/ -a -s
	@poetry run radon mi src/ -s
	@echo ""
	@echo "=== Analyzing complexity (Xenon) - demanding A grade ==="
	@poetry run xenon --max-absolute A --max-modules A --max-average A src/

lint-placement: ## File placement linting (dogfooding our own linter)
	@echo ""
	@echo "=== Running file placement linter (dogfooding) ==="
	@poetry run thai-lint lint file-placement .
	@echo "✓ File placement checks passed"

lint-full: lint-all lint-security lint-complexity lint-placement ## ALL quality checks
	@echo "✅ All linting checks complete!"

format: ## Auto-fix formatting and linting issues
	@poetry run ruff format src/ tests/
	@poetry run ruff check --fix src/ tests/

test: ## Run tests
	@poetry run pytest -v

test-coverage: ## Run tests with coverage
	@poetry run pytest --cov=src --cov-report=term --cov-report=html -v

init: ## Initial setup (install dependencies and show activation instructions)
	@echo "🚀 Setting up thai-lint development environment..."
	@echo ""
	@poetry install
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "📋 Next steps - Choose your preferred workflow:"
	@echo ""
	@echo "Option 1: Activate the virtual environment (Poetry 2.0+)"
	@echo "  source $$(poetry env info --path)/bin/activate"
	@echo "  # Now you can run: thai-lint --help"
	@echo ""
	@echo "Option 2: Use poetry run prefix (no activation)"
	@echo "  poetry run thai-lint --help"
	@echo ""
	@echo "Option 3: Use make targets (easiest, no activation)"
	@echo "  make lint-placement"
	@echo "  make test"
	@echo ""
	@echo "Quick start (copy and paste):"
	@echo "  source $$(poetry env info --path)/bin/activate"
	@echo "  thai-lint lint file-placement ."
	@echo ""

install: ## Install/update dependencies
	@echo "📦 Installing dependencies..."
	@poetry install
	@echo "✓ Dependencies installed"

activate: ## Show command to activate virtualenv
	@echo "To activate the virtual environment, run:"
	@echo ""
	@echo "  source $$(poetry env info --path)/bin/activate"
	@echo ""
	@echo "Or copy and paste this command:"
	@echo ""
	@echo "source $$(poetry env info --path)/bin/activate"

venv-info: ## Show virtualenv path and activation command
	@echo "Virtual Environment Information:"
	@echo ""
	@echo "Virtualenv path:"
	@poetry env info --path
	@echo ""
	@echo "Python version:"
	@poetry env info --python
	@echo ""
	@echo "To activate the virtualenv (Poetry 2.0+):"
	@echo "  source $$(poetry env info --path)/bin/activate"
	@echo ""
	@echo "Once activated, you can run:"
	@echo "  thai-lint --help"
	@echo "  thai-lint lint file-placement ."
	@echo ""
	@echo "To deactivate:"
	@echo "  deactivate"

clean: ## Clean cache and artifacts
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "✓ Cleaned cache and artifacts"
