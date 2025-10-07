# python-cli installation - PR Breakdown

**Purpose**: Detailed implementation breakdown of python-cli installation into manageable, atomic pull requests

**Scope**: Complete feature implementation from empty repository through production-ready Python CLI application

**Overview**: Comprehensive breakdown of the python-cli installation feature into 7 manageable, atomic
    pull requests (PR0-PR6). Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: ai-projen framework, Git, Python 3.11+, Docker, Poetry

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the python-cli installation feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application state
- Incrementally builds toward the complete feature
- Revertible if needed
- Validated before moving to next PR

---

## PR0: Planning - Create Roadmap

**Status**: ✅ Complete

**Branch**: main (planning happens on main)

**Goal**: Create the installation roadmap with three-document structure

**Why This PR**: Establishes the installation plan before executing any changes. Prevents shortcuts and ensures systematic execution.

### Implementation Steps

1. **Calculate parameters**:
   ```bash
   TARGET_REPO_PATH="$(pwd)"
   REPO_NAME=$(basename "${TARGET_REPO_PATH}")
   APP_NAME="${REPO_NAME}"
   INSTALL_PATH="."
   ```

2. **Create roadmap directory**:
   ```bash
   mkdir -p .roadmap/python-cli-install
   ```

3. **Copy templates**:
   ```bash
   cp .ai/templates/roadmap-meta-plugin-installation.md.template .roadmap/python-cli-install/PROGRESS_TRACKER.md
   cp .ai/templates/roadmap-pr-breakdown.md.template .roadmap/python-cli-install/PR_BREAKDOWN.md
   cp .ai/templates/roadmap-ai-context.md.template .roadmap/python-cli-install/AI_CONTEXT.md
   ```

4. **Replace template variables**: Use sed to populate all {{PLACEHOLDERS}}

5. **Commit roadmap**:
   ```bash
   git add .roadmap/python-cli-install/
   git commit -m "chore: Create roadmap for python-cli installation"
   ```

### Success Criteria
- [x] .roadmap/python-cli-install/ directory created
- [x] PROGRESS_TRACKER.md exists and populated
- [x] PR_BREAKDOWN.md exists and populated
- [x] AI_CONTEXT.md exists and populated
- [x] All template variables replaced
- [x] Roadmap committed to git

---

## PR1: Foundation - Install ai-folder Plugin

**Branch**: `feature/pr1-install-ai-folder`

**Goal**: Install foundation/ai-folder plugin to create .ai/ directory structure

**Why This PR**: Foundation plugin is required by all other plugins. Creates AI navigation and documentation structure.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout -b feature/pr1-install-ai-folder
   ```

2. **Follow plugin instructions**:
   ```bash
   # Read the plugin's installation instructions
   cat /path/to/ai-projen/plugins/foundation/ai-folder/AGENT_INSTRUCTIONS.md

   # Follow all steps exactly as documented
   ```

3. **Expected result**:
   - `.ai/` directory created
   - `.ai/index.yaml` created
   - `.ai/layout.yaml` created
   - `.ai/docs/` directory created
   - `.ai/howtos/` directory created
   - `.ai/templates/` directory created

### Validation

```bash
# Check directory structure
test -d .ai && echo "✅ .ai/ directory" || echo "❌ Missing .ai/"
test -f .ai/index.yaml && echo "✅ index.yaml" || echo "❌ Missing index.yaml"
test -f .ai/layout.yaml && echo "✅ layout.yaml" || echo "❌ Missing layout.yaml"
test -d .ai/docs && echo "✅ docs/ directory" || echo "❌ Missing docs/"
test -d .ai/howtos && echo "✅ howtos/ directory" || echo "❌ Missing howtos/"
test -d .ai/templates && echo "✅ templates/ directory" || echo "❌ Missing templates/"
```

### Success Criteria
- [ ] Feature branch created
- [ ] foundation/ai-folder plugin installation complete
- [ ] All validation checks pass
- [ ] Changes committed with descriptive message
- [ ] Branch merged to main
- [ ] Feature branch deleted
- [ ] PROGRESS_TRACKER.md updated (PR1 marked complete with commit hash)

---

## PR2: Languages - Install Python Plugin

**Branch**: `feature/pr2-install-python`

**Goal**: Install languages/python plugin with comprehensive tooling suite

**Why This PR**: Sets up Python development environment with all necessary linting, formatting, type checking, testing, and security tools.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/pr2-install-python
   ```

2. **Follow Python core plugin instructions**:
   ```bash
   # Read and follow
   cat /path/to/ai-projen/plugins/languages/python/core/AGENT_INSTRUCTIONS.md
   ```

3. **Install comprehensive tooling suite** (Step 11 in Python plugin):
   ```bash
   poetry add --group dev \
     pylint \
     flake8 flake8-docstrings flake8-bugbear flake8-comprehensions flake8-simplify \
     radon xenon \
     safety pip-audit
   ```

4. **Create composite Makefile**:
   - Create `Makefile` with `lint-*` namespaced targets
   - Include: `lint`, `lint-all`, `lint-security`, `lint-complexity`, `lint-full`
   - Include: `format`, `test`, `test-coverage`, `install`, `clean`

5. **Expected result**:
   - `pyproject.toml` created with Poetry configuration
   - Ruff, MyPy, pytest configured
   - Comprehensive tooling suite installed
   - `Makefile` with composite targets
   - `.gitignore` with Python-specific patterns

### Validation

```bash
# Check files
test -f pyproject.toml && echo "✅ pyproject.toml" || echo "❌ Missing pyproject.toml"
test -f Makefile && echo "✅ Makefile" || echo "❌ Missing Makefile"

# Check Poetry installed
poetry --version && echo "✅ Poetry" || echo "❌ Poetry not installed"

# Check comprehensive tools
poetry run pylint --version && echo "✅ Pylint" || echo "❌ Pylint missing"
poetry run flake8 --version && echo "✅ Flake8" || echo "❌ Flake8 missing"
poetry run radon --version && echo "✅ Radon" || echo "❌ Radon missing"
poetry run xenon --version && echo "✅ Xenon" || echo "❌ Xenon missing"
poetry run safety --version && echo "✅ Safety" || echo "❌ Safety missing"
poetry run pip-audit --version && echo "✅ pip-audit" || echo "❌ pip-audit missing"

# Check Makefile targets
make help | grep -q "lint-all" && echo "✅ lint-all target" || echo "❌ Missing lint-all"
make help | grep -q "lint-security" && echo "✅ lint-security target" || echo "❌ Missing lint-security"
make help | grep -q "lint-complexity" && echo "✅ lint-complexity target" || echo "❌ Missing lint-complexity"
make help | grep -q "lint-full" && echo "✅ lint-full target" || echo "❌ Missing lint-full"
```

### Success Criteria
- [ ] Feature branch created
- [ ] Python plugin installation complete
- [ ] Comprehensive tooling suite installed
- [ ] Composite Makefile created with lint-* targets
- [ ] All validation checks pass
- [ ] Changes committed
- [ ] Branch merged to main
- [ ] Feature branch deleted
- [ ] PROGRESS_TRACKER.md updated (PR2 marked complete with commit hash)

---

## PR3: Infrastructure - Install Docker and CI/CD

**Branch**: `feature/pr3-install-infrastructure`

**Goal**: Install Docker containerization and GitHub Actions CI/CD pipelines

**Why This PR**: Enables containerized distribution and automated testing/deployment.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/pr3-install-infrastructure
   ```

2. **Install Docker plugin**:
   ```bash
   # Follow Docker plugin instructions
   cat /path/to/ai-projen/plugins/infrastructure/containerization/docker/AGENT_INSTRUCTIONS.md

   # Options:
   # - Services: cli
   # - Compose: yes
   ```

3. **Install GitHub Actions plugin**:
   ```bash
   # Follow GitHub Actions plugin instructions
   cat /path/to/ai-projen/plugins/infrastructure/ci-cd/github-actions/AGENT_INSTRUCTIONS.md

   # Options:
   # - Workflows: all (test, lint, build, deploy)
   # - Matrix: yes
   # - Python versions: ["3.11", "3.12"]
   ```

4. **Expected result**:
   - `Dockerfile` created
   - `docker-compose.yml` created
   - `.github/workflows/test.yml` created
   - `.github/workflows/lint.yml` created
   - `.github/workflows/build.yml` created

### Validation

```bash
# Check Docker files
test -f Dockerfile && echo "✅ Dockerfile" || echo "❌ Missing Dockerfile"
test -f docker-compose.yml && echo "✅ docker-compose.yml" || echo "❌ Missing docker-compose.yml"

# Check CI/CD workflows
test -d .github/workflows && echo "✅ workflows/ directory" || echo "❌ Missing workflows/"
test -f .github/workflows/test.yml && echo "✅ test.yml" || echo "❌ Missing test.yml"
test -f .github/workflows/lint.yml && echo "✅ lint.yml" || echo "❌ Missing lint.yml"

# Verify Docker builds (optional - may fail without app code)
docker compose build --dry-run 2>/dev/null && echo "✅ Docker compose valid" || echo "⚠️  Docker compose (will work after app code added)"
```

### Success Criteria
- [ ] Feature branch created
- [ ] Docker plugin installation complete
- [ ] GitHub Actions plugin installation complete
- [ ] All validation checks pass
- [ ] Changes committed
- [ ] Branch merged to main
- [ ] Feature branch deleted
- [ ] PROGRESS_TRACKER.md updated (PR3 marked complete with commit hash)

---

## PR4: Standards - Install Security, Documentation, Pre-commit Hooks

**Branch**: `feature/pr4-install-standards`

**Goal**: Install security scanning, documentation standards, and pre-commit hooks

**Why This PR**: Establishes quality gates and security best practices.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/pr4-install-standards
   ```

2. **Install security plugin**:
   ```bash
   # Follow security plugin instructions
   cat /path/to/ai-projen/plugins/standards/security/AGENT_INSTRUCTIONS.md

   # Options:
   # - Scanning: [secrets, dependencies]
   # - Tools: [gitleaks, trivy]
   ```

3. **Install documentation plugin**:
   ```bash
   # Follow documentation plugin instructions
   cat /path/to/ai-projen/plugins/standards/documentation/AGENT_INSTRUCTIONS.md

   # Options:
   # - Headers: yes
   # - README sections: standard
   ```

4. **Install pre-commit hooks plugin**:
   ```bash
   # Follow pre-commit hooks plugin instructions
   cat /path/to/ai-projen/plugins/standards/pre-commit-hooks/AGENT_INSTRUCTIONS.md

   # Options:
   # - Hooks: [format, lint, secrets, trailing-whitespace]
   # - Python: yes
   ```

5. **Expected result**:
   - `.gitleaks.toml` or gitleaks configuration
   - `.ai/docs/file-headers.md` documentation standards
   - `.pre-commit-config.yaml` with hooks
   - Pre-commit hooks installed in `.git/hooks/`

### Validation

```bash
# Check security files
test -f .gitignore && grep -q "secrets" .gitignore && echo "✅ Security patterns in .gitignore" || echo "❌ Missing security patterns"

# Check documentation
test -f .ai/docs/FILE_HEADER_STANDARDS.md && echo "✅ File header standards" || echo "❌ Missing file header standards"

# Check pre-commit
test -f .pre-commit-config.yaml && echo "✅ pre-commit config" || echo "❌ Missing pre-commit config"
poetry run pre-commit --version && echo "✅ pre-commit installed" || echo "❌ pre-commit not installed"

# Test pre-commit runs
poetry run pre-commit run --all-files --show-diff-on-failure || echo "⚠️  Pre-commit checks (may fail until app code added)"
```

### Success Criteria
- [ ] Feature branch created
- [ ] Security plugin installation complete
- [ ] Documentation plugin installation complete
- [ ] Pre-commit hooks plugin installation complete
- [ ] All validation checks pass
- [ ] Changes committed
- [ ] Branch merged to main
- [ ] Feature branch deleted
- [ ] PROGRESS_TRACKER.md updated (PR4 marked complete with commit hash)

---

## PR5: Application - Copy CLI Code, Configure, Install Dependencies

**Branch**: `feature/pr5-install-application`

**Goal**: Copy Python CLI starter application code, configure for thai-lint project, install dependencies

**Why This PR**: Provides the actual CLI application code with Click framework, configuration management, and example commands.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/pr5-install-application
   ```

2. **Copy application source code**:
   ```bash
   # Copy from python-cli plugin
   cp -r /path/to/ai-projen/plugins/applications/python-cli/project-content/src ./
   cp -r /path/to/ai-projen/plugins/applications/python-cli/project-content/tests ./
   ```

3. **Copy and customize configuration files**:
   ```bash
   # Copy pyproject.toml template (may merge with existing)
   cp /path/to/ai-projen/plugins/applications/python-cli/project-content/pyproject.toml.template ./pyproject.toml.cli

   # Copy README template
   cp /path/to/ai-projen/plugins/applications/python-cli/project-content/README.md.template ./README.md

   # Customize for thai-lint
   sed -i 's/{{PROJECT_NAME}}/thai-lint/g' pyproject.toml README.md
   sed -i 's/{{PROJECT_DESCRIPTION}}/The AI Linter - Lint and governance for AI-generated code/g' pyproject.toml README.md
   sed -i 's/{{AUTHOR_NAME}}/Steve Jackson/g' pyproject.toml
   sed -i 's/{{AUTHOR_EMAIL}}/your.email@example.com/g' pyproject.toml
   ```

4. **Copy application documentation**:
   ```bash
   # Copy application-specific docs
   mkdir -p .ai/docs/python-cli
   cp /path/to/ai-projen/plugins/applications/python-cli/ai-content/docs/* .ai/docs/python-cli/

   # Copy application-specific how-tos
   mkdir -p .ai/howtos/python-cli
   cp -r /path/to/ai-projen/plugins/applications/python-cli/ai-content/howtos/* .ai/howtos/python-cli/

   # Copy application templates
   mkdir -p .ai/templates/python-cli
   cp -r /path/to/ai-projen/plugins/applications/python-cli/ai-content/templates/* .ai/templates/python-cli/
   ```

5. **Install dependencies with Poetry**:
   ```bash
   # Install all dependencies in isolated venv
   poetry install

   # Install pre-commit hooks
   poetry run pre-commit install
   ```

6. **Update .ai/index.yaml**:
   ```yaml
   application:
     type: cli
     stack: [python, click, docker]
     howtos: .ai/howtos/python-cli/
     templates: .ai/templates/python-cli/
     primary_language: python
     frameworks: [click, pytest]
   ```

7. **Expected result**:
   - `src/` directory with CLI application code
   - `tests/` directory with test suite
   - Application configured for "thai-lint"
   - Dependencies installed in Poetry venv
   - Pre-commit hooks active

### Validation

```bash
# Check application structure
test -d src && echo "✅ src/ directory" || echo "❌ Missing src/"
test -f src/cli.py && echo "✅ cli.py entrypoint" || echo "❌ Missing cli.py"
test -f src/config.py && echo "✅ config.py" || echo "❌ Missing config.py"
test -d tests && echo "✅ tests/ directory" || echo "❌ Missing tests/"

# Check configuration
grep -q "thai-lint" pyproject.toml && echo "✅ Project name configured" || echo "❌ Project name not set"

# Check dependencies
poetry show | grep -q "click" && echo "✅ Click installed" || echo "❌ Click missing"
poetry show | grep -q "pytest" && echo "✅ pytest installed" || echo "❌ pytest missing"

# Test CLI runs
poetry run python -m src.cli --help && echo "✅ CLI runs" || echo "❌ CLI fails"

# Test commands
poetry run python -m src.cli hello --name "Test" && echo "✅ Example command works" || echo "❌ Example command fails"

# Run tests
poetry run pytest -v && echo "✅ Tests pass" || echo "❌ Tests fail"
```

### Success Criteria
- [ ] Feature branch created
- [ ] Application source code copied
- [ ] Configuration customized for thai-lint
- [ ] Documentation copied to .ai/
- [ ] Dependencies installed via Poetry
- [ ] Pre-commit hooks installed
- [ ] CLI runs and displays help
- [ ] Example commands work
- [ ] Tests pass
- [ ] All validation checks pass
- [ ] Changes committed
- [ ] Branch merged to main
- [ ] Feature branch deleted
- [ ] PROGRESS_TRACKER.md updated (PR5 marked complete with commit hash)

---

## PR6: Finalization - Validate Setup and Create AGENTS.md

**Branch**: `feature/pr6-finalize`

**Goal**: Run comprehensive validation and create AGENTS.md for repository

**Why This PR**: Ensures complete, working installation and provides AI agent guidance for future development.

### Implementation Steps

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/pr6-finalize
   ```

2. **Copy and run validation script**:
   ```bash
   # Copy validation script
   mkdir -p ./scripts
   cp /path/to/ai-projen/plugins/applications/python-cli/scripts/validate-cli-setup.sh ./scripts/
   chmod +x ./scripts/validate-cli-setup.sh

   # Run validation
   ./scripts/validate-cli-setup.sh
   ```

3. **Create AGENTS.md** (AI agent guidance for the repository):
   ```bash
   cat > AGENTS.md << 'EOF'
   # AI Agent Instructions for thai-lint

   **Purpose**: Guide AI agents working on the thai-lint project

   **Project**: The AI Linter - Lint and governance for AI-generated code

   **Type**: Python CLI application

   ## Quick Start

   1. **Install dependencies**: `make install`
   2. **Run linter**: `make lint`
   3. **Run tests**: `make test`
   4. **Format code**: `make format`

   ## Development Workflow

   1. Create feature branch: `git checkout -b feature/your-feature`
   2. Make changes to source code in `src/`
   3. Add tests in `tests/`
   4. Run quality checks: `make lint-full`
   5. Run tests: `make test-coverage`
   6. Commit changes (pre-commit hooks will run)
   7. Create PR for review

   ## Project Structure

   - `src/cli.py` - Main CLI entrypoint
   - `src/config.py` - Configuration management
   - `src/commands/` - Individual command implementations
   - `src/linters/` - Language-specific linters
   - `tests/` - Test suite

   ## Make Targets

   - `make lint` - Fast linting (Ruff - for development)
   - `make lint-all` - Comprehensive linting (all linters + type checking)
   - `make lint-security` - Security scanning (Bandit, Safety, pip-audit)
   - `make lint-complexity` - Complexity analysis (Radon, Xenon)
   - `make lint-full` - ALL quality checks
   - `make format` - Auto-fix formatting issues
   - `make test` - Run tests
   - `make test-coverage` - Run tests with coverage

   ## Adding New Features

   See `.ai/howtos/python-cli/` for guides:
   - `how-to-add-cli-command.md` - Add new CLI commands
   - `how-to-handle-config-files.md` - Configuration management
   - `how-to-package-cli-tool.md` - Distribution and packaging

   ## Important Rules

   1. **Always use Make targets** - Never run `python`, `pytest`, or tools directly
   2. **All operations in Poetry venv** - Keeps dependencies isolated
   3. **Pre-commit hooks required** - Quality gates before commits
   4. **Tests required** - All features need test coverage
   5. **Security scanning** - Run `make lint-security` before PRs

   ## Next Development Steps

   The infrastructure is now complete. Next steps for thai-lint development:

   1. **Implement core linting engine**:
      - AST-based analysis for Python
      - Pattern matching for AI mistakes
      - Rule engine with configurable severity

   2. **Define AI-specific rules**:
      - Hardcoded file paths
      - Missing error handling
      - Generic variable names
      - Missing type hints
      - Incomplete test coverage

   3. **Add language support**:
      - Python linter (start here)
      - JavaScript/TypeScript
      - Additional languages

   4. **Auto-fix capabilities**:
      - Suggest fixes
      - Apply fixes with --fix flag

   See `.ai/docs/python-cli/` for architecture documentation.
   EOF
   ```

4. **Final validation**:
   ```bash
   # Run all quality checks
   make lint-full

   # Run tests
   make test-coverage

   # Build Docker container
   docker compose build

   # Test Docker container
   docker compose run cli --help
   ```

5. **Update PROGRESS_TRACKER.md**:
   - Mark PR6 as complete with commit hash
   - Set overall status to "Complete"

### Validation

```bash
# Check validation script
test -x ./scripts/validate-cli-setup.sh && echo "✅ Validation script" || echo "❌ Missing validation script"

# Check AGENTS.md
test -f AGENTS.md && echo "✅ AGENTS.md" || echo "❌ Missing AGENTS.md"

# Run comprehensive validation
./scripts/validate-cli-setup.sh || echo "❌ Validation failed"

# Verify all make targets work
make help && echo "✅ Makefile help" || echo "❌ Makefile help failed"
make lint && echo "✅ lint target" || echo "❌ lint failed"
make test && echo "✅ test target" || echo "❌ test failed"

# Verify Docker
docker compose build && echo "✅ Docker build" || echo "❌ Docker build failed"
docker compose run cli --help && echo "✅ Docker CLI" || echo "❌ Docker CLI failed"
```

### Success Criteria
- [ ] Feature branch created
- [ ] Validation script copied and executable
- [ ] Validation script passes 100%
- [ ] AGENTS.md created
- [ ] All make targets work
- [ ] Docker container builds and runs
- [ ] PROGRESS_TRACKER.md updated (PR6 marked complete, overall status = Complete)
- [ ] Changes committed
- [ ] Branch merged to main
- [ ] Feature branch deleted

---

## Implementation Guidelines

### Code Standards

**Python Code**:
- Follow PEP 8 style guide (enforced by Ruff)
- Use type hints (checked by MyPy)
- Maximum cyclomatic complexity: B (enforced by Xenon)
- Docstrings required for all public functions (enforced by Flake8)

**File Headers**:
- All Python files require docstring headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Include: Purpose, Scope, Overview, Dependencies, Exports

**Commit Messages**:
- Use conventional commits format
- Include commit hash in PROGRESS_TRACKER.md notes

### Testing Requirements

**Test Coverage**:
- Minimum 80% code coverage (measured by pytest-cov)
- All new features require tests
- Test both success and failure cases

**Test Structure**:
- Unit tests in `tests/test_*.py`
- Use pytest fixtures for reusable test components
- Use Click's testing utilities for CLI tests

**CI/CD Testing**:
- Tests run automatically on PR via GitHub Actions
- Matrix testing across Python 3.11 and 3.12
- All tests must pass before merge

### Documentation Standards

**Code Documentation**:
- All public functions/classes require docstrings
- Use Google-style docstrings (checked by Flake8)
- Include examples in docstrings for complex functions

**How-To Guides**:
- Store in `.ai/howtos/python-cli/`
- Follow `.ai/templates/HOW_TO_TEMPLATE.md` structure
- Include code examples and expected output

**Architecture Documentation**:
- Store in `.ai/docs/python-cli/`
- Update when making architectural changes
- Include diagrams where helpful

### Progress Tracking Standards

After completing each PR:
1. **Record commit hash in PROGRESS_TRACKER.md**:
   - Get the short commit hash: `git log --oneline -1`
   - Add to Notes column in PR Status Dashboard
   - Format: "Brief description (commit abc1234)"
   - Example: "Python plugin installed (commit c124b88)"
2. This creates a clear audit trail of when each PR was completed
3. Makes it easy to reference specific changes or revert if needed

### Security Considerations

**Secret Scanning**:
- Gitleaks runs on all commits (pre-commit hook)
- Never commit credentials, API keys, or secrets
- Use environment variables for sensitive data

**Dependency Scanning**:
- Safety and pip-audit scan for CVEs
- Run before releases: `make lint-security`
- Update vulnerable dependencies immediately

**Container Security**:
- Trivy scans Docker images for vulnerabilities
- Use minimal base images (python:3.11-slim)
- No secrets in Docker images

### Performance Targets

**CLI Responsiveness**:
- Help command: < 100ms
- Simple commands: < 500ms
- Linting small files: < 1s

**Test Suite**:
- Full test suite: < 10s
- Individual test files: < 2s

**Docker Image**:
- Image size: < 200MB
- Build time: < 2 minutes

## Rollout Strategy

**Phase 1: Infrastructure (PR0-PR4)**
- Establish foundation, language, infrastructure, standards
- No application code yet
- Focus: Environment setup and quality tooling

**Phase 2: Application (PR5)**
- Add CLI starter code
- Configure for thai-lint
- Validate all tooling works with app code

**Phase 3: Finalization (PR6)**
- Comprehensive validation
- Documentation completion
- Production readiness verification

## Success Metrics

### Launch Metrics

**Installation Success**:
- [ ] All 7 PRs completed
- [ ] All plugins installed without errors
- [ ] Validation script passes 100%
- [ ] No manual intervention required

**Application Functionality**:
- [ ] CLI runs and displays help
- [ ] Example commands execute successfully
- [ ] Tests pass with >80% coverage
- [ ] Docker container builds and runs

**Quality Gates**:
- [ ] All linters pass (Ruff, Pylint, Flake8, MyPy)
- [ ] Security scans pass (Bandit, Safety, Gitleaks)
- [ ] Complexity analysis within thresholds (Radon, Xenon)
- [ ] Pre-commit hooks installed and functional

### Ongoing Metrics

**Development Velocity**:
- Make targets work consistently
- CI/CD pipelines run successfully
- Pre-commit hooks prevent bad commits

**Code Quality**:
- Linting passes on all PRs
- Test coverage maintained >80%
- Security scans clean

**Production Readiness**:
- Docker builds succeed
- Release automation configured
- Documentation up to date
