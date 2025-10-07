# Getting Started with thailint

**Purpose**: Quick start guide for installing and using thailint for the first time

**Scope**: Installation methods, basic usage, and initial configuration for new users

**Overview**: Comprehensive getting started guide covering all installation methods (pip, source, Docker),
    basic usage patterns for CLI and library modes, and initial configuration setup. Walks users through
    their first linting operation with practical examples and troubleshooting tips. Provides quickstart
    paths for different use cases including CI/CD integration, local development, and containerized
    deployments. Helps users understand core concepts and get productive quickly.

**Dependencies**: Python 3.11+, pip or Poetry, Docker (optional)

**Exports**: Installation and usage instructions for thailint

**Related**: configuration.md for detailed config options, cli-reference.md for all CLI commands,
    api-reference.md for programmatic usage

**Implementation**: Step-by-step tutorial format with code examples and expected outputs

---

## Overview

thailint is an enterprise-ready multi-language linter designed for AI-generated code. It helps enforce project structure, file placement rules, and coding standards across Python, TypeScript, and other languages.

## Prerequisites

- **Python 3.11 or higher**
- **pip** (for PyPI installation) or **Poetry** (for source installation)
- **Docker** (optional, for containerized usage)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install thailint
```

Verify installation:

```bash
thai-lint --version
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/thai-lint.git
cd thai-lint

# Install with Poetry
poetry install

# Or install with pip
pip install -e .
```

### Option 3: Use Docker

```bash
# Pull image (when published)
docker pull thailint/thailint:latest

# Or build locally
docker build -t thailint/thailint .
```

## Quick Start

### 1. Your First Lint

Lint the current directory for file placement issues:

```bash
thai-lint file-placement .
```

**Expected output:**
```
✅ No violations found
```

Or with violations:
```
❌ Found 2 violations:
  src/test_example.py: Test files should be in tests/ directory
  config.py: Python files should be in src/ directory
```

### 2. Lint a Specific Directory

```bash
# Lint only the src/ directory
thai-lint file-placement src/

# Lint recursively (default)
thai-lint file-placement --recursive src/

# Lint non-recursively
thai-lint file-placement --no-recursive src/
```

### 3. Using a Configuration File

Create a `.thailint.yaml` file in your project root:

```yaml
rules:
  file-placement:
    allow:
      - ".*\\.py$"        # Allow Python files
    deny:
      - "test_.*\\.py$"   # Deny test files (should be in tests/)

ignore:
  - "__pycache__/"
  - "*.pyc"
  - ".venv/"
```

Then run:

```bash
thai-lint file-placement . --config .thailint.yaml
```

### 4. Using Inline Rules

For quick testing without a config file:

```bash
thai-lint file-placement . --rules '{"allow": [".*\\.py$"], "deny": ["test_.*"]}'
```

### 5. Get JSON Output

For CI/CD integration or programmatic parsing:

```bash
thai-lint file-placement . --format json
```

**Output:**
```json
[
  {
    "file_path": "src/test_example.py",
    "rule_id": "file-placement",
    "message": "Test files should be in tests/ directory",
    "severity": "ERROR"
  }
]
```

## Using as a Library

### Basic Library Usage

```python
from src import Linter

# Initialize linter
linter = Linter(config_file='.thailint.yaml')

# Lint a directory
violations = linter.lint('src/', rules=['file-placement'])

# Process violations
if violations:
    print(f"Found {len(violations)} violations:")
    for v in violations:
        print(f"  {v.file_path}: {v.message}")
else:
    print("No violations found!")
```

### Without Config File

```python
from src import Linter

# Linter will auto-discover .thailint.yaml or .thailint.json in project root
linter = Linter()

# Lint current directory
violations = linter.lint('.')
```

See [API Reference](api-reference.md) for complete library documentation.

## Using with Docker

### Docker Run (Quick Test)

```bash
# Show help
docker run --rm thailint/thailint --help

# Lint current directory (mount as volume)
docker run --rm -v $(pwd):/workspace thailint/thailint lint file-placement /workspace
```

### Docker Compose (Development)

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

See [Deployment Modes](deployment-modes.md) for detailed Docker usage.

## Configuration Basics

### Config File Locations

thailint looks for config files in this order:

1. File specified with `--config` flag
2. `.thailint.yaml` in current directory
3. `.thailint.json` in current directory
4. `.thailint.yaml` in project root

### Simple Configuration Example

**`.thailint.yaml`:**

```yaml
# Global patterns (apply everywhere)
global_patterns:
  deny:
    - pattern: '^(?!src/|tests/).*\\.py$'
      message: "Python files should be in src/ or tests/"

# Directory-specific rules
directories:
  src:
    allow:
      - '.*\\.py$'
    deny:
      - 'test_.*\\.py$'

  tests:
    allow:
      - 'test_.*\\.py$'
      - 'conftest\\.py$'

# Ignore patterns
ignore:
  - "__pycache__/"
  - "*.pyc"
  - ".venv/"
```

**JSON equivalent (`.thailint.json`):**

```json
{
  "global_patterns": {
    "deny": [
      {
        "pattern": "^(?!src/|tests/).*\\.py$",
        "message": "Python files should be in src/ or tests/"
      }
    ]
  },
  "directories": {
    "src": {
      "allow": [".*\\.py$"],
      "deny": ["test_.*\\.py$"]
    },
    "tests": {
      "allow": ["test_.*\\.py$", "conftest\\.py$"]
    }
  },
  "ignore": ["__pycache__/", "*.pyc", ".venv/"]
}
```

See [Configuration Reference](configuration.md) for all available options.

## Common Use Cases

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: thailint
        name: thailint file placement
        entry: thai-lint file-placement
        language: python
        pass_filenames: false
        always_run: true
```

### CI/CD Integration (GitHub Actions)

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Run linter
        run: thai-lint file-placement .
```

### VS Code Integration

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Lint with thailint",
      "type": "shell",
      "command": "thai-lint file-placement .",
      "group": {
        "kind": "test",
        "isDefault": true
      }
    }
  ]
}
```

Run with `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac).

## Exit Codes

thailint uses standard exit codes for CI/CD integration:

- **0**: No violations found (success)
- **1**: Violations found (linting failed)
- **2**: Error occurred (invalid config, file not found, etc.)

Example CI script:

```bash
#!/bin/bash
thai-lint file-placement .
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Linting passed"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "❌ Linting failed - violations found"
    exit 1
elif [ $EXIT_CODE -eq 2 ]; then
    echo "❌ Linting error - check configuration"
    exit 2
fi
```

## Troubleshooting

### Common Issues

**Issue: "No module named 'src'"**

When running examples, set PYTHONPATH:

```bash
PYTHONPATH=/path/to/thai-lint python examples/basic_usage.py
```

**Issue: "Config file not found"**

Ensure `.thailint.yaml` or `.thailint.json` exists in:
- Current directory, or
- Project root, or
- Specify explicitly with `--config`

**Issue: "Permission denied" in Docker**

Use user mapping:

```bash
docker run --rm --user $(id -u):$(id -g) -v $(pwd):/workspace thailint/thailint lint file-placement /workspace
```

**Issue: No violations detected**

1. Check your config file is valid YAML/JSON
2. Verify patterns use correct regex syntax
3. Run with `--verbose` flag for debug output:
   ```bash
   thai-lint --verbose lint file-placement .
   ```

## Next Steps

- **[Configuration Reference](configuration.md)** - Learn all configuration options
- **[CLI Reference](cli-reference.md)** - Complete CLI command documentation
- **[API Reference](api-reference.md)** - Use thailint as a library
- **[File Placement Linter](file-placement-linter.md)** - Detailed linter guide
- **[Deployment Modes](deployment-modes.md)** - CLI, Library, and Docker usage

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` for working code

## Quick Reference

```bash
# Basic linting
thai-lint file-placement .

# With config
thai-lint file-placement --config .thailint.yaml .

# JSON output
thai-lint file-placement --format json .

# Inline rules
thai-lint file-placement --rules '{"allow": [".*\\.py$"]}' .

# Show help
thai-lint --help
thai-lint lint --help
thai-lint file-placement --help
```
