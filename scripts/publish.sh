#!/usr/bin/env bash
# Purpose: Publish thai-lint to PyPI and Docker Hub, then create a PR for changes
# Scope: Full publish workflow including version bump, packaging, and PR creation
# Overview: Orchestrates the complete publish workflow: runs tests, updates badges,
#     bumps version, publishes to PyPI and Docker Hub, then creates a PR to capture
#     all changes made during the publish process (version bump, lock file, badges).
# Dependencies: poetry, docker, gh CLI, pyproject.toml, .env (for credentials)
# Exports: Exit codes (0=success, 1=error)
# Interfaces: Command line args (--skip-checks), terminal output
# Environment: Requires PYPI_API_TOKEN, DOCKERHUB_USERNAME, DOCKERHUB_TOKEN in .env
# Related: justfile (just publish), pyproject.toml, README.md

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

# Parse arguments
SKIP_CHECKS=false
VERSION=""
for arg in "$@"; do
    if [ "$arg" = "--skip-checks" ]; then
        SKIP_CHECKS=true
    elif [[ "$arg" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        VERSION="$arg"
    fi
done

# Check for VERSION_INPUT environment variable (from GitHub Actions)
if [ -z "$VERSION" ] && [ -n "${VERSION_INPUT:-}" ]; then
    VERSION="$VERSION_INPUT"
fi

echo "=========================================="
echo "Publishing to PyPI and Docker Hub"
echo "=========================================="
echo ""

# --- Step 1-4: Run checks (unless skipped) ---
if [ "$SKIP_CHECKS" = "false" ]; then
    echo "Step 1: Auto-formatting code..."
    just format
    echo "✓ Code formatted"
    echo ""

    echo "Step 2: Running tests with coverage..."
    just test-coverage
    echo "✓ Tests passed"
    echo ""

    echo "Step 3: Updating test and coverage badges..."
    just update-test-badges
    echo ""

    echo "Step 4: Running full linting..."
    just lint-full
    echo "✓ Linting passed"
    echo ""
else
    echo -e "${YELLOW}⚠️  SKIPPING tests and linting checks (--skip-checks flag)${NC}"
    echo ""
fi

# --- Step 5: Version bump ---
echo "Step 5: Version bump..."
if [ -n "$VERSION" ]; then
    # Non-interactive: version provided via argument or env var
    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    echo "Updating version from $CURRENT_VERSION to $VERSION"
    sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml
    poetry install --quiet
    echo "✓ Version bumped to $VERSION"
else
    # Interactive: prompt for version
    just bump-version
fi
echo ""

# --- Step 6: Publish to PyPI ---
just _publish-pypi-only
echo ""

# --- Step 7: Publish to Docker Hub ---
just _publish-docker-only
echo ""

# --- Step 8: Create branch and PR for publish changes ---
echo ""
echo "Step 8: Creating branch and PR for publish changes..."

VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)
BRANCH_NAME="publish/v$VERSION"

git checkout -b "$BRANCH_NAME"

git add pyproject.toml poetry.lock README.md

git commit -m "$(cat <<EOF
chore: Publish v$VERSION

Updates from publish workflow:
- Version bump to $VERSION
- Updated poetry.lock
- Updated README badges (version, tests, coverage)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push -u origin "$BRANCH_NAME"

gh pr create --title "chore: Publish v$VERSION" --body "$(cat <<EOF
## Summary
- Version bump to $VERSION
- Updated poetry.lock
- Updated README badges (version, tests, coverage)

## Published to
- PyPI: https://pypi.org/project/thailint/$VERSION/
- Docker Hub: https://hub.docker.com/r/$DOCKERHUB_USERNAME/thailint

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

git checkout main

echo -e "${GREEN}✓ Created PR for publish changes${NC}"

# --- Final summary ---
echo ""
echo "=========================================="
echo -e "${GREEN}${BOLD}✅ Publishing Complete!${NC}"
echo "=========================================="
echo ""
echo "Published version: $VERSION"
echo ""
echo "PyPI: https://pypi.org/project/thailint/$VERSION/"
echo "Docker Hub: https://hub.docker.com/r/$DOCKERHUB_USERNAME/thailint"
echo ""
echo "Installation:"
echo "  pip install thailint==$VERSION"
echo "  docker pull $DOCKERHUB_USERNAME/thailint:$VERSION"
