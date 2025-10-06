#!/usr/bin/env bash
# Purpose: Validate Python CLI application setup completeness
# Scope: Check all tools, Makefile targets, CI/CD workflows, and configurations
# Overview: Comprehensive validation script that checks Python CLI setup includes all
#     comprehensive tooling, Makefile targets, release workflows, and proper configurations.
#     Provides clear success/failure output with specific remediation steps.
# Dependencies: bash, poetry (optional), docker (optional), gh CLI (optional)
# Exports: Exit code 0 on success, 1 on failure
# Environment: Should be run from project root directory
# Related: AGENT_INSTRUCTIONS.md, cli-quality-standards.md

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Python CLI Application Setup Validation           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check file exists
check_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $description: $file"
        return 0
    else
        echo -e "${RED}❌${NC} $description: $file (MISSING)"
        ((ERRORS++))
        return 1
    fi
}

# Function to check command exists
check_command() {
    local cmd=$1
    local description=$2

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n1)
        echo -e "${GREEN}✅${NC} $description: $cmd ($version)"
        return 0
    else
        echo -e "${RED}❌${NC} $description: $cmd (NOT INSTALLED)"
        ((ERRORS++))
        return 1
    fi
}

# Function to check Makefile target
check_make_target() {
    local target=$1
    local description=$2

    if make -n "$target" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $description: make $target"
        return 0
    else
        echo -e "${RED}❌${NC} $description: make $target (NOT FOUND)"
        ((ERRORS++))
        return 1
    fi
}

# Function to check pyproject.toml has tool
check_pyproject_tool() {
    local tool=$1
    local description=$2

    if [ -f "pyproject.toml" ] && grep -q "\\[tool\\.$tool\\]" pyproject.toml; then
        echo -e "${GREEN}✅${NC} $description: [tool.$tool] configured"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  $description: [tool.$tool] (NOT CONFIGURED)"
        ((WARNINGS++))
        return 1
    fi
}

echo -e "${CYAN}📁 Checking Project Structure...${NC}"
check_file "pyproject.toml" "Python project config"
check_file "src/cli.py" "CLI entrypoint"
check_file "src/config.py" "Config handler"
check_file "tests/test_cli.py" "CLI tests"
check_file "Makefile" "Main Makefile"
check_file "README.md" "Project README"
echo ""

echo -e "${CYAN}🔧 Checking Core Tools...${NC}"
check_command "python" "Python runtime"
check_command "poetry" "Poetry package manager"
check_command "docker" "Docker"
echo ""

echo -e "${CYAN}🧹 Checking Linting Tools...${NC}"
if command -v poetry &> /dev/null; then
    poetry run ruff --version &> /dev/null && echo -e "${GREEN}✅${NC} Ruff (fast linter + formatter)" || { echo -e "${RED}❌${NC} Ruff (NOT INSTALLED)"; ((ERRORS++)); }
    poetry run pylint --version &> /dev/null && echo -e "${GREEN}✅${NC} Pylint (comprehensive linting)" || { echo -e "${RED}❌${NC} Pylint (NOT INSTALLED)"; ((ERRORS++)); }
    poetry run flake8 --version &> /dev/null && echo -e "${GREEN}✅${NC} Flake8 (style guide enforcement)" || { echo -e "${RED}❌${NC} Flake8 (NOT INSTALLED)"; ((ERRORS++)); }
else
    echo -e "${YELLOW}⚠️${NC}  Poetry not available, skipping tool checks"
    ((WARNINGS++))
fi
echo ""

echo -e "${CYAN}🔒 Checking Security Tools...${NC}"
if command -v poetry &> /dev/null; then
    poetry run bandit --version &> /dev/null && echo -e "${GREEN}✅${NC} Bandit (code security)" || { echo -e "${RED}❌${NC} Bandit (NOT INSTALLED)"; ((ERRORS++)); }
    poetry run safety --version &> /dev/null && echo -e "${GREEN}✅${NC} Safety (dependency vulnerabilities)" || { echo -e "${RED}❌${NC} Safety (NOT INSTALLED)"; ((ERRORS++)); }
    poetry run pip-audit --version &> /dev/null && echo -e "${GREEN}✅${NC} pip-audit (dependency audit)" || { echo -e "${RED}❌${NC} pip-audit (NOT INSTALLED)"; ((ERRORS++)); }
fi
echo ""

echo -e "${CYAN}📊 Checking Complexity Tools...${NC}"
if command -v poetry &> /dev/null; then
    poetry run radon --version &> /dev/null && echo -e "${GREEN}✅${NC} Radon (complexity analysis)" || { echo -e "${RED}❌${NC} Radon (NOT INSTALLED)"; ((ERRORS++)); }
    poetry run xenon --version &> /dev/null && echo -e "${GREEN}✅${NC} Xenon (complexity enforcement)" || { echo -e "${RED}❌${NC} Xenon (NOT INSTALLED)"; ((ERRORS++)); }
fi
echo ""

echo -e "${CYAN}🎯 Checking Type Checking...${NC}"
if command -v poetry &> /dev/null; then
    poetry run mypy --version &> /dev/null && echo -e "${GREEN}✅${NC} MyPy (static type checker)" || { echo -e "${RED}❌${NC} MyPy (NOT INSTALLED)"; ((ERRORS++)); }
fi
echo ""

echo -e "${CYAN}🧪 Checking Testing Tools...${NC}"
if command -v poetry &> /dev/null; then
    poetry run pytest --version &> /dev/null && echo -e "${GREEN}✅${NC} pytest (testing framework)" || { echo -e "${RED}❌${NC} pytest (NOT INSTALLED)"; ((ERRORS++)); }
    poetry show pytest-cov &> /dev/null && echo -e "${GREEN}✅${NC} pytest-cov (coverage)" || { echo -e "${YELLOW}⚠️${NC}  pytest-cov (NOT INSTALLED)"; ((WARNINGS++)); }
fi
echo ""

echo -e "${CYAN}🎯 Checking Makefile Targets...${NC}"
check_make_target "help" "Help target"
check_make_target "lint" "Fast linting (Ruff)"
check_make_target "lint-all" "Comprehensive linting"
check_make_target "lint-security" "Security scanning"
check_make_target "lint-complexity" "Complexity analysis"
check_make_target "lint-full" "ALL quality checks"
check_make_target "format" "Auto-fix formatting"
check_make_target "test" "Run tests"
check_make_target "test-coverage" "Tests with coverage"
echo ""

echo -e "${CYAN}⚙️  Checking Tool Configurations...${NC}"
check_pyproject_tool "ruff" "Ruff config"
check_pyproject_tool "pylint" "Pylint config"
check_pyproject_tool "mypy" "MyPy config"
echo ""

echo -e "${CYAN}🚀 Checking CI/CD...${NC}"
check_file ".github/workflows/python.yml" "Python CI workflow"
check_file ".github/workflows/release.yml" "Release workflow"
echo ""

echo -e "${CYAN}📚 Checking Documentation...${NC}"
check_file ".ai/docs/python-cli-architecture.md" "Architecture docs"
check_file ".ai/howtos/python-cli/how-to-add-cli-command.md" "How-to: Add command"
check_file ".ai/howtos/python-cli/how-to-publish-to-pypi.md" "How-to: PyPI publishing"
check_file ".ai/howtos/python-cli/how-to-create-github-release.md" "How-to: GitHub releases"
echo ""

# Summary
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    Validation Summary                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found (non-critical)${NC}"
    fi
    echo -e "${GREEN}Your Python CLI setup is complete and production-ready!${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo -e "${YELLOW}Remediation:${NC}"
    echo "1. Install missing tools: poetry install"
    echo "2. Install missing Makefile: cp plugins/languages/python/core/project-content/makefiles/makefile-python.mk ./Makefile.python"
    echo "3. Install release workflow: cp plugins/applications/python-cli/project-content/.github/workflows/release.yml.template .github/workflows/release.yml"
    echo ""
    exit 1
fi
