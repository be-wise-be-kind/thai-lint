# Python CLI Application Makefile
# Composite lint-* targets for clean namespace
#
# Usage:
#   make lint              - Lint all files in src/ and tests/
#   make lint FILES=...    - Lint specific files
#   make lint-full         - Full linting on all files
#   make lint-full FILES=changed  - Full linting on changed files only (for pre-commit)

.PHONY: help init install activate venv-info lint lint-all lint-security lint-complexity lint-placement lint-solid lint-nesting lint-dry clean-cache lint-full format test test-coverage clean get-changed-files publish-pypi publish-docker publish update-version-badges bump-version show-version

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
	@echo "  make lint-complexity   - Complexity analysis (Radon + Xenon + Nesting)"
	@echo "  make lint-complexity FILES=... - Complexity analysis on specific files"
	@echo "  make lint-placement    - File placement linting (dogfooding our own linter)"
	@echo "  make lint-placement FILES=...  - File placement linting on specific files"
	@echo "  make lint-solid        - SOLID principle linting (SRP)"
	@echo "  make lint-solid FILES=...      - SOLID principle linting on specific files"
	@echo "  make lint-dry          - DRY principle linting (duplicate code detection)"
	@echo "  make clean-cache       - Clear DRY linter cache"
	@echo "  make lint-full         - ALL quality checks (includes lint-dry as of PR4)"
	@echo "  make lint-full FILES=changed   - ALL quality checks on changed files (pre-commit)"
	@echo "  make format            - Auto-fix formatting and linting issues"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             - Clean cache and artifacts"
	@echo ""
	@echo "Versioning:"
	@echo "  make show-version      - Show current version"
	@echo "  make bump-version      - Interactive version bump with validation"
	@echo ""
	@echo "Publishing:"
	@echo "  make publish-pypi      - Publish to PyPI (after tests, linting, and version bump)"
	@echo "  make publish-docker    - Publish to Docker Hub (after tests, linting, and version bump)"
	@echo "  make publish           - Publish to both PyPI and Docker Hub"

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

lint-complexity: ## Complexity analysis (Radon + Xenon + Nesting)
	@echo ""
	@echo "=== Analyzing code complexity (Radon) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run radon cc $(SRC_TARGETS) -a -s; \
		poetry run radon mi $(SRC_TARGETS) -s; \
	fi
	@echo ""
	@echo "=== Analyzing complexity (Xenon) - demanding A grade ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run xenon --max-absolute A --max-modules A --max-average A --exclude 'src/linters/srp/linter.py' $(SRC_TARGETS); \
	fi
	@echo ""
	@echo "=== Running nesting depth linter (dogfooding) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run thai-lint nesting $(SRC_TARGETS) --config .thailint.yaml; \
		echo "✓ Nesting depth checks passed"; \
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

lint-solid: ## SOLID principle linting (SRP)
	@echo ""
	@echo "=== Running SRP linter (dogfooding) ==="
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run thai-lint srp $(SRC_TARGETS) --config .thailint.yaml; \
		echo "✓ SRP checks passed"; \
	fi
	@echo "✅ SOLID principle checks complete!"

lint-dry: ## DRY principle linting (duplicate code detection) - opt-in for performance
	@echo ""
	@echo "=== Running DRY linter (duplicate code detection) ==="
	@echo "Note: This may take several minutes on large codebases (first run)"
	@if [ -n "$(SRC_TARGETS)" ]; then \
		poetry run thai-lint dry $(SRC_TARGETS) --config .thailint.yaml; \
		echo "✓ DRY checks passed"; \
	fi
	@echo "✅ DRY principle checks complete!"

clean-cache: ## Clear DRY linter cache
	@echo "Clearing DRY linter cache..."
	@rm -rf .thailint-cache/
	@echo "✓ Cache cleared"

lint-full: lint-all lint-security lint-complexity lint-placement lint-solid lint-dry ## ALL quality checks (includes lint-dry as of PR4)
	@echo "✅ All linting checks complete (including DRY)!"

format: ## Auto-fix formatting and linting issues
	@poetry run ruff format src/ tests/
	@poetry run ruff check --fix src/ tests/

test: ## Run tests
	@poetry run pytest -v

test-coverage: ## Run tests with coverage
	@poetry run pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml -v

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

show-version: ## Show current version from pyproject.toml
	@VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	echo "Current version: $$VERSION"

bump-version: ## Interactive version bump with validation
	@echo "=========================================="
	@echo "Version Bump"
	@echo "=========================================="
	@echo ""
	@CURRENT_VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	echo "Current version: $$CURRENT_VERSION"; \
	echo ""; \
	echo "Enter new version (semver format: major.minor.patch):"; \
	read -r NEW_VERSION; \
	echo ""; \
	if [ -z "$$NEW_VERSION" ]; then \
		echo "❌ Version cannot be empty!"; \
		exit 1; \
	fi; \
	if ! echo "$$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$$'; then \
		echo "❌ Invalid version format! Must be semver (e.g., 1.2.3)"; \
		exit 1; \
	fi; \
	echo "Updating version from $$CURRENT_VERSION to $$NEW_VERSION"; \
	echo ""; \
	echo "Confirm update? [y/N]"; \
	read -r CONFIRM; \
	if [ "$$CONFIRM" != "y" ] && [ "$$CONFIRM" != "Y" ]; then \
		echo "❌ Version update cancelled"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Updating pyproject.toml..."; \
	sed -i "s/^version = \"$$CURRENT_VERSION\"/version = \"$$NEW_VERSION\"/" pyproject.toml; \
	if [ $$? -ne 0 ]; then \
		echo "❌ Failed to update pyproject.toml!"; \
		exit 1; \
	fi; \
	echo "✓ Updated pyproject.toml"; \
	echo ""; \
	echo "Reinstalling package with new version..."; \
	poetry install --quiet; \
	if [ $$? -ne 0 ]; then \
		echo "❌ Failed to reinstall package!"; \
		echo "Reverting version change..."; \
		sed -i "s/^version = \"$$NEW_VERSION\"/version = \"$$CURRENT_VERSION\"/" pyproject.toml; \
		exit 1; \
	fi; \
	echo "✓ Package reinstalled"; \
	echo ""; \
	VERIFIED_VERSION=$$(poetry run python -c "from src import __version__; print(__version__)"); \
	if [ "$$VERIFIED_VERSION" = "$$NEW_VERSION" ]; then \
		echo "✅ Version successfully updated to $$NEW_VERSION"; \
		echo ""; \
		echo "Next steps:"; \
		echo "  1. Review the change: git diff pyproject.toml"; \
		echo "  2. Commit the version bump: git commit -am 'chore: Bump version to $$NEW_VERSION'"; \
		echo "  3. Publish: make publish"; \
	else \
		echo "❌ Version verification failed!"; \
		echo "   Expected: $$NEW_VERSION"; \
		echo "   Got: $$VERIFIED_VERSION"; \
		exit 1; \
	fi

update-version-badges: ## Update version badges in README.md
	@echo "Updating version badges in README.md..."
	@VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	sed -i "s|!\[Version\](https://img.shields.io/badge/version-.*-blue)|![Version](https://img.shields.io/badge/version-$$VERSION-blue)|g" README.md || true
	@echo "✓ Version badges updated"

publish-pypi: ## Publish to PyPI (runs tests, linting, and version bump first)
	@echo "=========================================="
	@echo "Publishing to PyPI"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Running tests..."
	@make test
	@if [ $$? -ne 0 ]; then \
		echo "❌ Tests failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Tests passed"
	@echo ""
	@echo "Step 2: Running full linting..."
	@make lint-full
	@if [ $$? -ne 0 ]; then \
		echo "❌ Linting failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Linting passed"
	@echo ""
	@echo "Step 3: Version bump..."
	@make bump-version
	@if [ $$? -ne 0 ]; then \
		echo "❌ Version bump cancelled or failed!"; \
		exit 1; \
	fi
	@echo ""
	@make _publish-pypi-only

_publish-pypi-only: ## Internal: Publish to PyPI without running tests/linting
	@echo "=========================================="
	@echo "Publishing to PyPI"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Updating version badges..."
	@make update-version-badges
	@echo ""
	@echo "Step 2: Updating lock file..."
	@poetry lock
	@echo "✓ Lock file updated"
	@echo ""
	@echo "Step 3: Cleaning previous builds..."
	@rm -rf dist/ build/ *.egg-info
	@echo "✓ Previous builds cleaned"
	@echo ""
	@echo "Step 4: Building package..."
	@poetry build
	@if [ $$? -ne 0 ]; then \
		echo "❌ Build failed!"; \
		exit 1; \
	fi
	@echo "✓ Package built successfully"
	@echo ""
	@echo "Step 5: Publishing to PyPI..."
	@if [ -f .env ]; then \
		export $$(cat .env | grep PYPI_API_TOKEN | xargs) && \
		poetry config pypi-token.pypi $$PYPI_API_TOKEN && \
		poetry publish; \
	else \
		echo "❌ .env file not found! Cannot read PYPI_API_TOKEN."; \
		exit 1; \
	fi
	@if [ $$? -eq 0 ]; then \
		VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
		echo ""; \
		echo "✅ Successfully published to PyPI!"; \
		echo ""; \
		echo "Package: thailint"; \
		echo "Version: $$VERSION"; \
		echo "URL: https://pypi.org/project/thailint/$$VERSION/"; \
		echo ""; \
		echo "To install: pip install thailint==$$VERSION"; \
	else \
		echo "❌ Publishing to PyPI failed!"; \
		exit 1; \
	fi

publish-docker: ## Publish to Docker Hub (runs tests, linting, and version bump first)
	@echo "=========================================="
	@echo "Publishing to Docker Hub"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Running tests..."
	@make test
	@if [ $$? -ne 0 ]; then \
		echo "❌ Tests failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Tests passed"
	@echo ""
	@echo "Step 2: Running full linting..."
	@make lint-full
	@if [ $$? -ne 0 ]; then \
		echo "❌ Linting failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Linting passed"
	@echo ""
	@echo "Step 3: Version bump..."
	@make bump-version
	@if [ $$? -ne 0 ]; then \
		echo "❌ Version bump cancelled or failed!"; \
		exit 1; \
	fi
	@echo ""
	@make _publish-docker-only

_publish-docker-only: ## Internal: Publish to Docker Hub without running tests/linting
	@echo "=========================================="
	@echo "Publishing to Docker Hub"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Updating version badges..."
	@make update-version-badges
	@echo ""
	@echo "Step 2: Updating lock file..."
	@poetry lock
	@echo "✓ Lock file updated"
	@echo ""
	@echo "Step 3: Loading Docker Hub credentials..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found! Cannot read Docker Hub credentials."; \
		exit 1; \
	fi
	@export $$(cat .env | grep DOCKERHUB_USERNAME | xargs) && \
	export $$(cat .env | grep DOCKERHUB_TOKEN | xargs) && \
	VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2) && \
	echo "✓ Credentials loaded" && \
	echo "" && \
	echo "Step 4: Logging into Docker Hub..." && \
	echo $$DOCKERHUB_TOKEN | docker login -u $$DOCKERHUB_USERNAME --password-stdin && \
	if [ $$? -ne 0 ]; then \
		echo "❌ Docker Hub login failed!"; \
		exit 1; \
	fi && \
	echo "✓ Logged into Docker Hub" && \
	echo "" && \
	echo "Step 5: Building Docker image..." && \
	docker build -t $$DOCKERHUB_USERNAME/thailint:$$VERSION -t $$DOCKERHUB_USERNAME/thailint:latest . && \
	if [ $$? -ne 0 ]; then \
		echo "❌ Docker build failed!"; \
		exit 1; \
	fi && \
	echo "✓ Docker image built" && \
	echo "" && \
	echo "Step 6: Pushing to Docker Hub..." && \
	docker push $$DOCKERHUB_USERNAME/thailint:$$VERSION && \
	docker push $$DOCKERHUB_USERNAME/thailint:latest && \
	if [ $$? -eq 0 ]; then \
		echo ""; \
		echo "✅ Successfully published to Docker Hub!"; \
		echo ""; \
		echo "Image: $$DOCKERHUB_USERNAME/thailint"; \
		echo "Tags: $$VERSION, latest"; \
		echo "URL: https://hub.docker.com/r/$$DOCKERHUB_USERNAME/thailint"; \
		echo ""; \
		echo "To pull: docker pull $$DOCKERHUB_USERNAME/thailint:$$VERSION"; \
		echo "To pull: docker pull $$DOCKERHUB_USERNAME/thailint:latest"; \
	else \
		echo "❌ Publishing to Docker Hub failed!"; \
		exit 1; \
	fi

publish: ## Publish to both PyPI and Docker Hub
	@echo "=========================================="
	@echo "Publishing to PyPI and Docker Hub"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Running tests..."
	@make test
	@if [ $$? -ne 0 ]; then \
		echo "❌ Tests failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Tests passed"
	@echo ""
	@echo "Step 2: Running full linting..."
	@make lint-full
	@if [ $$? -ne 0 ]; then \
		echo "❌ Linting failed! Cannot publish."; \
		exit 1; \
	fi
	@echo "✓ Linting passed"
	@echo ""
	@echo "Step 3: Version bump..."
	@make bump-version
	@if [ $$? -ne 0 ]; then \
		echo "❌ Version bump cancelled or failed!"; \
		exit 1; \
	fi
	@echo ""
	@make _publish-pypi-only
	@if [ $$? -ne 0 ]; then \
		echo "❌ PyPI publishing failed! Stopping."; \
		exit 1; \
	fi
	@echo ""
	@make _publish-docker-only
	@if [ $$? -ne 0 ]; then \
		echo "❌ Docker Hub publishing failed!"; \
		exit 1; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✅ Publishing Complete!"
	@echo "=========================================="
	@VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	DOCKERHUB_USERNAME=$$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2); \
	echo ""; \
	echo "Published version: $$VERSION"; \
	echo ""; \
	echo "PyPI: https://pypi.org/project/thailint/$$VERSION/"; \
	echo "Docker Hub: https://hub.docker.com/r/$$DOCKERHUB_USERNAME/thailint"; \
	echo ""; \
	echo "Installation:"; \
	echo "  pip install thailint==$$VERSION"; \
	echo "  docker pull $$DOCKERHUB_USERNAME/thailint:$$VERSION"
