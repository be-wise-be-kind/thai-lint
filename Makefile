# Python CLI Application Makefile
# Composite lint-* targets for clean namespace
#
# Usage:
#   make lint              - Lint all files in src/ and tests/
#   make lint FILES=...    - Lint specific files
#   make lint-full         - Full linting on all files
#   make lint-full FILES=changed  - Full linting on changed files only (for pre-commit)

.PHONY: help init install activate venv-info lint lint-all lint-security lint-complexity lint-placement lint-nesting lint-full format test test-coverage clean get-changed-files

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
	@echo "  make lint FILES=...    - Fast linting on specific files"
	@echo "  make lint-all          - Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)"
	@echo "  make lint-all FILES=...        - Comprehensive linting on specific files"
	@echo "  make lint-security     - Security scanning (Bandit + Safety + pip-audit)"
	@echo "  make lint-security FILES=...   - Security scanning on specific files"
	@echo "  make lint-complexity   - Complexity analysis (Radon + Xenon)"
	@echo "  make lint-complexity FILES=... - Complexity analysis on specific files"
	@echo "  make lint-placement    - File placement linting (dogfooding our own linter)"
	@echo "  make lint-placement FILES=...  - File placement linting on specific files"
	@echo "  make lint-nesting      - Nesting depth linting (dogfooding our own linter)"
	@echo "  make lint-nesting FILES=...    - Nesting depth linting on specific files"
	@echo "  make lint-full         - ALL quality checks"
	@echo "  make lint-full FILES=changed   - ALL quality checks on changed files (pre-commit)"
	@echo "  make format            - Auto-fix formatting and linting issues"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             - Clean cache and artifacts"

# Determine which files to lint based on FILES parameter
# Default: src/ tests/ (all files)
# FILES=changed: only staged files
# FILES=<paths>: specific files/directories
ifeq ($(FILES),changed)
    PYTHON_FILES := $(shell git diff --cached --name-only --diff-filter=ACM | grep -E "^(src|tests)/.*\.py$$" || true)
    PYTHON_SRC_FILES := $(shell git diff --cached --name-only --diff-filter=ACM | grep -E "^src/.*\.py$$" || true)
    ALL_CHANGED_FILES := $(shell git diff --cached --name-only --diff-filter=ACM || true)
    TARGETS := $(PYTHON_FILES)
    SRC_TARGETS := $(PYTHON_SRC_FILES)
    PLACEMENT_TARGETS := $(ALL_CHANGED_FILES)
else ifdef FILES
    TARGETS := $(FILES)
    SRC_TARGETS := $(filter src/%,$(FILES))
    PLACEMENT_TARGETS := $(FILES)
else
    TARGETS := src/ tests/
    SRC_TARGETS := src/
    PLACEMENT_TARGETS := .
endif

lint: ## Fast linting (Ruff - use during development)
	@echo "Running fast linting (Ruff)..."
	@if [ -n "$(TARGETS)" ]; then \
		poetry run ruff check $(TARGETS) && \
		poetry run ruff format --check $(TARGETS); \
	else \
		echo "No files to lint"; \
	fi

lint-all: ## Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)
	@echo "=== Running Ruff (linter) ==="
	@if [ -n "$(TARGETS)" ]; then \
		poetry run ruff check $(TARGETS); \
		echo "✓ Ruff checks passed"; \
	fi
	@echo ""
	@echo "=== Running Ruff (formatter) ==="
	@if [ -n "$(TARGETS)" ]; then \
		poetry run ruff format --check $(TARGETS); \
		echo "✓ Ruff formatting passed"; \
	fi
	@echo ""
	@echo "=== Running Pylint ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run pylint $(SRC_TARGETS); \
		echo "✓ Pylint passed"; \
	fi
	@echo ""
	@echo "=== Running Flake8 ==="
	@if [ -n "$(TARGETS)" ]; then \
		poetry run flake8 $(TARGETS); \
		echo "✓ Flake8 passed"; \
	fi
	@echo ""
	@echo "=== Running MyPy (type checking) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run mypy $(SRC_TARGETS); \
		echo "✓ MyPy passed"; \
	fi

lint-security: ## Security scanning (Bandit + pip-audit)
	@echo ""
	@echo "=== Running Bandit (security linter) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run bandit -r $(SRC_TARGETS) -q; \
		echo "✓ Bandit passed"; \
	fi
ifeq ($(FILES),)
	@echo ""
	@echo "=== Running pip-audit (dependency audit) ==="
	@poetry run pip-audit || true
endif

lint-dependencies: ## Check dependencies for vulnerabilities (Safety - requires API)
	@echo ""
	@echo "=== Running Safety (dependency vulnerabilities) ==="
	@echo "Note: This requires network access to Safety API and may be slow"
	@poetry run safety scan --output json || true

lint-complexity: ## Complexity analysis (Radon + Xenon)
	@echo ""
	@echo "=== Analyzing code complexity (Radon) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run radon cc $(SRC_TARGETS) -a -s; \
		poetry run radon mi $(SRC_TARGETS) -s; \
	fi
	@echo ""
	@echo "=== Analyzing complexity (Xenon) - demanding A grade ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run xenon --max-absolute A --max-modules A --max-average A $(SRC_TARGETS); \
	fi

lint-placement: ## File placement linting (dogfooding our own linter)
	@echo ""
	@echo "=== Running file placement linter (dogfooding) ==="
	@if [ -n "$(PLACEMENT_TARGETS)" ]; then \
		poetry run thai-lint file-placement $(PLACEMENT_TARGETS); \
		echo "✓ File placement checks passed"; \
	fi

lint-nesting: ## Nesting depth linting (dogfooding our own linter)
	@echo ""
	@echo "=== Running nesting depth linter (dogfooding) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run thai-lint nesting $(SRC_TARGETS) --config .thailint.yaml; \
		echo "✓ Nesting depth checks passed"; \
	fi

lint-full: lint-all lint-security lint-complexity lint-placement lint-nesting ## ALL quality checks
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
	@echo "  thai-lint file-placement ."
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
	@echo "  thai-lint file-placement ."
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
