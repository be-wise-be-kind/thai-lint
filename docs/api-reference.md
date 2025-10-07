# API Reference

**Purpose**: Complete API documentation for using thailint as a Python library

**Scope**: Linter class, Orchestrator, direct linter imports, and all programmatic interfaces

**Overview**: Comprehensive API reference for integrating thailint into Python applications, editors,
    CI/CD pipelines, and automation tools. Documents the high-level Linter class as the primary
    entry point, low-level Orchestrator for advanced control, direct linter imports for specific
    rules, and all supporting types and interfaces. Includes initialization options, method
    signatures, return types, exception handling, and practical usage examples for each API.

**Dependencies**: src package with Linter, Orchestrator, linter modules, and core types

**Exports**: API documentation for all public interfaces

**Related**: getting-started.md for basic usage, examples/ for working code samples

**Implementation**: Class and method documentation with type signatures, parameters, and examples

---

## Overview

thailint provides three levels of API for programmatic usage:

1. **High-Level API** (`Linter` class) - Recommended for most use cases
2. **Mid-Level API** (`Orchestrator` class) - Advanced control and rule management
3. **Low-Level API** (Direct linter imports) - Maximum flexibility

## High-Level API

### Linter Class

The `Linter` class is the primary entry point for library usage.

#### Import

```python
from src import Linter
```

#### Constructor

```python
Linter(
    config_file: str | Path | None = None,
    project_root: str | Path | None = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_file` | `str \| Path \| None` | `None` | Path to config file (`.thailint.yaml` or `.thailint.json`). If not provided, auto-discovers in project root. |
| `project_root` | `str \| Path \| None` | `Path.cwd()` | Root directory of project. Used for config discovery and path resolution. |

**Returns:** `Linter` instance

**Example:**

```python
from src import Linter
from pathlib import Path

# With config file
linter = Linter(config_file='.thailint.yaml')

# With project root (auto-discovers config)
linter = Linter(project_root='/path/to/project')

# With both
linter = Linter(
    config_file='/path/to/config.yaml',
    project_root='/path/to/project'
)

# Using defaults (current directory)
linter = Linter()
```

#### Methods

##### lint()

```python
Linter.lint(
    path: str | Path,
    rules: list[str] | None = None
) -> list[Violation]
```

Lint a file or directory.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | Required | File or directory to lint. Accepts string or `Path` object. |
| `rules` | `list[str] \| None` | `None` | Optional list of rule names to run. If `None`, runs all rules. |

**Returns:** `list[Violation]` - List of violations found

**Example:**

```python
from src import Linter

linter = Linter(config_file='.thailint.yaml')

# Lint directory with all rules
violations = linter.lint('src/')

# Lint file
violations = linter.lint('src/main.py')

# Lint with specific rules only
violations = linter.lint('src/', rules=['file-placement'])

# Using Path objects
from pathlib import Path
violations = linter.lint(Path('src/'))

# Process violations
for v in violations:
    print(f"{v.file_path}: {v.message}")
```

**Exit Behavior:**
- Returns empty list `[]` if path doesn't exist
- Automatically recurses through directories
- Filters violations by rule names if `rules` parameter provided

### Complete Linter Example

```python
from src import Linter
from pathlib import Path

def lint_project():
    """Lint entire project with file placement rules."""
    # Initialize linter
    linter = Linter(config_file='.thailint.yaml')

    # Lint project
    violations = linter.lint('.', rules=['file-placement'])

    # Report results
    if violations:
        print(f"Found {len(violations)} violations:\n")
        for v in violations:
            print(f"  {v.file_path}")
            print(f"    Rule: {v.rule_id}")
            print(f"    Message: {v.message}")
            print(f"    Severity: {v.severity.name}")
            print()
        return 1  # Exit code for violations
    else:
        print("No violations found!")
        return 0  # Success

if __name__ == "__main__":
    import sys
    sys.exit(lint_project())
```

## Mid-Level API

### Orchestrator Class

The `Orchestrator` provides lower-level control over linting operations.

#### Import

```python
from src import Orchestrator
# Or
from src.orchestrator.core import Orchestrator
```

#### Constructor

```python
Orchestrator(
    project_root: Path | None = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_root` | `Path \| None` | `Path.cwd()` | Root directory of project for rule discovery and context. |

**Example:**

```python
from src import Orchestrator
from pathlib import Path

# With project root
orchestrator = Orchestrator(project_root=Path('/path/to/project'))

# Using current directory
orchestrator = Orchestrator()
```

#### Methods

##### lint_file()

```python
Orchestrator.lint_file(
    file_path: Path
) -> list[Violation]
```

Lint a single file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `Path` | Path to file to lint (must be `Path` object) |

**Returns:** `list[Violation]` - Violations found in file

**Example:**

```python
from src import Orchestrator
from pathlib import Path

orchestrator = Orchestrator()

# Lint single file
violations = orchestrator.lint_file(Path('src/main.py'))

for v in violations:
    print(f"{v.rule_id}: {v.message}")
```

##### lint_directory()

```python
Orchestrator.lint_directory(
    dir_path: Path,
    recursive: bool = True
) -> list[Violation]
```

Lint all files in a directory.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dir_path` | `Path` | Required | Directory path (must be `Path` object) |
| `recursive` | `bool` | `True` | Recursively scan subdirectories |

**Returns:** `list[Violation]` - Violations found in directory

**Example:**

```python
from src import Orchestrator
from pathlib import Path

orchestrator = Orchestrator()

# Recursive scan (default)
violations = orchestrator.lint_directory(Path('src/'))

# Non-recursive (top-level only)
violations = orchestrator.lint_directory(Path('src/'), recursive=False)
```

### Complete Orchestrator Example

```python
from src import Orchestrator
from pathlib import Path

def advanced_linting():
    """Advanced linting with Orchestrator."""
    orchestrator = Orchestrator(project_root=Path.cwd())

    # Lint specific files
    api_violations = orchestrator.lint_file(Path('src/api.py'))
    config_violations = orchestrator.lint_file(Path('src/config.py'))

    # Lint directories non-recursively
    src_violations = orchestrator.lint_directory(Path('src/'), recursive=False)
    test_violations = orchestrator.lint_directory(Path('tests/'), recursive=True)

    # Combine results
    all_violations = api_violations + config_violations + src_violations + test_violations

    # Group by file
    by_file = {}
    for v in all_violations:
        file = str(v.file_path)
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(v)

    # Report
    for file, violations in by_file.items():
        print(f"{file}: {len(violations)} violations")

if __name__ == "__main__":
    advanced_linting()
```

## Low-Level API

### Direct Linter Imports

Import and use specific linters directly.

#### File Placement Linter

```python
from src import file_placement_lint
# Or
from src.linters.file_placement import lint as file_placement_lint
```

**Function Signature:**

```python
file_placement_lint(
    path: Path,
    config: dict
) -> list[Violation]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | File or directory to lint |
| `config` | `dict` | Configuration dictionary with allow/deny patterns |

**Returns:** `list[Violation]`

**Example:**

```python
from src import file_placement_lint
from pathlib import Path

# Define config
config = {
    "allow": [r".*\.py$"],
    "deny": [r"test_.*\.py$"],
    "ignore": ["__pycache__/", "*.pyc"]
}

# Run linter
violations = file_placement_lint(Path('src/'), config)

# Process results
for v in violations:
    print(f"{v.file_path}: {v.message}")
```

## Core Types

### Violation

Represents a linting violation.

#### Import

```python
from src.core.types import Violation
```

#### Attributes

```python
@dataclass
class Violation:
    rule_id: str          # Rule identifier (e.g., "file-placement")
    file_path: Path       # File where violation occurred
    message: str          # Human-readable description
    severity: Severity    # ERROR or WARNING (currently only ERROR used)
```

#### Methods

##### to_dict()

```python
Violation.to_dict() -> dict
```

Convert violation to dictionary (useful for JSON serialization).

**Returns:**

```python
{
    "rule_id": "file-placement",
    "file_path": "src/test_example.py",
    "message": "Test files should be in tests/",
    "severity": "ERROR"
}
```

**Example:**

```python
from src import Linter
import json

linter = Linter()
violations = linter.lint('src/')

# Convert to JSON
violations_json = json.dumps(
    [v.to_dict() for v in violations],
    indent=2,
    default=str  # Handle Path objects
)
print(violations_json)
```

### Severity

Enum for violation severity levels.

#### Import

```python
from src.core.types import Severity
```

#### Values

```python
class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
```

**Note:** Currently only `ERROR` is used (binary severity model).

**Example:**

```python
from src import Linter
from src.core.types import Severity

linter = Linter()
violations = linter.lint('src/')

# Filter by severity
errors = [v for v in violations if v.severity == Severity.ERROR]
warnings = [v for v in violations if v.severity == Severity.WARNING]

print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
```

## Configuration Loading

### LinterConfigLoader

Load configuration files programmatically.

#### Import

```python
from src.linter_config.loader import LinterConfigLoader
```

#### Usage

```python
from src.linter_config.loader import LinterConfigLoader
from pathlib import Path

loader = LinterConfigLoader()

# Load config file
config = loader.load(Path('.thailint.yaml'))

# Access config
print(config.get('directories'))
print(config.get('ignore'))
```

## Exception Handling

### Common Exceptions

```python
from src import Linter
from pathlib import Path

try:
    linter = Linter(config_file='nonexistent.yaml')
    violations = linter.lint('src/')
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Error Handling Best Practices

```python
from src import Linter
from pathlib import Path
import sys

def safe_lint(path: str, config_file: str | None = None) -> int:
    """Safely lint with error handling.

    Returns:
        0: Success (no violations)
        1: Violations found
        2: Error occurred
    """
    try:
        # Initialize linter
        linter = Linter(config_file=config_file) if config_file else Linter()

        # Lint path
        violations = linter.lint(path)

        # Report violations
        if violations:
            print(f"Found {len(violations)} violations")
            for v in violations:
                print(f"  {v.file_path}: {v.message}")
            return 1

        print("No violations found")
        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: Invalid configuration - {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    exit_code = safe_lint('src/', '.thailint.yaml')
    sys.exit(exit_code)
```

## Integration Examples

### Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook for thailint."""

from src import Linter
import sys

def main():
    linter = Linter(config_file='.thailint.yaml')
    violations = linter.lint('.')

    if violations:
        print("❌ Linting failed - violations found:")
        for v in violations:
            print(f"  {v.file_path}: {v.message}")
        return 1

    print("✅ Linting passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Editor Integration (VS Code)

```python
"""VS Code extension integration example."""

from src import Linter
from pathlib import Path
from typing import List, Dict

class ThailintProvider:
    """Linting provider for VS Code."""

    def __init__(self):
        self.linter = Linter()

    def lint_file(self, file_path: str) -> List[Dict]:
        """Lint single file for editor."""
        violations = self.linter.lint(file_path)

        # Convert to VS Code diagnostic format
        diagnostics = []
        for v in violations:
            diagnostics.append({
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 0}
                },
                "message": v.message,
                "severity": 1 if v.severity.name == "ERROR" else 2,
                "source": "thailint"
            })

        return diagnostics

    def lint_on_save(self, file_path: str):
        """Lint when file is saved."""
        diagnostics = self.lint_file(file_path)
        # Send diagnostics to VS Code
        return diagnostics
```

### Test Suite Integration

```python
"""Pytest integration example."""

import pytest
from src import Linter

@pytest.fixture
def linter():
    """Create linter instance for tests."""
    return Linter(config_file='tests/.thailint.yaml')

def test_no_violations_in_src(linter):
    """Test that src/ has no violations."""
    violations = linter.lint('src/', rules=['file-placement'])
    assert len(violations) == 0, f"Found {len(violations)} violations in src/"

def test_no_violations_in_tests(linter):
    """Test that tests/ has no violations."""
    violations = linter.lint('tests/', rules=['file-placement'])
    assert len(violations) == 0, f"Found {len(violations)} violations in tests/"

def test_specific_file(linter):
    """Test specific file compliance."""
    violations = linter.lint('src/main.py')
    assert len(violations) == 0, f"main.py has violations: {violations[0].message}"
```

### CI/CD Integration (GitHub Actions)

```python
#!/usr/bin/env python3
"""GitHub Actions integration script."""

import json
import sys
from pathlib import Path
from src import Linter

def main():
    """Run linting for GitHub Actions."""
    linter = Linter(config_file='.thailint.yaml')
    violations = linter.lint('.')

    if violations:
        # Write GitHub Actions annotations
        for v in violations:
            # Format: ::error file={file},line={line}::{message}
            print(f"::error file={v.file_path}::{v.message}")

        # Write JSON report for artifact
        report_data = [v.to_dict() for v in violations]
        Path('lint-report.json').write_text(
            json.dumps(report_data, indent=2, default=str)
        )

        print(f"\n❌ Found {len(violations)} violations")
        return 1

    print("✅ Linting passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Type Hints and MyPy

All APIs are fully typed and compatible with MyPy strict mode.

```python
from typing import List
from pathlib import Path
from src import Linter
from src.core.types import Violation

def lint_with_types(path: str, config: str | None = None) -> List[Violation]:
    """Type-safe linting function."""
    linter: Linter = Linter(config_file=config)
    violations: List[Violation] = linter.lint(path)
    return violations

# MyPy will catch type errors
violations: List[Violation] = lint_with_types('src/', '.thailint.yaml')
```

## API Migration Guide

### From Direct Imports to Linter API

**Before (direct import):**

```python
from src.linters.file_placement import lint
from pathlib import Path

config = {"allow": [".*\\.py$"]}
violations = lint(Path("src/"), config)
```

**After (Linter API):**

```python
from src import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])
```

### From Orchestrator to Linter

**Before (Orchestrator):**

```python
from src.orchestrator.core import Orchestrator
from pathlib import Path

orchestrator = Orchestrator(project_root=Path.cwd())
violations = orchestrator.lint_directory(Path('src/'), recursive=True)
```

**After (Linter):**

```python
from src import Linter

linter = Linter()
violations = linter.lint('src/')  # Automatically recursive
```

## API Best Practices

1. **Use the Linter class for most use cases** - Simplest and most maintainable
2. **Use Orchestrator for advanced control** - When you need fine-grained file/directory control
3. **Use direct imports sparingly** - Only when you need maximum customization
4. **Always handle exceptions** - Especially FileNotFoundError and ValueError
5. **Use Path objects consistently** - More robust than strings
6. **Filter by rules when possible** - Better performance: `lint(path, rules=['file-placement'])`
7. **Process violations in batches** - Group by file or rule for better reporting

## Next Steps

- **[Getting Started](getting-started.md)** - Basic library usage
- **[Examples](../examples/)** - Working code examples
- **[CLI Reference](cli-reference.md)** - Command-line interface
- **[Configuration](configuration.md)** - Config file reference
