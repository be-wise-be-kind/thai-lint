# Pre-commit Hooks for thai-lint

**Purpose**: User guide for installing and using pre-commit hooks with thai-lint

**Scope**: Local development workflow automation and code quality enforcement

**Overview**: Pre-commit hooks automatically run code quality checks before commits and pushes, ensuring all code meets quality standards before it enters version control. This guide covers installation, configuration, usage, and troubleshooting for integrating thai-lint with your git workflow.

---

## What Are Pre-commit Hooks?

Pre-commit hooks are automated checks that run before git commits and pushes. They help maintain code quality by:

- **Preventing Bad Code**: Stop commits with linting errors or failing tests
- **Automating Quality Checks**: Run formatters, linters, and tests automatically
- **Saving Time**: Catch issues locally before pushing to remote
- **Enforcing Standards**: Ensure all team members follow the same quality gates

## Quick Start

Install pre-commit hooks in 3 simple steps:

```bash
# 1. Install pre-commit framework
pip install pre-commit

# 2. Install git hooks
pre-commit install
pre-commit install --hook-type pre-push

# 3. Test it works
pre-commit run --all-files
```

That's it! Your hooks are installed and will run automatically on every commit and push.

---

## Installation

### Prerequisites

Before installing pre-commit hooks, ensure you have:

- Git repository initialized (`git init`)
- Python 3.9 or higher installed
- thai-lint installed (`pip install thailint`)

### Step 1: Install Pre-commit Framework

Install the pre-commit framework using pip:

```bash
# Using pip
pip install pre-commit

# Or using pip3
pip3 install pre-commit

# Verify installation
pre-commit --version
# Output: pre-commit 3.x.x
```

**Alternative installation methods:**

```bash
# Using Homebrew (macOS)
brew install pre-commit

# Using conda
conda install -c conda-forge pre-commit
```

### Step 2: Install Git Hooks

Install the hooks into your git repository:

```bash
# Install pre-commit hooks (runs on 'git commit')
pre-commit install
# Output: pre-commit installed at .git/hooks/pre-commit

# Install pre-push hooks (runs on 'git push')
pre-commit install --hook-type pre-push
# Output: pre-commit installed at .git/hooks/pre-push
```

**Verify installation:**

```bash
# Check hooks were created
ls -la .git/hooks/pre-commit .git/hooks/pre-push

# View hook contents
cat .git/hooks/pre-commit
```

### Step 3: Test Hooks

Test the hooks on your codebase:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Expected: Hooks run, may show some violations to fix
```

**Note:** The first run is slower as tools are downloaded and cached. Subsequent runs are much faster.

---

## Configuration

thai-lint uses a `.pre-commit-config.yaml` file to configure hooks. Here are two recommended configurations:

### Option 1: Using Poetry (Recommended for Development)

```yaml
repos:
  - repo: local
    hooks:
      # ========================================
      # BRANCH PROTECTION
      # ========================================
      - id: no-commit-to-main
        name: Prevent commits to main branch
        entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then echo "❌ Direct commits to main/master branch are not allowed! Create a feature branch instead."; exit 1; fi'
        language: system
        pass_filenames: false
        stages: [pre-commit]
        always_run: true

      # ========================================
      # PRE-COMMIT - Format and lint changed files
      # ========================================
      - id: thailint-file-placement
        name: Check file placement
        entry: poetry run thailint file-placement
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: thailint-nesting
        name: Check nesting depth
        entry: poetry run thailint nesting --max-depth 3
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: thailint-srp
        name: Check SRP violations
        entry: poetry run thailint srp
        language: system
        pass_filenames: false
        stages: [pre-commit]

      # ========================================
      # PRE-PUSH - Full validation on entire codebase
      # ========================================
      - id: pre-push-lint-all
        name: Run all linters (entire codebase)
        entry: bash -c 'poetry run thailint file-placement . && poetry run thailint nesting . && poetry run thailint srp .'
        language: system
        pass_filenames: false
        stages: [pre-push]
        always_run: true
```

### Option 2: Using Docker (Recommended for CI/CD)

```yaml
repos:
  - repo: local
    hooks:
      # ========================================
      # BRANCH PROTECTION
      # ========================================
      - id: no-commit-to-main
        name: Prevent commits to main branch
        entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then echo "❌ Direct commits to main/master branch are not allowed! Create a feature branch instead."; exit 1; fi'
        language: system
        pass_filenames: false
        stages: [pre-commit]
        always_run: true

      # ========================================
      # PRE-COMMIT - Format and lint changed files
      # ========================================
      - id: thailint-docker-file-placement
        name: Check file placement (Docker)
        entry: docker run --rm -v $(pwd):/workspace washad/thailint:latest file-placement /workspace
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: thailint-docker-nesting
        name: Check nesting depth (Docker)
        entry: docker run --rm -v $(pwd):/workspace washad/thailint:latest nesting --max-depth 3 /workspace
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: thailint-docker-srp
        name: Check SRP violations (Docker)
        entry: docker run --rm -v $(pwd):/workspace washad/thailint:latest srp /workspace
        language: system
        pass_filenames: false
        stages: [pre-commit]

      # ========================================
      # PRE-PUSH - Full validation on entire codebase
      # ========================================
      - id: pre-push-lint-all-docker
        name: Run all linters (Docker, entire codebase)
        entry: bash -c 'docker run --rm -v $(pwd):/workspace washad/thailint:latest file-placement /workspace && docker run --rm -v $(pwd):/workspace washad/thailint:latest nesting /workspace && docker run --rm -v $(pwd):/workspace washad/thailint:latest srp /workspace'
        language: system
        pass_filenames: false
        stages: [pre-push]
        always_run: true
```

### Customizing Configuration

**Add more protected branches:**
```yaml
# Protect develop branch too
entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "develop" ]; then ...'
```

**Skip specific hooks temporarily:**
```bash
# Skip all hooks (emergency only)
git commit --no-verify -m "Emergency fix"

# Skip specific hook
SKIP=lint-full-changed git commit -m "Skip linting this once"
```

---

## Usage

### Normal Development Workflow

Pre-commit hooks run automatically during your normal git workflow:

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes to your code
echo "def hello(): print('Hello')" > src/hello.py

# 3. Stage changes
git add src/hello.py

# 4. Commit (hooks run automatically)
git commit -m "Add hello function"
# Hooks run:
# ✓ Branch protection passed
# ✓ Format passed
# ✓ Lint checks passed
# Commit created

# 5. Push (pre-push hooks run)
git push origin feature/my-feature
# Hooks run:
# ✓ Full linting passed
# ✓ All tests passed
# Push completed
```

### What Hooks Do

**Pre-commit hooks** (run on `git commit`):
1. **Branch Protection**: Prevents commits directly to main/master
2. **Auto-format**: Fixes formatting issues automatically
3. **Lint Changed Files**: Runs linters only on files you changed (fast)

**Pre-push hooks** (run on `git push`):
1. **Full Linting**: Runs comprehensive linting on entire codebase
2. **All Tests**: Runs complete test suite

### Manual Hook Execution

You can run hooks manually without committing:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run all hooks on staged files only
pre-commit run

# Run specific hook
pre-commit run lint-full-changed

# Run specific hook on specific file
pre-commit run --files src/cli.py
```

---

## Using thai-lint in Pre-commit Hooks

### Basic thai-lint Hook

Add thai-lint to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: thailint-file-placement
        name: Check file placement
        entry: thailint file-placement
        language: system
        pass_filenames: false

      - id: thailint-nesting
        name: Check nesting depth
        entry: thailint nesting
        language: system
        files: \.py$
        pass_filenames: true
```

### thai-lint with Config File

```yaml
repos:
  - repo: local
    hooks:
      - id: thailint-nesting
        name: Check nesting depth with config
        entry: thailint nesting --config .thailint.yaml
        language: system
        files: \.py$
```

### thai-lint in Docker

If you're using thai-lint via Docker:

```yaml
repos:
  - repo: local
    hooks:
      - id: thailint-docker
        name: Run thailint in Docker
        entry: docker run --rm -v $(pwd):/workspace thailint/thailint nesting
        language: system
        pass_filenames: false
```

---

## Workflow Examples

### Example 1: Successful Commit

```bash
$ git commit -m "Add new feature"

Prevent commits to main branch..................................Passed
Auto-fix formatting issues......................................Passed
Run all linting checks (changed files only)....................Passed

[feature/my-feature abc123] Add new feature
 1 file changed, 10 insertions(+)
```

### Example 2: Failed Commit (Linting Error)

```bash
$ git commit -m "Add buggy code"

Prevent commits to main branch..................................Passed
Auto-fix formatting issues......................................Passed
Run all linting checks (changed files only)....................Failed
- hook id: lint-full-changed
- exit code: 1

src/buggy.py:5:1: E302 expected 2 blank lines, found 1
src/buggy.py:10:80: E501 line too long (85 > 79 characters)

# Fix the errors
$ make format
$ git add -u
$ git commit -m "Add feature (fixed linting)"
# Hooks pass, commit succeeds
```

### Example 3: Protected Branch Violation

```bash
$ git checkout main
$ git commit -m "Direct commit to main"

Prevent commits to main branch..................................Failed
- hook id: no-commit-to-main
- exit code: 1

❌ Direct commits to main/master branch are not allowed! Create a feature branch instead.

# Create feature branch instead
$ git checkout -b feature/my-feature
$ git commit -m "Add feature"
# Hooks pass, commit succeeds
```

---

## Troubleshooting

### Issue: Pre-commit Not Found

**Symptoms:** `pre-commit: command not found`

**Solution:** Install pre-commit framework
```bash
pip install pre-commit
# or
pip3 install pre-commit
```

### Issue: Hooks Not Running

**Symptoms:** Commits succeed without running hooks

**Solution:** Install git hooks
```bash
pre-commit install
pre-commit install --hook-type pre-push
```

**Verify:**
```bash
ls -la .git/hooks/pre-commit .git/hooks/pre-push
```

### Issue: Hooks Failing with Command Not Found

**Symptoms:** `poetry: command not found` or `docker: command not found`

**Solution:** Install the required tool for your configuration

**For Poetry:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry

# Verify installation
poetry --version
```

**For Docker:**
```bash
# Install Docker (varies by OS)
# See: https://docs.docker.com/get-docker/

# Verify installation
docker --version
```

### Issue: Want to Skip Hooks Temporarily

**Symptoms:** Need to commit urgently without running hooks

**Solution:** Use `--no-verify` (emergency only)
```bash
git commit --no-verify -m "Emergency fix"
```

**Warning:** Only use for genuine emergencies. Fix issues immediately after.

### Issue: Hooks Are Too Slow

**Symptoms:** Hooks take >30 seconds

**Solutions:**
1. First run is slower (tools downloaded and cached)
2. Subsequent runs should be faster (3-10s)
3. Pre-commit hooks only lint changed files (fast)
4. Pre-push hooks lint all files (slower, but comprehensive)

### Issue: Hook Fails But I Don't Understand Why

**Solution:** Run the command manually with verbose output

**For Poetry:**
```bash
# Run specific hook manually
pre-commit run thailint-nesting --verbose

# Run thailint directly
poetry run thailint nesting . --format text
```

**For Docker:**
```bash
# Run specific hook manually
pre-commit run thailint-docker-nesting --verbose

# Run Docker command directly
docker run --rm -v $(pwd):/workspace washad/thailint:latest nesting /workspace
```

---

## Best Practices

### 1. Always Work on Feature Branches

```bash
# Good: Create feature branch
git checkout -b feature/my-feature

# Bad: Commit directly to main (blocked by hooks)
git checkout main
git commit -m "..."  # ❌ Blocked by branch protection
```

### 2. Fix Issues Before Committing

Save time by running linters before commit:

```bash
# Run linters manually first
poetry run thailint file-placement .
poetry run thailint nesting .
poetry run thailint srp .

# Or with Docker
docker run --rm -v $(pwd):/workspace washad/thailint:latest file-placement /workspace

# Stage fixes
git add -u

# Commit (hooks pass faster)
git commit -m "Your message"
```

### 3. Commit Small Changes Frequently

- Smaller commits = faster hooks
- Easier to fix issues
- Better git history

### 4. Review Hook Output

When hooks fail:
1. Read the error messages
2. Understand why it failed
3. Fix the actual issue
4. Don't skip hooks without good reason

### 5. Keep Hooks Updated

Update pre-commit framework regularly:

```bash
# Update pre-commit
pip install --upgrade pre-commit

# Update hook dependencies
pre-commit autoupdate

# Test after updates
pre-commit run --all-files
```

---

## Advanced Configuration

### Skip Specific Files

```yaml
- id: thailint-nesting
  name: Check nesting depth
  entry: thailint nesting
  language: system
  files: \.py$
  exclude: ^tests/|^migrations/
```

### Run Hooks in Parallel

```yaml
- id: lint-parallel
  name: Run linting in parallel
  entry: bash -c 'make lint & make test & wait'
  language: system
```

### Custom Error Messages

```yaml
- id: custom-check
  name: Custom validation
  entry: bash -c 'echo "Running custom checks..." && ./scripts/validate.sh'
  language: system
```

---

## Integration with CI/CD

Run the same hooks in CI/CD to ensure consistency:

```yaml
# GitHub Actions example
name: Pre-commit Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pre-commit
      - name: Run pre-commit
        run: pre-commit run --all-files
```

---

## Summary

Pre-commit hooks help maintain code quality by:

✅ **Preventing bad commits**: Stop low-quality code from entering version control
✅ **Automating checks**: Run formatters, linters, and tests automatically
✅ **Saving time**: Catch issues locally before CI/CD
✅ **Enforcing standards**: Consistent quality across all contributors

**Quick reference:**
```bash
# Install
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push

# Use
git commit -m "..."    # Runs pre-commit hooks automatically
git push              # Runs pre-push hooks automatically

# Manual run
pre-commit run --all-files

# Skip (emergency only)
git commit --no-verify -m "..."
```

---

## Resources

- **Pre-commit Framework**: https://pre-commit.com/
- **thai-lint Documentation**: [README.md](../README.md)
- **Configuration Reference**: [.pre-commit-config.yaml](../.pre-commit-config.yaml)
- **Makefile Targets**: `make help`

## Support

For issues with pre-commit hooks:
- Check this guide's troubleshooting section
- Run hooks manually: `pre-commit run --all-files --verbose`
- Review `.pre-commit-config.yaml` configuration
- Check thai-lint documentation: [docs/](.)
