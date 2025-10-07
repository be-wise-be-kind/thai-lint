# Deployment Modes

**Purpose**: Complete guide to using thailint in CLI, Library, and Docker deployment modes

**Scope**: All deployment options including command-line, programmatic, and containerized usage

**Overview**: Comprehensive guide covering all three deployment modes for thailint: CLI for terminal
    usage and scripting, Library API for programmatic integration in Python applications, and Docker
    for containerized deployments. Documents installation, configuration, usage patterns, and best
    practices for each mode. Helps users choose the right deployment mode for their use case and
    understand how to integrate thailint into different environments and workflows.

**Dependencies**: Python 3.11+, Docker (for container mode), pip/Poetry for installation

**Exports**: Deployment guides and integration patterns

**Related**: getting-started.md for quick start, cli-reference.md for CLI details, api-reference.md for library usage

**Implementation**: Mode-specific documentation with installation, usage, and integration examples

---

## Overview

thailint supports three deployment modes to fit different use cases and environments:

1. **CLI Mode** - Command-line interface for terminal usage and scripts
2. **Library Mode** - Python API for programmatic integration
3. **Docker Mode** - Containerized deployment for isolation and CI/CD

## Deployment Mode Comparison

| Feature | CLI Mode | Library Mode | Docker Mode |
|---------|----------|--------------|-------------|
| **Installation** | `pip install thailint` | `pip install thailint` | `docker pull thailint/thailint` |
| **Usage** | Terminal commands | Python import | Docker run |
| **Best For** | Interactive use, scripts | Python apps, editors | CI/CD, isolation |
| **Configuration** | Config file or flags | Config file or code | Config file + volumes |
| **Performance** | Fast | Fastest | Slight overhead |
| **Isolation** | No | No | Yes |
| **Python Required** | Yes | Yes | No (in container) |
| **Updates** | `pip install -U` | `pip install -U` | `docker pull` |

## CLI Mode

### Installation

```bash
# From PyPI
pip install thailint

# From source
git clone https://github.com/YOUR_USERNAME/thai-lint.git
cd thai-lint
pip install -e .

# Verify
thai-lint --version
```

### Basic Usage

```bash
# Lint current directory
thai-lint file-placement .

# Lint with config
thai-lint file-placement --config .thailint.yaml .

# JSON output
thai-lint file-placement --format json .

# Verbose mode
thai-lint --verbose lint file-placement .
```

### Configuration

**Option 1: Config File**

Create `.thailint.yaml`:
```yaml
directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"

ignore:
  - "__pycache__/"
  - "*.pyc"
```

Run:
```bash
thai-lint file-placement .
```

**Option 2: Inline Rules**

```bash
thai-lint file-placement --rules '{
  "allow": [".*\\.py$"],
  "deny": ["test_.*\\.py$"]
}' .
```

### Use Cases

#### 1. Interactive Development

```bash
# Quick check during development
thai-lint file-placement src/

# Check specific file
thai-lint file-placement src/main.py

# Check before commit
thai-lint file-placement . && git commit -m "feat: add feature"
```

#### 2. Shell Scripts

```bash
#!/bin/bash
# lint-and-test.sh

set -e

echo "Running linter..."
thai-lint file-placement .

echo "Running tests..."
pytest

echo "All checks passed!"
```

#### 3. Makefile Integration

```makefile
.PHONY: lint test all

lint:
	thai-lint file-placement .

test:
	pytest

all: lint test
	@echo "All checks passed"
```

#### 4. Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

thai-lint file-placement .
if [ $? -ne 0 ]; then
    echo "Linting failed - fix violations or use --no-verify"
    exit 1
fi
```

### CLI Mode Advantages

✅ **Simple** - No code required, just terminal commands
✅ **Interactive** - Immediate feedback
✅ **Scriptable** - Easy integration with bash/shell
✅ **Portable** - Works on any system with Python
✅ **Standard** - Uses familiar CLI patterns

### CLI Mode Limitations

❌ **No Programmatic Control** - Can't customize behavior in code
❌ **Less Flexible** - Limited to command-line options
❌ **Text Processing** - Requires parsing output for automation

## Library Mode

### Installation

```bash
# Same as CLI
pip install thailint
```

### Basic Usage

```python
from src import Linter

# Initialize
linter = Linter(config_file='.thailint.yaml')

# Lint
violations = linter.lint('src/', rules=['file-placement'])

# Process results
if violations:
    for v in violations:
        print(f"{v.file_path}: {v.message}")
```

### Configuration

**Option 1: Config File**

```python
from src import Linter

# Auto-discovers .thailint.yaml
linter = Linter()

# Or specify explicitly
linter = Linter(config_file='/path/to/config.yaml')

violations = linter.lint('src/')
```

**Option 2: Programmatic Config**

```python
from src import file_placement_lint
from pathlib import Path

config = {
    "allow": [r".*\.py$"],
    "deny": [r"test_.*\.py$"],
    "ignore": ["__pycache__/"]
}

violations = file_placement_lint(Path('src/'), config)
```

### Use Cases

#### 1. Editor Integration

```python
# VS Code extension
from src import Linter

class ThailintProvider:
    def __init__(self):
        self.linter = Linter()

    def lint_on_save(self, file_path: str):
        violations = self.linter.lint(file_path)
        return [self.to_diagnostic(v) for v in violations]

    def to_diagnostic(self, violation):
        return {
            "message": violation.message,
            "severity": "error",
            "source": "thailint"
        }
```

#### 2. CI/CD Scripts

```python
#!/usr/bin/env python3
# ci-lint.py

from src import Linter
import json
import sys

def main():
    linter = Linter(config_file='.thailint.yaml')
    violations = linter.lint('.')

    if violations:
        # Write JSON report
        with open('lint-report.json', 'w') as f:
            json.dump([v.to_dict() for v in violations], f, indent=2, default=str)

        print(f"❌ Found {len(violations)} violations")
        return 1

    print("✅ No violations")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### 3. Test Suite Integration

```python
# test_linting.py

import pytest
from src import Linter

@pytest.fixture
def linter():
    return Linter(config_file='.thailint.yaml')

def test_no_violations_in_src(linter):
    violations = linter.lint('src/')
    assert len(violations) == 0, f"Found violations: {violations}"

def test_no_violations_in_tests(linter):
    violations = linter.lint('tests/')
    assert len(violations) == 0
```

#### 4. Custom Workflows

```python
from src import Linter, Orchestrator
from pathlib import Path

def custom_linting_workflow():
    """Custom linting with advanced processing."""
    linter = Linter()

    # Lint different directories with different rules
    api_violations = linter.lint('src/api/', rules=['file-placement'])
    model_violations = linter.lint('src/models/', rules=['file-placement'])

    # Group by severity
    errors = [v for v in api_violations + model_violations if v.severity.name == "ERROR"]

    # Custom reporting
    if errors:
        print(f"Critical errors: {len(errors)}")
        for e in errors:
            notify_slack(f"Linting error in {e.file_path}: {e.message}")

    # Auto-fix (custom logic)
    for v in errors:
        suggest_fix(v)

def notify_slack(message: str):
    # Send to Slack
    pass

def suggest_fix(violation):
    # Suggest automated fix
    pass
```

### Library Mode Advantages

✅ **Programmatic Control** - Full customization in Python
✅ **Integration** - Embed in apps, editors, frameworks
✅ **Flexibility** - Custom workflows and processing
✅ **Type Safety** - Full type hints and IDE support
✅ **Performance** - Direct API calls, no subprocess overhead

### Library Mode Limitations

❌ **Python Only** - Requires Python application
❌ **Dependencies** - Must install package
❌ **Complexity** - More code than CLI

## Docker Mode

### Installation

```bash
# Pull from Docker Hub (when published)
docker pull thailint/thailint:latest

# Or build locally
docker build -t thailint/thailint .

# Or use docker-compose
docker-compose build
```

### Basic Usage

```bash
# Run with volume mount
docker run --rm -v $(pwd):/workspace thailint/thailint lint file-placement /workspace

# With config file
docker run --rm \
  -v $(pwd):/workspace \
  thailint/thailint lint file-placement --config /workspace/.thailint.yaml /workspace

# JSON output
docker run --rm -v $(pwd):/workspace \
  thailint/thailint lint file-placement --format json /workspace
```

### Configuration

**Option 1: Volume Mount Config**

```bash
# Mount directory with .thailint.yaml
docker run --rm \
  -v $(pwd):/workspace \
  thailint/thailint lint file-placement /workspace
```

**Option 2: Inline Rules**

```bash
docker run --rm -v $(pwd):/workspace \
  thailint/thailint lint file-placement \
  --rules '{"allow": [".*\\.py$"]}' \
  /workspace
```

**Option 3: Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  linter:
    image: thailint/thailint:latest
    volumes:
      - .:/workspace
    command: lint file-placement /workspace
```

Run:
```bash
docker-compose run linter
```

### Use Cases

#### 1. CI/CD Pipelines

**GitHub Actions:**

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run thailint
        run: |
          docker run --rm -v $(pwd):/workspace \
            thailint/thailint lint file-placement /workspace
```

**GitLab CI:**

```yaml
lint:
  image: thailint/thailint:latest
  script:
    - thai-lint file-placement .
  artifacts:
    when: on_failure
    paths:
      - lint-report.json
```

**Jenkins:**

```groovy
pipeline {
    agent {
        docker {
            image 'thailint/thailint:latest'
        }
    }
    stages {
        stage('Lint') {
            steps {
                sh 'thai-lint file-placement .'
            }
        }
    }
}
```

#### 2. Consistent Environments

```bash
# Same environment everywhere
docker run --rm -v $(pwd):/workspace \
  thailint/thailint lint file-placement /workspace

# No Python version conflicts
# No dependency issues
# Reproducible results
```

#### 3. Multi-project Setup

```bash
# Lint project A
docker run --rm -v ~/projects/project-a:/workspace \
  thailint/thailint lint file-placement /workspace

# Lint project B with different config
docker run --rm -v ~/projects/project-b:/workspace \
  thailint/thailint lint file-placement --config /workspace/.thailint.yaml /workspace
```

#### 4. Development Workflow

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  linter:
    image: thailint/thailint:latest
    volumes:
      - .:/workspace
    command: lint file-placement /workspace

  linter-dev:
    build: .
    volumes:
      - .:/workspace
      - ./src:/app/src  # Mount source for live updates
    command: lint file-placement /workspace
```

**Usage:**

```bash
# Production linter
docker-compose run linter

# Development linter (with source mount)
docker-compose run linter-dev

# Watch mode (with file watcher)
docker-compose run linter-dev --watch
```

### Docker Mode Advantages

✅ **Isolation** - No local Python required
✅ **Consistency** - Same environment everywhere
✅ **CI/CD Ready** - Perfect for pipelines
✅ **No Dependencies** - Self-contained image
✅ **Versioning** - Pin specific versions

### Docker Mode Limitations

❌ **Overhead** - Container startup time
❌ **Complexity** - More complex setup
❌ **Volume Mounts** - File permission issues
❌ **Size** - Image download required

## Choosing a Deployment Mode

### Use CLI Mode When:

- ✅ Working interactively in terminal
- ✅ Writing shell scripts
- ✅ Quick local development checks
- ✅ Pre-commit hooks
- ✅ Simple automation

### Use Library Mode When:

- ✅ Integrating into Python applications
- ✅ Building editor extensions
- ✅ Custom workflows and processing
- ✅ Test suite integration
- ✅ Advanced automation

### Use Docker Mode When:

- ✅ CI/CD pipelines
- ✅ Consistent environments needed
- ✅ Multiple projects with different configs
- ✅ No local Python installation
- ✅ Containerized infrastructure

## Hybrid Approaches

### CLI + Library

```python
# Use CLI for interactive, Library for automation
import subprocess
from src import Linter

def interactive_lint():
    """Run interactive CLI linting."""
    subprocess.run(['thai-lint', 'lint', 'file-placement', '.'])

def automated_lint():
    """Run automated library linting."""
    linter = Linter()
    violations = linter.lint('.')
    return violations

# Interactive development
if __name__ == "__main__":
    interactive_lint()

# CI/CD automation
def ci_lint():
    violations = automated_lint()
    if violations:
        exit(1)
```

### Docker + Library

```python
# Use Docker for CI, Library for local development
import os
from src import Linter

def lint():
    if os.environ.get('CI'):
        # In CI: Use Docker
        import subprocess
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}:/workspace',
            'thailint/thailint',
            'lint', 'file-placement', '/workspace'
        ])
    else:
        # Local: Use Library
        linter = Linter()
        violations = linter.lint('.')
        if violations:
            for v in violations:
                print(f"{v.file_path}: {v.message}")
```

### All Three Modes

```yaml
# Makefile with all modes

.PHONY: lint-cli lint-library lint-docker

# CLI mode (interactive)
lint-cli:
	thai-lint file-placement .

# Library mode (programmatic)
lint-library:
	python scripts/lint.py

# Docker mode (CI/CD)
lint-docker:
	docker run --rm -v $(PWD):/workspace \
		thailint/thailint lint file-placement /workspace

# Default to CLI for development
lint: lint-cli
```

## Environment-Specific Configuration

### Development

```bash
# CLI with dev config
thai-lint file-placement --config .thailint.dev.yaml .

# Library with dev config
linter = Linter(config_file='.thailint.dev.yaml')

# Docker with dev config
docker run --rm -v $(pwd):/workspace \
  thailint/thailint lint file-placement --config /workspace/.thailint.dev.yaml /workspace
```

### Production

```bash
# Strict production config
thai-lint file-placement --config .thailint.prod.yaml .

# CI/CD with production config
docker run --rm -v $(pwd):/workspace \
  thailint/thailint lint file-placement --config /workspace/.thailint.prod.yaml /workspace
```

## Performance Comparison

| Operation | CLI | Library | Docker |
|-----------|-----|---------|--------|
| Single file | ~20ms | ~15ms | ~50ms* |
| 100 files | ~300ms | ~250ms | ~350ms* |
| 1000 files | ~900ms | ~800ms | ~1000ms* |

*Docker includes container startup overhead (~30-50ms)

## Troubleshooting

### CLI Mode

**Issue: Command not found**
```bash
# Solution: Use python module
python -m src.cli lint file-placement .

# Or install in PATH
pip install -e .
```

### Library Mode

**Issue: No module named 'src'**
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=/path/to/thai-lint
python script.py
```

### Docker Mode

**Issue: Permission denied**
```bash
# Solution: Use user mapping
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd):/workspace \
  thailint/thailint lint file-placement /workspace
```

**Issue: Config not found**
```bash
# Solution: Ensure volume mount includes config
docker run --rm \
  -v $(pwd):/workspace \
  thailint/thailint lint file-placement --config /workspace/.thailint.yaml /workspace
```

## Next Steps

- **[Getting Started](getting-started.md)** - Quick start guide
- **[CLI Reference](cli-reference.md)** - Complete CLI documentation
- **[API Reference](api-reference.md)** - Library API documentation
- **[Configuration](configuration.md)** - Config file reference
- **[Examples](../examples/)** - Working code examples
