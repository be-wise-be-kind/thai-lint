#!/usr/bin/env bash
# Purpose: Safe git workflow automation for quick collaboration without pre-commit hooks
# Scope: Git staging, committing, and pushing with comprehensive safety checks
# Overview: Streamlines the commit-push workflow for rapid iteration and collaboration by bypassing
#     pre-commit hooks and linting checks while maintaining critical safety guards. Detects sensitive
#     files (secrets, credentials, keys), validates branch naming conventions, prevents main branch
#     commits, and shows change previews before execution. Designed for WIP commits and quick sharing
#     while protecting against common security mistakes and data loss scenarios.
# Dependencies: git, bash 4.0+
# Exports: Exit codes (0=success, 1=user abort or error)
# Interfaces: Git CLI, user prompts (stdin/stdout), color-coded terminal output
# Environment: Git repository with remote origin configured
# Related: justfile (just share), .pre-commit-config.yaml, .git/hooks/
# Philosophy: Speed for collaboration, safety against accidents - trust but verify before commit
set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Safety check: prevent use on main/master/develop
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" || "$CURRENT_BRANCH" == "develop" ]]; then
    echo -e "${RED}❌ Error: Cannot use 'just share' on $CURRENT_BRANCH branch${NC}"
    echo "   Create a feature branch first with: git checkout -b <branch-name>"
    exit 1
fi

# Safety check: ensure branch follows naming convention (starts with feat/, fix/, etc.)
if ! [[ "$CURRENT_BRANCH" =~ ^(feat|fix|chore|docs|test|refactor|perf|ci|build|style|revert)/ ]]; then
    echo -e "${YELLOW}⚠️  Warning: Branch name doesn't follow convention${NC}"
    echo "   Expected pattern: <type>/<description> (e.g., feat/add-magic-numbers)"
    echo "   Valid types: feat, fix, chore, docs, test, refactor, perf, ci, build, style, revert"
    echo "   Current branch: $CURRENT_BRANCH"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Get commit message from argument or prompt
COMMIT_MSG="${1:-}"
if [ -z "$COMMIT_MSG" ]; then
    read -p "Enter commit message: " -r COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        echo -e "${RED}❌ Error: Commit message cannot be empty${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🔄 Quick sharing on branch: $CURRENT_BRANCH${NC}"
echo -e "${BLUE}📝 Message: $COMMIT_MSG${NC}"
echo ""

# Safety check: show what will be committed
echo -e "${YELLOW}📋 Checking status...${NC}"
git status --short

# Check for potentially sensitive files
SENSITIVE_PATTERNS=(
    "\.env$"
    "\.env\."
    "\.pem$"
    "\.key$"
    "\.p12$"
    "\.pfx$"
    "credential"
    "secret"
)

FOUND_SENSITIVE=false
# Get list of changed files (strip status codes, just get filenames)
CHANGED_FILES=$(git status --short | awk '{print $2}')

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if echo "$CHANGED_FILES" | grep -iE "$pattern" > /dev/null 2>&1; then
        echo -e "${RED}⚠️  WARNING: Potential sensitive file detected matching pattern: $pattern${NC}"
        echo "$CHANGED_FILES" | grep -iE "$pattern" | sed 's/^/     /'
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    echo ""
    read -p "Sensitive files detected! Are you SURE you want to commit? (yes/N): " -r
    if [[ ! $REPLY == "yes" ]]; then
        echo "Aborted for safety."
        exit 1
    fi
fi

# Check if there are actually changes to commit
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    exit 0
fi

# Stage all changes to show full diff
echo -e "${GREEN}📦 Staging all changes...${NC}"
git add -A

# Show what will be committed
echo ""
echo -e "${YELLOW}Changes to be committed:${NC}"
git diff --cached --stat
echo ""

# Single confirmation prompt (can be skipped with --yes flag)
if [[ "${2:-}" != "--yes" ]]; then
    read -p "Commit and push these changes? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Changes are staged but not committed."
        echo "Run 'git reset' to unstage."
        exit 1
    fi
fi

# Commit with --no-verify to skip hooks
echo -e "${GREEN}💾 Committing changes (skipping hooks)...${NC}"
if ! git commit -m "$COMMIT_MSG" --no-verify; then
    echo -e "${RED}❌ Commit failed${NC}"
    exit 1
fi

# Check if remote branch exists and is up to date
echo -e "${GREEN}🔍 Checking remote status...${NC}"
git fetch origin "$CURRENT_BRANCH" 2>/dev/null || true

# Check if we're behind remote
if git rev-list HEAD..origin/"$CURRENT_BRANCH" 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}⚠️  Warning: Your branch is behind origin/$CURRENT_BRANCH${NC}"
    echo "   You may want to pull and rebase before pushing."
    read -p "Continue with push anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Commit is saved locally."
        echo "Run 'git pull --rebase' then 'git push' manually."
        exit 1
    fi
fi

# Push to remote (creates remote branch if it doesn't exist)
echo -e "${GREEN}🚀 Pushing to origin/$CURRENT_BRANCH...${NC}"
if ! git push -u origin "$CURRENT_BRANCH" --no-verify; then
    echo -e "${RED}❌ Push failed${NC}"
    echo "   Your commit is saved locally but not pushed."
    echo "   Fix the issue and run 'git push' manually."
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Changes shared successfully!${NC}"
echo "   Branch: $CURRENT_BRANCH"
echo "   Remote: origin/$CURRENT_BRANCH"
