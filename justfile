# Python CLI Application Justfile
# Composite lint-* recipes for clean namespace
#
# Usage:
#   just lint              - Lint all files in src/ and tests/
#   just lint file1 file2  - Lint specific files
#   just lint-full         - Full linting on all files
#   just lint-full changed - Full linting on changed files only (for pre-commit)

# Colors for output
RED := '\033[0;31m'
GREEN := '\033[0;32m'
BLUE := '\033[0;34m'
YELLOW := '\033[1;33m'
NC := '\033[0m' # No Color
BOLD := '\033[1m'

# Default recipe (shows help)
default:
    @just --list

# Show available recipes with descriptions
help:
    @echo "Available recipes:"
    @echo ""
    @echo "Setup & Environment:"
    @echo "  just init              - Initial setup (install deps + show activation instructions)"
    @echo "  just install           - Install/update dependencies"
    @echo "  just activate          - Show command to activate virtualenv"
    @echo "  just venv-info         - Show virtualenv path and activation command"
    @echo ""
    @echo "Linting & Quality:"
    @echo "  just lint [FILES...]           - Fast linting (Ruff)"
    @echo "  just lint-all [FILES...]       - Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)"
    @echo "  just lint-security [FILES...]  - Security scanning (Bandit + Safety + pip-audit)"
    @echo "  just lint-complexity [FILES...] - Complexity analysis (Radon + Xenon + Nesting)"
    @echo "  just lint-placement [PATH]     - File placement linting (dogfooding our own linter)"
    @echo "  just lint-solid [FILES...]     - SOLID principle linting (SRP)"
    @echo "  just lint-dry                  - DRY principle linting (duplicate code detection)"
    @echo "  just clean-cache               - Clear DRY linter cache"
    @echo "  just lint-full [FILES...]      - ALL quality checks (includes lint-dry as of PR4)"
    @echo "  just format                    - Auto-fix formatting and linting issues"
    @echo ""
    @echo "Testing:"
    @echo "  just test              - Run tests"
    @echo "  just test-coverage     - Run tests with coverage"
    @echo ""
    @echo "Maintenance:"
    @echo "  just clean             - Clean cache and artifacts"
    @echo ""
    @echo "Versioning:"
    @echo "  just show-version      - Show current version"
    @echo "  just bump-version      - Interactive version bump with validation"
    @echo ""
    @echo "Publishing:"
    @echo "  just publish-pypi      - Publish to PyPI (after tests, linting, and version bump)"
    @echo "  just publish-docker    - Publish to Docker Hub (after tests, linting, and version bump)"
    @echo "  just publish           - Publish to both PyPI and Docker Hub"

# Get list of Python files to lint
_get-targets +files="src/ tests/":
    #!/usr/bin/env bash
    if [ "{{files}}" = "changed" ]; then
        git diff --cached --name-only --diff-filter=ACM | grep -E "^(src|tests)/.*\.py$" || echo ""
    else
        echo "{{files}}"
    fi

# Get list of Python source files
_get-src-targets +files="src/ tests/":
    #!/usr/bin/env bash
    if [ "{{files}}" = "changed" ]; then
        git diff --cached --name-only --diff-filter=ACM | grep -E "^src/.*\.py$" || echo ""
    elif [ "{{files}}" = "src/ tests/" ]; then
        echo "src/"
    else
        echo "{{files}}" | tr ' ' '\n' | grep -E "^src/" || echo ""
    fi

# Get list of all changed files for placement linting
_get-placement-target files=".":
    #!/usr/bin/env bash
    if [ "{{files}}" = "changed" ]; then
        # For changed files, just use current directory
        echo "."
    else
        # Take the first file/directory only
        echo "{{files}}" | awk '{print $1}'
    fi

# Fast linting (Ruff - use during development)
lint +files="src/ tests/":
    @echo "{{BLUE}}{{BOLD}}▶ Running fast linting (Ruff)...{{NC}}"
    @TARGETS=$(just _get-targets {{files}}); \
    if [ -n "$TARGETS" ]; then \
        poetry run ruff check $TARGETS && \
        poetry run ruff format --check $TARGETS; \
    else \
        echo "{{YELLOW}}⚠ No files to lint{{NC}}"; \
    fi

# Comprehensive linting (Ruff + Pylint + Flake8 + MyPy)
lint-all +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  COMPREHENSIVE LINTING{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @echo "{{BOLD}}[1/5] Ruff (linter){{NC}}"
    @TARGETS=$(just _get-targets {{files}}); \
    if [ -n "$TARGETS" ]; then \
        if poetry run ruff check $TARGETS 2>&1; then \
            echo "{{GREEN}}✓ Ruff checks passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Ruff checks failed{{NC}}"; \
            exit 1; \
        fi \
    fi
    @echo ""
    @echo "{{BOLD}}[2/5] Ruff (formatter){{NC}}"
    @TARGETS=$(just _get-targets {{files}}); \
    if [ -n "$TARGETS" ]; then \
        if poetry run ruff format --check $TARGETS 2>&1; then \
            echo "{{GREEN}}✓ Ruff formatting passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Ruff formatting failed{{NC}}"; \
            exit 1; \
        fi \
    fi
    @echo ""
    @echo "{{BOLD}}[3/5] Pylint{{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run pylint $SRC_TARGETS 2>&1; then \
            echo "{{GREEN}}✓ Pylint passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Pylint failed{{NC}}"; \
            exit 1; \
        fi \
    fi
    @echo ""
    @echo "{{BOLD}}[4/5] Flake8{{NC}}"
    @TARGETS=$(just _get-targets {{files}}); \
    if [ -n "$TARGETS" ]; then \
        if poetry run flake8 $TARGETS 2>&1; then \
            echo "{{GREEN}}✓ Flake8 passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Flake8 failed{{NC}}"; \
            exit 1; \
        fi \
    fi
    @echo ""
    @echo "{{BOLD}}[5/5] MyPy (type checking){{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run mypy $SRC_TARGETS 2>&1; then \
            echo "{{GREEN}}✓ MyPy passed{{NC}}"; \
        else \
            echo "{{RED}}✗ MyPy failed{{NC}}"; \
            exit 1; \
        fi \
    fi

# Security scanning (Bandit + pip-audit)
lint-security +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  SECURITY SCANNING{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @echo "{{BOLD}}[1/2] Bandit (security linter){{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run bandit -r $SRC_TARGETS -q 2>&1; then \
            echo "{{GREEN}}✓ Bandit passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Bandit failed{{NC}}"; \
            exit 1; \
        fi \
    fi
    @if [ "{{files}}" = "src/ tests/" ]; then \
        echo ""; \
        echo "{{BOLD}}[2/2] pip-audit (dependency audit){{NC}}"; \
        if poetry run pip-audit 2>&1; then \
            echo "{{GREEN}}✓ pip-audit passed{{NC}}"; \
        else \
            echo "{{YELLOW}}⚠ pip-audit found issues (non-blocking){{NC}}"; \
        fi \
    fi

# Check dependencies for vulnerabilities (Safety - requires API)
lint-dependencies:
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  DEPENDENCY VULNERABILITIES{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @echo "{{YELLOW}}Note: This requires network access to Safety API and may be slow{{NC}}"
    @poetry run safety scan --output json || true

# Complexity analysis (Radon + Xenon + Nesting)
lint-complexity +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  COMPLEXITY ANALYSIS{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @echo "{{BOLD}}[1/3] Radon (cyclomatic complexity){{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        poetry run radon cc $SRC_TARGETS -a -s 2>&1 | grep -E '(^[^ ]|Average complexity)' || true; \
    fi
    @echo ""
    @echo "{{BOLD}}[2/3] Xenon (complexity enforcement - A grade required){{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run xenon --max-absolute A --max-modules A --max-average A $SRC_TARGETS 2>&1; then \
            echo "{{GREEN}}✓ All code is A-grade{{NC}}"; \
        else \
            echo "{{RED}}✗ Xenon found code below A-grade{{NC}}"; \
            exit 1; \
        fi \
    fi
    @echo ""
    @echo "{{BOLD}}[3/3] Nesting depth{{NC}}"
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run thai-lint nesting $SRC_TARGETS --config .thailint.yaml 2>&1; then \
            echo "{{GREEN}}✓ Nesting depth checks passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Nesting depth checks failed{{NC}}"; \
            exit 1; \
        fi \
    fi

# File placement linting (dogfooding our own linter)
lint-placement path=".":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  FILE PLACEMENT{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @PLACEMENT_TARGET=$(just _get-placement-target {{path}}); \
    if poetry run thai-lint file-placement $PLACEMENT_TARGET 2>&1; then \
        echo "{{GREEN}}✓ File placement checks passed{{NC}}"; \
    else \
        echo "{{RED}}✗ File placement checks failed{{NC}}"; \
        exit 1; \
    fi

# Nesting depth linting (dogfooding our own linter)
lint-nesting +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  NESTING DEPTH{{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run thai-lint nesting $SRC_TARGETS --config .thailint.yaml 2>&1; then \
            echo "{{GREEN}}✓ Nesting depth checks passed{{NC}}"; \
        else \
            echo "{{RED}}✗ Nesting depth checks failed{{NC}}"; \
            exit 1; \
        fi \
    fi

# SOLID principle linting (SRP)
lint-solid +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  SOLID PRINCIPLES (SRP){{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run thai-lint srp $SRC_TARGETS --config .thailint.yaml 2>&1; then \
            echo "{{GREEN}}✓ SRP checks passed{{NC}}"; \
        else \
            echo "{{RED}}✗ SRP checks failed{{NC}}"; \
            exit 1; \
        fi \
    fi

# DRY principle linting (duplicate code detection) - opt-in for performance
lint-dry +files="src/ tests/":
    @echo ""
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo "{{BOLD}}  DRY PRINCIPLES (Duplicate Detection){{NC}}"
    @echo "{{BLUE}}{{BOLD}}════════════════════════════════════════════════════════════{{NC}}"
    @echo ""
    @echo "{{YELLOW}}Note: This may take several minutes on large codebases (first run){{NC}}"
    @echo ""
    @SRC_TARGETS=$(just _get-src-targets {{files}}); \
    if [ -n "$SRC_TARGETS" ]; then \
        if poetry run thai-lint dry $SRC_TARGETS --config .thailint.yaml 2>&1; then \
            echo "{{GREEN}}✓ DRY checks passed{{NC}}"; \
        else \
            echo "{{RED}}✗ DRY checks failed{{NC}}"; \
            exit 1; \
        fi \
    fi

# Clear DRY linter cache
clean-cache:
    @echo "{{BLUE}}Clearing DRY linter cache...{{NC}}"
    @rm -rf .thailint-cache/
    @echo "{{GREEN}}✓ Cache cleared{{NC}}"

# ALL quality checks (includes lint-dry as of PR4)
lint-full +files="src/ tests/":
    #!/usr/bin/env bash
    set -e

    # Track results
    PASSED=()
    FAILED=()

    echo ""
    echo -e "{{BLUE}}{{BOLD}}╔════════════════════════════════════════════════════════════╗{{NC}}"
    echo -e "{{BOLD}}║                  FULL QUALITY CHECK                        ║{{NC}}"
    echo -e "{{BLUE}}{{BOLD}}╚════════════════════════════════════════════════════════════╝{{NC}}"

    # Run each linter and track results
    echo ""
    if just lint-all {{files}}; then
        PASSED+=("Comprehensive Linting")
    else
        FAILED+=("Comprehensive Linting")
    fi

    echo ""
    if just lint-security {{files}}; then
        PASSED+=("Security Scanning")
    else
        FAILED+=("Security Scanning")
    fi

    echo ""
    if just lint-complexity {{files}}; then
        PASSED+=("Complexity Analysis")
    else
        FAILED+=("Complexity Analysis")
    fi

    echo ""
    # Get the first file/directory for placement
    PLACEMENT_TARGET=$(echo "{{files}}" | awk '{print $1}')
    if just lint-placement "$PLACEMENT_TARGET"; then
        PASSED+=("File Placement")
    else
        FAILED+=("File Placement")
    fi

    echo ""
    if just lint-solid {{files}}; then
        PASSED+=("SOLID Principles")
    else
        FAILED+=("SOLID Principles")
    fi

    echo ""
    if just lint-dry {{files}}; then
        PASSED+=("DRY Principles")
    else
        FAILED+=("DRY Principles")
    fi

    # Print summary
    echo ""
    echo -e "{{BLUE}}{{BOLD}}╔════════════════════════════════════════════════════════════╗{{NC}}"
    echo -e "{{BOLD}}║                      SUMMARY                               ║{{NC}}"
    echo -e "{{BLUE}}{{BOLD}}╚════════════════════════════════════════════════════════════╝{{NC}}"
    echo ""

    if [ ${#PASSED[@]} -gt 0 ]; then
        echo -e "{{GREEN}}{{BOLD}}✓ PASSED (${#PASSED[@]}):{{NC}}"
        for item in "${PASSED[@]}"; do
            echo -e "{{GREEN}}  ✓ $item{{NC}}"
        done
        echo ""
    fi

    if [ ${#FAILED[@]} -gt 0 ]; then
        echo -e "{{RED}}{{BOLD}}✗ FAILED (${#FAILED[@]}):{{NC}}"
        for item in "${FAILED[@]}"; do
            echo -e "{{RED}}  ✗ $item{{NC}}"
        done
        echo ""
        echo -e "{{RED}}{{BOLD}}❌ Quality checks FAILED - please fix the issues above{{NC}}"
        exit 1
    else
        echo -e "{{GREEN}}{{BOLD}}✅ ALL QUALITY CHECKS PASSED!{{NC}}"
    fi

# Auto-fix formatting and linting issues
format:
    @poetry run ruff format src/ tests/
    @poetry run ruff check --fix src/ tests/

# Run tests
test:
    @poetry run pytest -v

# Run tests with coverage
test-coverage:
    @poetry run pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml -v

# Initial setup (install dependencies and show activation instructions)
init:
    @echo "🚀 Setting up thai-lint development environment..."
    @echo ""
    @poetry install
    @echo ""
    @echo "✅ Installation complete!"
    @echo ""
    @echo "📋 Next steps - Choose your preferred workflow:"
    @echo ""
    @echo "Option 1: Activate the virtual environment (Poetry 2.0+)"
    @echo "  source $(poetry env info --path)/bin/activate"
    @echo "  # Now you can run: thai-lint --help"
    @echo ""
    @echo "Option 2: Use poetry run prefix (no activation)"
    @echo "  poetry run thai-lint --help"
    @echo ""
    @echo "Option 3: Use just recipes (easiest, no activation)"
    @echo "  just lint-placement"
    @echo "  just test"
    @echo ""
    @echo "Quick start (copy and paste):"
    @echo "  source $(poetry env info --path)/bin/activate"
    @echo "  thai-lint file-placement ."
    @echo ""

# Install/update dependencies
install:
    @echo "📦 Installing dependencies..."
    @poetry install
    @echo "✓ Dependencies installed"

# Show command to activate virtualenv
activate:
    @echo "To activate the virtual environment, run:"
    @echo ""
    @echo "  source $(poetry env info --path)/bin/activate"
    @echo ""
    @echo "Or copy and paste this command:"
    @echo ""
    @echo "source $(poetry env info --path)/bin/activate"

# Show virtualenv path and activation command
venv-info:
    @echo "Virtual Environment Information:"
    @echo ""
    @echo "Virtualenv path:"
    @poetry env info --path
    @echo ""
    @echo "Python version:"
    @poetry env info --python
    @echo ""
    @echo "To activate the virtualenv (Poetry 2.0+):"
    @echo "  source $(poetry env info --path)/bin/activate"
    @echo ""
    @echo "Once activated, you can run:"
    @echo "  thai-lint --help"
    @echo "  thai-lint file-placement ."
    @echo ""
    @echo "To deactivate:"
    @echo "  deactivate"

# Clean cache and artifacts
clean:
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    @find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @rm -rf htmlcov/ .coverage 2>/dev/null || true
    @echo "✓ Cleaned cache and artifacts"

# Show current version from pyproject.toml
show-version:
    @VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
    echo "Current version: $VERSION"

# Interactive version bump with validation
bump-version:
    #!/usr/bin/env bash
    echo "=========================================="
    echo "Version Bump"
    echo "=========================================="
    echo ""
    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    echo "Current version: $CURRENT_VERSION"
    echo ""
    echo "Enter new version (semver format: major.minor.patch):"
    read -r NEW_VERSION
    echo ""
    if [ -z "$NEW_VERSION" ]; then
        echo "❌ Version cannot be empty!"
        exit 1
    fi
    if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        echo "❌ Invalid version format! Must be semver (e.g., 1.2.3)"
        exit 1
    fi
    echo "Updating version from $CURRENT_VERSION to $NEW_VERSION"
    echo ""
    echo "Confirm update? [y/N]"
    read -r CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "❌ Version update cancelled"
        exit 1
    fi
    echo ""
    echo "Updating pyproject.toml..."
    sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    if [ $? -ne 0 ]; then
        echo "❌ Failed to update pyproject.toml!"
        exit 1
    fi
    echo "✓ Updated pyproject.toml"
    echo ""
    echo "Reinstalling package with new version..."
    poetry install --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to reinstall package!"
        echo "Reverting version change..."
        sed -i "s/^version = \"$NEW_VERSION\"/version = \"$CURRENT_VERSION\"/" pyproject.toml
        exit 1
    fi
    echo "✓ Package reinstalled"
    echo ""
    VERIFIED_VERSION=$(poetry run python -c "from src import __version__; print(__version__)")
    if [ "$VERIFIED_VERSION" = "$NEW_VERSION" ]; then
        echo "✅ Version successfully updated to $NEW_VERSION"
        echo ""
        echo "Next steps:"
        echo "  1. Review the change: git diff pyproject.toml"
        echo "  2. Commit the version bump: git commit -am 'chore: Bump version to $NEW_VERSION'"
        echo "  3. Publish: just publish"
    else
        echo "❌ Version verification failed!"
        echo "   Expected: $NEW_VERSION"
        echo "   Got: $VERIFIED_VERSION"
        exit 1
    fi

# Update version badges in README.md
update-version-badges:
    @echo "Updating version badges in README.md..."
    @VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
    sed -i "s|!\[Version\](https://img.shields.io/badge/version-.*-blue)|![Version](https://img.shields.io/badge/version-$VERSION-blue)|g" README.md || true
    @echo "✓ Version badges updated"

# Publish to PyPI (runs tests, linting, and version bump first)
publish-pypi:
    @echo "=========================================="
    @echo "Publishing to PyPI"
    @echo "=========================================="
    @echo ""
    @echo "Step 1: Running tests..."
    just test
    @echo "✓ Tests passed"
    @echo ""
    @echo "Step 2: Running full linting..."
    just lint-full
    @echo "✓ Linting passed"
    @echo ""
    @echo "Step 3: Version bump..."
    just bump-version
    @echo ""
    just _publish-pypi-only

# Internal: Publish to PyPI without running tests/linting
_publish-pypi-only:
    #!/usr/bin/env bash
    echo "=========================================="
    echo "Publishing to PyPI"
    echo "=========================================="
    echo ""
    echo "Step 1: Updating version badges..."
    just update-version-badges
    echo ""
    echo "Step 2: Updating lock file..."
    poetry lock
    echo "✓ Lock file updated"
    echo ""
    echo "Step 3: Cleaning previous builds..."
    rm -rf dist/ build/ *.egg-info
    echo "✓ Previous builds cleaned"
    echo ""
    echo "Step 4: Building package..."
    poetry build
    if [ $? -ne 0 ]; then
        echo "❌ Build failed!"
        exit 1
    fi
    echo "✓ Package built successfully"
    echo ""
    echo "Step 5: Publishing to PyPI..."
    if [ -f .env ]; then
        export $(cat .env | grep PYPI_API_TOKEN | xargs)
        poetry config pypi-token.pypi $PYPI_API_TOKEN
        poetry publish
    else
        echo "❌ .env file not found! Cannot read PYPI_API_TOKEN."
        exit 1
    fi
    if [ $? -eq 0 ]; then
        VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
        echo ""
        echo "✅ Successfully published to PyPI!"
        echo ""
        echo "Package: thailint"
        echo "Version: $VERSION"
        echo "URL: https://pypi.org/project/thailint/$VERSION/"
        echo ""
        echo "To install: pip install thailint==$VERSION"
    else
        echo "❌ Publishing to PyPI failed!"
        exit 1
    fi

# Publish to Docker Hub (runs tests, linting, and version bump first)
publish-docker:
    @echo "=========================================="
    @echo "Publishing to Docker Hub"
    @echo "=========================================="
    @echo ""
    @echo "Step 1: Running tests..."
    just test
    @echo "✓ Tests passed"
    @echo ""
    @echo "Step 2: Running full linting..."
    just lint-full
    @echo "✓ Linting passed"
    @echo ""
    @echo "Step 3: Version bump..."
    just bump-version
    @echo ""
    just _publish-docker-only

# Internal: Publish to Docker Hub without running tests/linting
_publish-docker-only:
    #!/usr/bin/env bash
    echo "=========================================="
    echo "Publishing to Docker Hub"
    echo "=========================================="
    echo ""
    echo "Step 1: Updating version badges..."
    just update-version-badges
    echo ""
    echo "Step 2: Updating lock file..."
    poetry lock
    echo "✓ Lock file updated"
    echo ""
    echo "Step 3: Loading Docker Hub credentials..."
    if [ ! -f .env ]; then
        echo "❌ .env file not found! Cannot read Docker Hub credentials."
        exit 1
    fi
    export $(cat .env | grep DOCKERHUB_USERNAME | xargs)
    export $(cat .env | grep DOCKERHUB_TOKEN | xargs)
    VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    echo "✓ Credentials loaded"
    echo ""
    echo "Step 4: Logging into Docker Hub..."
    echo $DOCKERHUB_TOKEN | docker login -u $DOCKERHUB_USERNAME --password-stdin
    if [ $? -ne 0 ]; then
        echo "❌ Docker Hub login failed!"
        exit 1
    fi
    echo "✓ Logged into Docker Hub"
    echo ""
    echo "Step 5: Building Docker image..."
    docker build -t $DOCKERHUB_USERNAME/thailint:$VERSION -t $DOCKERHUB_USERNAME/thailint:latest .
    if [ $? -ne 0 ]; then
        echo "❌ Docker build failed!"
        exit 1
    fi
    echo "✓ Docker image built"
    echo ""
    echo "Step 6: Pushing to Docker Hub..."
    docker push $DOCKERHUB_USERNAME/thailint:$VERSION
    docker push $DOCKERHUB_USERNAME/thailint:latest
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully published to Docker Hub!"
        echo ""
        echo "Image: $DOCKERHUB_USERNAME/thailint"
        echo "Tags: $VERSION, latest"
        echo "URL: https://hub.docker.com/r/$DOCKERHUB_USERNAME/thailint"
        echo ""
        echo "To pull: docker pull $DOCKERHUB_USERNAME/thailint:$VERSION"
        echo "To pull: docker pull $DOCKERHUB_USERNAME/thailint:latest"
    else
        echo "❌ Publishing to Docker Hub failed!"
        exit 1
    fi

# Publish to both PyPI and Docker Hub
# Usage:
#   just publish                 - Run with tests and linting
#   just publish --skip-checks   - Skip tests and linting (already validated)
publish *ARGS="":
    #!/usr/bin/env bash
    echo "=========================================="
    echo "Publishing to PyPI and Docker Hub"
    echo "=========================================="
    echo ""

    # Check for --skip-checks flag
    SKIP_CHECKS=false
    for arg in {{ARGS}}; do
        if [ "$arg" = "--skip-checks" ]; then
            SKIP_CHECKS=true
        fi
    done

    # Run checks unless skipped
    if [ "$SKIP_CHECKS" = "false" ]; then
        echo "Step 1: Running tests..."
        just test
        if [ $? -ne 0 ]; then
            echo "❌ Tests failed! Cannot publish."
            exit 1
        fi
        echo "✓ Tests passed"
        echo ""
        echo "Step 2: Running full linting..."
        just lint-full
        if [ $? -ne 0 ]; then
            echo "❌ Linting failed! Cannot publish."
            exit 1
        fi
        echo "✓ Linting passed"
        echo ""
    else
        echo "⚠️  SKIPPING tests and linting checks (--skip-checks flag)"
        echo ""
    fi

    # Version bump always runs (even with --skip-checks)
    echo "Step 3: Version bump..."
    just bump-version
    if [ $? -ne 0 ]; then
        echo "❌ Version bump cancelled or failed!"
        exit 1
    fi
    echo ""

    just _publish-pypi-only
    if [ $? -ne 0 ]; then
        echo "❌ PyPI publishing failed! Stopping."
        exit 1
    fi
    echo ""
    just _publish-docker-only
    if [ $? -ne 0 ]; then
        echo "❌ Docker Hub publishing failed!"
        exit 1
    fi
    echo ""
    echo "=========================================="
    echo "✅ Publishing Complete!"
    echo "=========================================="
    VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)
    echo ""
    echo "Published version: $VERSION"
    echo ""
    echo "PyPI: https://pypi.org/project/thailint/$VERSION/"
    echo "Docker Hub: https://hub.docker.com/r/$DOCKERHUB_USERNAME/thailint"
    echo ""
    echo "Installation:"
    echo "  pip install thailint==$VERSION"
    echo "  docker pull $DOCKERHUB_USERNAME/thailint:$VERSION"
