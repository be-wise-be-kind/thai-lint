# python-cli installation - AI Context

**Purpose**: AI agent context document for implementing python-cli installation

**Scope**: Complete installation of Python CLI application plugin with all dependencies for the thai-lint project

**Overview**: Comprehensive context document for AI agents working on the python-cli installation feature.
    This document provides full context for installing a production-ready Python CLI application with Click framework,
    Docker packaging, comprehensive testing, security scanning, and CI/CD automation for the thai-lint project.

**Dependencies**: ai-projen framework, Git, Python 3.11+, Docker, Poetry

**Exports**: Fully configured Python CLI application with foundation, language, infrastructure, and standards plugins

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Roadmap-based meta-plugin installation via sequential PR execution

---

## Overview

The thai-lint project is "The AI Linter" - a specialized linter dedicated to identifying and preventing common mistakes made by AI agents when generating code. The goal is to create a cross-language linting tool that can be run against codebases to catch AI-specific antipatterns, security issues, and quality problems.

This installation roadmap sets up the complete Python CLI application infrastructure needed to build, test, package, and distribute the thai-lint tool as a professional command-line utility.

## Project Background

**Project Name**: thai-lint (The AI Linter)

**Mission**: Provide governance and quality control for AI-generated code across multiple programming languages

**Target Users**:
- Development teams using AI coding assistants
- DevOps engineers implementing AI-assisted automation
- Organizations establishing AI code quality standards
- Individual developers wanting to validate AI-generated code

**Repository**: /home/stevejackson/Projects/thai-lint

**Current State**: Empty repository (only README.md exists)

## Feature Vision

This installation creates a production-ready Python CLI application with:

1. **Professional CLI Framework**: Click-based command-line interface with subcommands, options, configuration management
2. **Comprehensive Testing**: pytest test suite with coverage reporting, fixtures, and CI/CD integration
3. **Code Quality Tooling**: Ruff (linting + formatting), MyPy (type checking), Pylint, Flake8, complexity analysis
4. **Security Scanning**: Bandit (code security), Safety (CVE database), pip-audit (OSV database), Gitleaks (secrets)
5. **Docker Packaging**: Containerized distribution for cross-platform deployment
6. **CI/CD Automation**: GitHub Actions workflows for testing, linting, security scanning, releases
7. **Documentation Standards**: File headers, README templates, how-to guides
8. **Pre-commit Hooks**: Automated quality gates before commits

## Current Application Context

**Stage**: Initial setup (no application code exists yet)

**Technology Decisions**:
- Language: Python 3.11+ (modern async support, performance improvements)
- CLI Framework: Click 8.x (decorator-based, widely adopted, extensive plugin ecosystem)
- Dependency Manager: Poetry (isolated venvs, lockfiles, prevents system corruption)
- Linter: Ruff (10-100x faster than traditional tools, handles linting + formatting)
- Testing: pytest (fixtures, parametrization, async support, coverage)
- Containerization: Docker + docker-compose (standardized packaging)
- CI/CD: GitHub Actions (native GitHub integration, matrix testing)

## Target Architecture

### Core Components

**CLI Application Structure**:
```
src/
├── cli.py           # Main CLI entrypoint with Click commands
├── config.py        # YAML/JSON configuration file management
├── commands/        # Individual command implementations
│   ├── lint.py      # Linting command (future)
│   ├── check.py     # Check command (future)
│   └── fix.py       # Auto-fix command (future)
├── linters/         # Language-specific linters (future)
│   ├── python.py
│   ├── javascript.py
│   └── ...
└── utils/           # Shared utilities
    ├── logger.py    # Structured logging
    └── errors.py    # Custom exceptions

tests/
├── test_cli.py      # CLI invocation tests
├── test_config.py   # Configuration tests
└── test_linters/    # Linter-specific tests (future)
```

**Plugin Dependencies**:
1. foundation/ai-folder → Creates `.ai/` structure for AI navigation
2. languages/python → Python development environment (Ruff, MyPy, pytest, Poetry)
3. infrastructure/docker → Docker containerization
4. infrastructure/github-actions → CI/CD workflows
5. standards/security → Gitleaks, Trivy scanning
6. standards/documentation → File headers, README templates
7. standards/pre-commit-hooks → Git hooks for quality gates

### User Journey

**Developer using thai-lint**:
1. Install CLI tool: `pip install thai-lint` or use Docker image
2. Run linter on codebase: `thai-lint lint ./src --language python`
3. View results: Violations grouped by severity, file location, rule
4. Auto-fix issues: `thai-lint fix ./src --rule ai-hardcoded-paths`
5. Configure rules: `~/.config/thai-lint/config.yaml` for custom rules

**Developer contributing to thai-lint**:
1. Clone repository
2. Run `make install` (Poetry installs deps in isolated venv)
3. Develop features using `just test`, `just lint`, `just format`
4. Pre-commit hooks ensure quality before commits
5. CI/CD runs comprehensive checks on PR
6. Release automation publishes to PyPI + Docker Hub

### Technology Stack Details

**Python Tooling Suite**:
- **Ruff**: Primary linter + formatter (fast, comprehensive)
- **Pylint**: Deep code quality analysis (naming, design, refactoring)
- **Flake8**: Style guide enforcement with plugins (docstrings, bugbear, comprehensions)
- **MyPy**: Static type checking with strict mode
- **Bandit**: Security vulnerability detection
- **Safety**: CVE database scanning for dependencies
- **pip-audit**: OSV database scanning (alternative to Safety)
- **Radon**: Cyclomatic complexity and maintainability metrics
- **Xenon**: Complexity threshold enforcement

**Make Targets** (composite for clean namespace):
- `just lint` - Fast linting (Ruff only - for development)
- `just lint-all` - Comprehensive (Ruff + Pylint + Flake8 + MyPy)
- `just lint-security` - Security scans (Bandit + Safety + pip-audit)
- `just lint-complexity` - Complexity analysis (Radon + Xenon)
- `just lint-full` - All quality checks combined
- `just format` - Auto-fix formatting and linting issues
- `just test` - Run pytest tests
- `just test-coverage` - Tests with coverage reporting

## Key Decisions Made

### Decision 1: Roadmap-Based Installation

**Why**: Meta-plugin installations are complex (6 phases, 7+ plugins). Breaking into sequential PRs prevents AI agents from taking shortcuts, skipping phases, or rushing through installation.

**Impact**: Each PR installs one phase independently, with validation and commit before proceeding. Ensures systematic, error-free setup.

### Decision 2: Poetry for Dependency Management

**Why**: Prevents corruption of user's global Python environment. All dependencies installed in isolated virtual environment.

**Impact**: `poetry install` creates project-specific venv. Users can safely install/uninstall without affecting system Python.

### Decision 3: Composite Make Targets with lint-* Namespace

**Why**: Python has many linting tools. Grouping under `lint-*` prefix provides clean organization and progressive complexity (fast → comprehensive → full).

**Impact**: Developers can choose appropriate linting level:
- Development: `just lint` (fast, Ruff only)
- Pre-commit: `just lint-all` (comprehensive linters)
- CI/CD: `just lint-full` (everything including security + complexity)

### Decision 4: Click Over Typer/Argparse

**Why**: Click is mature, widely adopted, decorator-based (clean syntax), extensive plugin ecosystem.

**Impact**: Easier to add subcommands, nested command groups, configuration via decorators.

### Decision 5: Docker Packaging

**Why**: CLI tools need cross-platform distribution. Docker provides consistent runtime environment.

**Impact**: Users can run `docker run thai-lint lint ./code` without installing Python/dependencies locally.

## Integration Points

### With Existing Features

**None yet** - This is initial setup. All integrations are with ai-projen plugins being installed.

### With ai-projen Framework

**foundation/ai-folder**: Creates `.ai/` directory structure
- Provides navigation index (`.ai/index.yaml`)
- Organizes documentation (`.ai/docs/`)
- Stores how-to guides (`.ai/howtos/`)
- Manages templates (`.ai/templates/`)

**languages/python**: Python development environment
- Creates `pyproject.toml` with Poetry configuration
- Configures Ruff, MyPy, pytest
- Adds comprehensive tooling suite (Pylint, Flake8, Radon, Xenon, Security tools)
- Creates composite Makefile with `lint-*` targets

**infrastructure/docker**: Containerization
- Creates `Dockerfile` for CLI tool
- Provides `docker-compose.yml` for local development
- Configures multi-stage builds for smaller images

**infrastructure/github-actions**: CI/CD
- Test workflow (matrix testing across Python versions)
- Lint workflow (runs all quality checks)
- Security workflow (Bandit, Safety, Gitleaks)
- Release workflow (PyPI + Docker Hub publishing)

**standards/security**: Security standards
- Gitleaks for secret scanning
- Trivy for container vulnerability scanning
- Security-focused `.gitignore` patterns

**standards/documentation**: Documentation standards
- File header templates and requirements
- README structure and sections
- How-to guide standards

**standards/pre-commit-hooks**: Quality gates
- Pre-commit hooks for linting, formatting, secret scanning
- Prevents committing code that violates standards

## Success Metrics

**Installation Success**:
- [ ] All 7 PRs executed successfully
- [ ] All plugins installed without errors
- [ ] Validation script passes 100%
- [ ] CLI runs and displays help correctly
- [ ] Tests pass (starter code)
- [ ] Docker container builds and runs
- [ ] CI/CD workflows execute without errors

**Development Readiness**:
- [ ] `just lint` runs successfully
- [ ] `just test` runs successfully
- [ ] `just format` auto-fixes issues
- [ ] `poetry install` creates isolated venv
- [ ] Pre-commit hooks installed and working
- [ ] Documentation structure in place

**Production Readiness**:
- [ ] Security scans configured (Bandit, Safety, Gitleaks)
- [ ] CI/CD pipelines functional (test, lint, security, release)
- [ ] Docker packaging functional
- [ ] Release automation configured (PyPI, Docker Hub)
- [ ] Comprehensive tooling suite installed and configured

## Technical Constraints

**Python Version**: 3.11+ required
- Reason: Modern async support, performance improvements, better type hints

**Poetry Required**: Cannot use global pip
- Reason: Prevents system Python corruption, ensures reproducible builds

**Docker Required**: For packaging and distribution
- Reason: Cross-platform consistency, isolated runtime environment

**Git Required**: Version control mandatory
- Reason: All plugins require Git for branching, commits, workflow

**GitHub Required**: For CI/CD
- Reason: GitHub Actions workflows are platform-specific

## AI Agent Guidance

### When Executing PRs

**CRITICAL**: Execute ONE PR at a time, then STOP.

**Process**:
1. Read `PROGRESS_TRACKER.md` to identify next PR
2. Read `PR_BREAKDOWN.md` for that PR's detailed steps
3. Execute ONLY that PR's steps
4. Validate completion per PR success criteria
5. Update `PROGRESS_TRACKER.md` (mark PR complete, update "Next PR")
6. Commit changes with descriptive message
7. STOP - do NOT continue to next PR

**Anti-Pattern**: Executing multiple PRs in one session
**Why Bad**: Leads to shortcuts, skipped validation, incomplete setup

### When Following Plugin Instructions

**CRITICAL**: Read and follow plugin `AGENT_INSTRUCTIONS.md` files exactly.

**Process**:
1. Locate plugin's `AGENT_INSTRUCTIONS.md` file
2. Read entire document before starting
3. Follow steps sequentially (do not skip or reorder)
4. Validate after each major step
5. Commit changes when plugin installation complete

**Anti-Pattern**: Copying files without running plugin instructions
**Why Bad**: Plugins create infrastructure (configs, Make targets, Git hooks) that files depend on. Copying files alone creates broken installations.

### Common Patterns

**Pattern 1: State Detection Before Changes**
- Every plugin checks if already installed before making changes
- Prevents duplicate installations and conflicts

**Pattern 2: Branching Before Installation**
- Every plugin creates feature branch before changes
- Enables safe rollback if issues occur

**Pattern 3: Validation After Installation**
- Every plugin includes validation steps
- Confirms successful installation before proceeding

**Pattern 4: Makefile Target Organization**
- Language plugins use namespaced targets (`lint-*`, `test-*`)
- Composite targets group related operations (`lint-full` = all linting)
- Prevents target name collisions in multi-language projects

## Risk Mitigation

**Risk 1: Agent Takes Shortcuts**
- **Mitigation**: Roadmap-based approach with explicit PR boundaries, validation gates
- **Detection**: Files exist but commands fail, missing infrastructure

**Risk 2: Dependency Conflicts**
- **Mitigation**: Poetry lockfile ensures reproducible dependency resolution
- **Detection**: `poetry install` fails or different versions installed

**Risk 3: System Python Corruption**
- **Mitigation**: All operations through Poetry's isolated venv, never global pip
- **Detection**: System Python has project dependencies installed globally

**Risk 4: Plugin Installation Failures**
- **Mitigation**: Validation steps after each plugin, git branches for rollback
- **Detection**: Validation script reports missing files or failed commands

**Risk 5: CI/CD Workflow Failures**
- **Mitigation**: Test workflows locally before committing, matrix testing
- **Detection**: GitHub Actions show red X, failed checks

## Future Enhancements

**Post-Installation Development** (not part of installation roadmap):

1. **Core Linting Engine**:
   - Implement AST-based analysis for Python
   - Add pattern matching for common AI mistakes
   - Create rule engine with configurable severity levels

2. **Language Support**:
   - Python linter (AST analysis)
   - JavaScript/TypeScript linter (ESLint plugin architecture)
   - Additional languages (Go, Rust, Java, etc.)

3. **AI-Specific Rules**:
   - Hardcoded file paths (common AI mistake)
   - Missing error handling (AI often omits)
   - Over-generic variable names (AI tendency)
   - Missing type hints (Python-specific)
   - Incomplete test coverage (AI generates happy path only)
   - Security vulnerabilities (SQL injection, hardcoded secrets)

4. **Auto-Fix Capabilities**:
   - Suggest fixes for detected issues
   - Apply fixes automatically with `--fix` flag
   - Preview changes before applying

5. **Integration Options**:
   - VSCode extension
   - Pre-commit hook integration
   - CI/CD GitHub Action
   - Web service API

6. **Reporting**:
   - HTML reports with code snippets
   - JSON output for programmatic consumption
   - Dashboard for trend tracking

**Installation Scope**: This roadmap sets up the infrastructure only. Application-specific features are developed AFTER installation completes.
