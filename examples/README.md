# thailint Library API Examples

**Purpose**: Usage examples for thailint library API

**Scope**: Programmatic usage patterns and integration examples

**Overview**: Collection of working examples demonstrating how to use thailint as a library
    in Python applications. Covers basic usage with the high-level Linter class, advanced
    patterns with direct linter imports, CI/CD integration with proper exit codes, and
    custom violation processing. Helps users integrate thailint into editors, testing
    frameworks, automation scripts, and continuous integration pipelines.

**Dependencies**: thailint library (src package)

**Exports**: Executable example scripts and documentation

**Related**: API documentation in docs/, PR_BREAKDOWN.md for implementation details

---

## Overview

This directory contains working examples demonstrating how to use thailint programmatically as a library.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Simple example showing the high-level Linter API:

```python
from src import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])
```

**Run it:**
```bash
python examples/basic_usage.py
```

### 2. Advanced Usage (`advanced_usage.py`)

Advanced patterns including:
- Direct linter imports
- Orchestrator usage
- Custom configuration
- Violation processing and grouping

```python
from src import Linter, Orchestrator, file_placement_lint

# Direct import
violations = file_placement_lint(Path("src/"), config)

# Orchestrator
orchestrator = Orchestrator(project_root=Path.cwd())
violations = orchestrator.lint_file(Path("src/api.py"))
```

**Run it:**
```bash
python examples/advanced_usage.py
```

### 3. CI/CD Integration (`ci_integration.py`)

Integration example for continuous integration pipelines:
- Proper exit codes (0=success, 1=violations, 2=error)
- JSON report generation
- Command-line interface

**Run it:**
```bash
python examples/ci_integration.py src/ --config .thailint.yaml
```

**GitHub Actions example:**
```yaml
- name: Lint with thailint
  run: |
    python examples/ci_integration.py src/

- name: Upload lint report
  uses: actions/upload-artifact@v3
  if: failure()
  with:
    name: lint-report
    path: lint-report.json
```

## API Quick Reference

### High-Level API (Recommended)

```python
from src import Linter

# Initialize
linter = Linter(config_file='.thailint.yaml')
linter = Linter(project_root='/path/to/project')

# Lint
violations = linter.lint('src/')                    # All rules
violations = linter.lint('src/', rules=['file-placement'])  # Specific rules
violations = linter.lint('file.py')                 # Single file
```

### Direct Linter Imports

```python
from src.linters import file_placement

config = {"allow": [r".*\.py$"]}
violations = file_placement.lint(Path("src/"), config)
```

### Advanced (Orchestrator)

```python
from src import Orchestrator

orchestrator = Orchestrator(project_root=Path.cwd())
violations = orchestrator.lint_file(Path("src/api.py"))
violations = orchestrator.lint_directory(Path("src/"), recursive=True)
```

## Violation Structure

All violations have these attributes:

```python
violation.rule_id       # str: Rule identifier (e.g., "file-placement")
violation.file_path     # Path: File where violation occurred
violation.message       # str: Human-readable description
violation.severity      # Severity: ERROR or WARNING
violation.to_dict()     # dict: Convert to dictionary
```

## Configuration

Linter supports YAML and JSON config files:

**`.thailint.yaml`:**
```yaml
rules:
  file-placement:
    allow:
      - ".*\\.py$"
    deny:
      - ".*test.*\\.py$"
```

**`.thailint.json`:**
```json
{
  "rules": {
    "file-placement": {
      "allow": [".*\\.py$"],
      "deny": [".*test.*\\.py$"]
    }
  }
}
```

## Use Cases

### 1. Pre-commit Hook
```python
from src import Linter

linter = Linter()
violations = linter.lint('.')
if violations:
    print("❌ Violations found, commit blocked")
    sys.exit(1)
```

### 2. Editor Integration
```python
from src import Linter

def lint_on_save(file_path):
    linter = Linter()
    violations = linter.lint(file_path)
    return violations  # Display in editor UI
```

### 3. Test Suite Integration
```python
from src import Linter

def test_no_violations():
    linter = Linter()
    violations = linter.lint('src/')
    assert len(violations) == 0, f"Found {len(violations)} violations"
```

## Next Steps

- See main README.md for installation instructions
- See docs/ for full API documentation
- See .thailint.yaml for configuration reference
- Run `thai-lint --help` for CLI usage
