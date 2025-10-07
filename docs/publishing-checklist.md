# Publishing Validation Checklist

**Purpose**: Step-by-step checklist for validating thai-lint publications to PyPI and Docker Hub

**Scope**: Post-publication testing and validation procedures

**Overview**: Comprehensive validation checklist to ensure thai-lint packages are properly published and functional. Includes testing PyPI installation, Docker registry pulls, and end-to-end workflows in fresh environments. Validates that all three deployment modes (CLI, Library, Docker) work correctly after publication.

---

## Pre-Publication Checklist

Before running `make publish`, ensure:

### Version Management
- [ ] Version bumped in `pyproject.toml`
- [ ] `CHANGELOG.md` updated with version changes
- [ ] README badges will be updated (automated by make target)
- [ ] Git committed all changes
- [ ] Working directory is clean (`git status`)

### Quality Gates
- [ ] All tests pass: `make test` exits with code 0
- [ ] All linting passes: `make lint-full` exits with code 0
- [ ] No uncommitted changes that should be included
- [ ] Branch is up to date with remote

### Secrets Configuration
- [ ] `.env` file exists with API keys
- [ ] `PYPI_API_TOKEN` is set in `.env`
- [ ] `DOCKERHUB_TOKEN` is set in `.env`
- [ ] `DOCKERHUB_USERNAME` is set in `.env`
- [ ] API tokens are valid and not expired

---

## Publication Commands

### Option 1: Publish to Both PyPI and Docker Hub

```bash
# Publishes to both registries with full quality gates
make publish
```

### Option 2: Publish to PyPI Only

```bash
# Publishes only to PyPI
make publish-pypi
```

### Option 3: Publish to Docker Hub Only

```bash
# Publishes only to Docker Hub
make publish-docker
```

---

## Post-Publication Validation

After successful publication, validate the package works correctly.

### 1. Validate PyPI Publication

#### 1.1 Check PyPI Website

```bash
# Get published version
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

# Open PyPI package page
open "https://pypi.org/project/thailint/$VERSION/"
# Or visit manually: https://pypi.org/project/thailint/
```

**Verify:**
- [ ] Package is visible on PyPI
- [ ] Correct version number displayed
- [ ] README renders correctly
- [ ] Package metadata is correct (author, license, description)
- [ ] Download statistics show the new version

#### 1.2 Test PyPI Installation in Fresh Environment

Create a completely fresh virtual environment and test installation:

```bash
# Create fresh virtual environment
python3 -m venv /tmp/test-thailint-pypi
source /tmp/test-thailint-pypi/bin/activate

# Verify clean environment
which python
# Should show: /tmp/test-thailint-pypi/bin/python

# Install from PyPI
pip install thailint

# Or install specific version
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
pip install "thailint==$VERSION"
```

**Verify installation:**
- [ ] Package installs without errors
- [ ] No dependency conflicts
- [ ] Installation completes in reasonable time (<60 seconds)

#### 1.3 Test CLI Mode (PyPI)

```bash
# Test CLI is available
which thailint
# Should show: /tmp/test-thailint-pypi/bin/thailint

# Test version
thailint --version
# Should show: thailint, version X.Y.Z

# Test help
thailint --help
# Should show help text

# Test file-placement linter
thailint file-placement --help

# Test nesting linter
thailint nesting --help
```

**Verify CLI:**
- [ ] `thailint` command is available in PATH
- [ ] `--version` shows correct version
- [ ] `--help` displays help text
- [ ] Subcommands work (`file-placement`, `nesting`)

#### 1.4 Test Library Mode (PyPI)

```bash
# Test library import
python -c "from src import Linter; print('✅ Library import works')"

# Test basic API usage
python << 'EOF'
from src import Linter

# Create linter instance
linter = Linter()
print("✅ Linter instantiated successfully")

# Test configuration
config_file = ".thailint.yaml"
linter_with_config = Linter(config_file=config_file)
print("✅ Linter with config works")

print("✅ Library API validation complete")
EOF
```

**Verify library:**
- [ ] Library imports without errors
- [ ] `Linter` class can be instantiated
- [ ] Configuration loading works
- [ ] No import errors or warnings

#### 1.5 Test Real Linting (PyPI)

Create a test directory and run actual linting:

```bash
# Create test directory
mkdir -p /tmp/test-thailint-project/src
cd /tmp/test-thailint-project

# Create sample Python file with nesting violation
cat > src/example.py << 'EOF'
def process_data(items):
    for item in items:
        if item.is_valid():
            try:
                if item.process():
                    return True
            except Exception:
                pass
    return False
EOF

# Create config file
cat > .thailint.yaml << 'EOF'
nesting:
  enabled: true
  max_nesting_depth: 3
EOF

# Run nesting linter
thailint nesting src/ --config .thailint.yaml

# Should detect violation at depth 4
```

**Verify linting:**
- [ ] Linter runs without errors
- [ ] Violations are detected correctly
- [ ] Output is formatted properly
- [ ] Exit codes are correct (0 = pass, 1 = violations found)

#### 1.6 Cleanup PyPI Test

```bash
# Deactivate virtual environment
deactivate

# Remove test environment
rm -rf /tmp/test-thailint-pypi
rm -rf /tmp/test-thailint-project

echo "✅ PyPI validation complete and cleaned up"
```

**Final PyPI checklist:**
- [ ] Installation works
- [ ] CLI mode works
- [ ] Library mode works
- [ ] Linting functionality works
- [ ] Cleanup completed

---

### 2. Validate Docker Hub Publication

#### 2.1 Check Docker Hub Website

```bash
# Get published version
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)

# Open Docker Hub page
open "https://hub.docker.com/r/$DOCKERHUB_USERNAME/thailint"
# Or visit manually
```

**Verify:**
- [ ] Image is visible on Docker Hub
- [ ] Correct version tag exists
- [ ] `latest` tag exists
- [ ] Image size is reasonable (≤300MB)
- [ ] Last updated timestamp is recent

#### 2.2 Test Docker Pull

```bash
# Get version and username
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)

# Pull specific version
docker pull "$DOCKERHUB_USERNAME/thailint:$VERSION"

# Pull latest
docker pull "$DOCKERHUB_USERNAME/thailint:latest"

# Verify images exist
docker images | grep thailint
```

**Verify pull:**
- [ ] Both version and latest tags pull successfully
- [ ] No pull errors
- [ ] Image size matches Docker Hub listing
- [ ] Pull completes in reasonable time

#### 2.3 Test CLI Mode (Docker)

```bash
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)

# Test help
docker run --rm "$DOCKERHUB_USERNAME/thailint:$VERSION" --help

# Test version
docker run --rm "$DOCKERHUB_USERNAME/thailint:$VERSION" --version

# Test file-placement command
docker run --rm "$DOCKERHUB_USERNAME/thailint:$VERSION" file-placement --help

# Test nesting command
docker run --rm "$DOCKERHUB_USERNAME/thailint:$VERSION" nesting --help
```

**Verify Docker CLI:**
- [ ] Container runs without errors
- [ ] `--help` displays help text
- [ ] `--version` shows correct version
- [ ] Subcommands are available

#### 2.4 Test Volume Mounting (Docker)

```bash
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)

# Create test directory
mkdir -p /tmp/test-docker-mount/src
cd /tmp/test-docker-mount

# Create sample file
cat > src/test.py << 'EOF'
def deeply_nested():
    for i in range(10):
        if i > 5:
            try:
                if i == 7:
                    return True
            except:
                pass
    return False
EOF

# Run linter with volume mount
docker run --rm \
    -v "$(pwd):/workspace" \
    "$DOCKERHUB_USERNAME/thailint:$VERSION" \
    nesting /workspace/src/

# Should detect nesting violations
```

**Verify volume mounting:**
- [ ] Container can access mounted files
- [ ] Linting runs on mounted code
- [ ] Results are displayed correctly
- [ ] No permission errors

#### 2.5 Test with Config File (Docker)

```bash
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)

# Create config file
cat > .thailint.yaml << 'EOF'
nesting:
  enabled: true
  max_nesting_depth: 3
EOF

# Run with config
docker run --rm \
    -v "$(pwd):/workspace" \
    "$DOCKERHUB_USERNAME/thailint:$VERSION" \
    nesting --config /workspace/.thailint.yaml /workspace/src/

# Should use config settings
```

**Verify config:**
- [ ] Config file is read correctly
- [ ] Settings are applied
- [ ] No config parsing errors

#### 2.6 Cleanup Docker Test

```bash
# Remove test directory
cd ~
rm -rf /tmp/test-docker-mount

# Remove pulled images (optional)
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)
docker rmi "$DOCKERHUB_USERNAME/thailint:$VERSION"
docker rmi "$DOCKERHUB_USERNAME/thailint:latest"

echo "✅ Docker validation complete and cleaned up"
```

**Final Docker checklist:**
- [ ] Image pulls successfully
- [ ] CLI mode works in container
- [ ] Volume mounting works
- [ ] Config files work
- [ ] Cleanup completed

---

### 3. End-to-End Integration Test

Test the complete workflow as a new user would experience it.

#### 3.1 Dummy Project Setup

Create a fresh project directory:

```bash
# Create project structure
mkdir -p ~/test-thailint-integration
cd ~/test-thailint-integration

mkdir -p src tests docs
touch README.md

# Create sample Python files
cat > src/main.py << 'EOF'
"""Main application module."""

def main():
    """Entry point for the application."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
EOF

cat > src/utils.py << 'EOF'
"""Utility functions."""

def process_items(items):
    """Process a list of items with complex nesting."""
    results = []
    for item in items:
        if item:
            try:
                if item.startswith("test"):
                    if len(item) > 10:
                        results.append(item.upper())
            except AttributeError:
                pass
    return results
EOF

cat > tests/test_main.py << 'EOF'
"""Tests for main module."""

from src.main import main

def test_main():
    """Test main function."""
    main()  # Should run without errors
EOF

# Initialize git
git init
git add .
git commit -m "Initial commit"
```

#### 3.2 Install thai-lint

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install thailint from PyPI
pip install thailint

# Verify installation
thailint --version
```

**Verify:**
- [ ] Installation succeeds
- [ ] Version is correct

#### 3.3 Create Configuration

```bash
# Create thailint config
cat > .thailint.yaml << 'EOF'
nesting:
  enabled: true
  max_nesting_depth: 3

file-placement:
  directories:
    src:
      allow:
        - ".*\\.py$"
      deny:
        - "test_.*\\.py$"
    tests:
      allow:
        - "test_.*\\.py$"
        - "conftest\\.py$"
EOF
```

#### 3.4 Run Linting

```bash
# Run nesting linter
thailint nesting src/ --config .thailint.yaml

# Should detect violation in src/utils.py at depth 4

# Run file placement linter
thailint file-placement .

# Should pass (files are in correct locations)
```

**Verify:**
- [ ] Nesting violations detected in `src/utils.py`
- [ ] File placement linting passes
- [ ] Output is clear and helpful

#### 3.5 Install Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Create pre-commit config
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: thailint-nesting
        name: Check nesting depth
        entry: thailint nesting --config .thailint.yaml
        language: system
        files: \.py$
EOF

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files

# Should detect nesting violations
```

**Verify:**
- [ ] Pre-commit installs successfully
- [ ] Hooks detect violations
- [ ] Hook output is helpful

#### 3.6 Fix Violations and Test Workflow

```bash
# Fix the nesting violation in src/utils.py
cat > src/utils.py << 'EOF'
"""Utility functions."""

def process_items(items):
    """Process a list of items with guard clauses to reduce nesting."""
    results = []
    for item in items:
        if not item:
            continue

        try:
            if item.startswith("test") and len(item) > 10:
                results.append(item.upper())
        except AttributeError:
            pass

    return results
EOF

# Run linter again
thailint nesting src/ --config .thailint.yaml
# Should pass now

# Test pre-commit workflow
git add src/utils.py
git commit -m "Fix nesting violation"
# Hooks should pass, commit succeeds
```

**Verify:**
- [ ] Violations are fixed
- [ ] Linting passes
- [ ] Pre-commit hooks pass
- [ ] Commit succeeds

#### 3.7 Test Docker Workflow

```bash
# Test with Docker (using published image)
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME ~/.thai-lint/.env | cut -d'=' -f2 || echo "YOUR_USERNAME")

docker run --rm \
    -v "$(pwd):/workspace" \
    "$DOCKERHUB_USERNAME/thailint:latest" \
    nesting --config /workspace/.thailint.yaml /workspace/src/

# Should pass (violations fixed)
```

**Verify:**
- [ ] Docker container runs successfully
- [ ] Linting passes
- [ ] No errors or warnings

#### 3.8 Cleanup Integration Test

```bash
# Deactivate virtual environment
deactivate

# Remove test project
cd ~
rm -rf ~/test-thailint-integration

echo "✅ Integration test complete and cleaned up"
```

**Final integration checklist:**
- [ ] Project setup works
- [ ] thai-lint installation works
- [ ] Configuration works
- [ ] Linting detects violations
- [ ] Pre-commit hooks work
- [ ] Docker workflow works
- [ ] Cleanup completed

---

## Publication Success Criteria

The publication is successful when ALL of the following are true:

### PyPI Publication
- [ ] Package visible on PyPI website
- [ ] Installs cleanly in fresh environment
- [ ] CLI mode works (`thailint --version`, `thailint --help`)
- [ ] Library mode works (can import and use)
- [ ] Linting functionality works correctly

### Docker Hub Publication
- [ ] Image visible on Docker Hub
- [ ] Both version and latest tags exist
- [ ] Image pulls successfully
- [ ] CLI works in container
- [ ] Volume mounting works
- [ ] Config files work in container

### Integration Testing
- [ ] New user workflow completes successfully
- [ ] Linting detects violations correctly
- [ ] Pre-commit hooks work
- [ ] Docker workflow works
- [ ] Documentation is accurate

### Documentation Updates
- [ ] README badges updated with new version
- [ ] CHANGELOG.md includes version
- [ ] All links work
- [ ] Installation instructions are accurate

---

## Rollback Procedures

If validation fails, follow these rollback procedures:

### PyPI Rollback

```bash
# Cannot delete from PyPI, but can yank (hide from pip searches)
# Log into PyPI website and yank the release
# Then publish a hotfix version
```

### Docker Hub Rollback

```bash
# Delete tags from Docker Hub website
# Or use Docker Hub API
# Or just publish a new version and update latest tag
```

### Emergency Hotfix

```bash
# 1. Fix the issue in code
# 2. Bump version to X.Y.Z+1
vim pyproject.toml  # Update version

# 3. Update CHANGELOG
vim CHANGELOG.md

# 4. Publish hotfix
make publish
```

---

## Common Issues

### PyPI Installation Fails

**Symptoms:** `pip install thailint` fails

**Solutions:**
- Check PyPI is up (https://status.python.org/)
- Verify package name spelling: `thailint` not `thai-lint`
- Check PyPI package page for issues
- Try with specific version: `pip install thailint==X.Y.Z`

### Docker Pull Fails

**Symptoms:** `docker pull` fails

**Solutions:**
- Check Docker Hub is up
- Verify image name: `username/thailint` not `thailint/thailint`
- Check Docker Hub permissions
- Try pulling latest: `docker pull username/thailint:latest`

### CLI Not Found After Install

**Symptoms:** `thailint: command not found`

**Solutions:**
- Check virtual environment is activated
- Verify pip install succeeded: `pip list | grep thailint`
- Check entry points in pyproject.toml
- Try: `python -m src.cli --help`

### Docker Container Permission Errors

**Symptoms:** Permission denied accessing mounted files

**Solutions:**
- Use `-u $(id -u):$(id -g)` flag
- Check file permissions in host
- Verify volume mount path is correct

---

## Support

If validation fails and you can't resolve it:

1. **Check logs:** Review publication output for errors
2. **Test locally:** Ensure code works before publishing
3. **Verify credentials:** Check API tokens are valid
4. **Review documentation:** Check PyPI and Docker Hub docs
5. **Ask for help:** Create GitHub issue with validation results

---

## Automation

Consider automating this checklist with a validation script:

```bash
#!/bin/bash
# validate-publication.sh

set -e

echo "🔍 Validating thai-lint publication..."

# Test PyPI installation
python3 -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install thailint
thailint --version
deactivate
rm -rf /tmp/test-env

echo "✅ PyPI validation passed"

# Test Docker pull
DOCKERHUB_USERNAME=$(grep DOCKERHUB_USERNAME .env | cut -d'=' -f2)
docker pull "$DOCKERHUB_USERNAME/thailint:latest"
docker run --rm "$DOCKERHUB_USERNAME/thailint:latest" --version

echo "✅ Docker validation passed"

echo "✅ All validations passed!"
```

Make it executable:
```bash
chmod +x validate-publication.sh
./validate-publication.sh
```

---

## Summary

Use this checklist after every publication to ensure:

- ✅ PyPI package works correctly
- ✅ Docker image works correctly
- ✅ End-to-end user experience works
- ✅ Documentation is accurate
- ✅ Rollback plan is ready if needed

**Remember:** It's better to catch issues in validation than after users report them!
