# File Placement Linter Guide

**Purpose**: Complete guide to the file placement linter including rules, patterns, and best practices

**Scope**: File placement rule system, pattern matching, directory scoping, and configuration

**Overview**: Comprehensive documentation for the file placement linter that enforces project structure
    conventions and file organization rules. Covers the rule system, regex pattern matching, allow/deny
    precedence, directory-specific scoping, ignore directives, and violation detection. Includes
    practical examples for common project layouts (Python, TypeScript, monorepo), troubleshooting
    guides, and best practices for maintaining clean project structure.

**Dependencies**: File placement linter implementation, pattern matching engine, configuration system

**Exports**: Linter usage documentation and configuration examples

**Related**: configuration.md for config reference, getting-started.md for basic usage

**Implementation**: Rule documentation with examples, pattern guides, and troubleshooting

---

## Overview

The file placement linter enforces project structure by ensuring files are located in appropriate directories based on configurable rules and patterns. It helps maintain consistent organization across your codebase.

## How It Works

### Rule System

The file placement linter uses a three-level rule hierarchy:

1. **Global Patterns** - Apply to entire project
2. **Directory Rules** - Apply within specific directories
3. **Ignore Patterns** - Skip specific files/directories

### Pattern Matching

Files are matched against regex patterns:

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"        # Allow Python files
    deny:
      - "test_.*\\.py$"   # Deny test files
```

### Precedence Rules

1. **Deny overrides allow**: If a file matches both allow and deny, it's denied
2. **Directory overrides global**: Directory-specific rules take precedence
3. **Ignore overrides all**: Ignored files skip all checks

## Basic Configuration

### Minimal Setup

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"  # Only Python files in src/

  tests:
    allow:
      - "test_.*\\.py$"  # Only test files in tests/
```

### With Global Rules

```yaml
global_patterns:
  deny:
    - pattern: "^(?!src/|tests/).*\\.py$"
      message: "Python files must be in src/ or tests/"

directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"
```

### With Ignore Patterns

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"

ignore:
  - "__pycache__/"
  - "*.pyc"
  - ".venv/"
```

## Rule Types

### Allow Rules

Explicitly permit file patterns.

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"           # Python source files
      - ".*\\.pyi$"          # Type stub files
      - "__init__\\.py$"     # Package initializers
```

**Behavior**: Files matching allow patterns are permitted

### Deny Rules

Explicitly forbid file patterns.

```yaml
directories:
  src:
    deny:
      - "test_.*\\.py$"      # No test files
      - ".*_test\\.py$"      # No test files (suffix)
      - ".*\\.tmp$"          # No temp files
      - ".*\\.bak$"          # No backup files
```

**Behavior**: Files matching deny patterns trigger violations

### Allow + Deny (Deny Wins)

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"           # Allow all Python files
    deny:
      - "test_.*\\.py$"      # But deny test files

    # Result: All Python files allowed EXCEPT test files
```

## Directory Scoping

### Single Directory

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"
```

Applies to: `src/`, `src/utils/`, `src/api/`, etc. (recursive)

### Multiple Directories

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*"

  tests:
    allow:
      - "test_.*\\.py$"
      - "conftest\\.py$"

  scripts:
    allow:
      - ".*\\.py$"
      - ".*\\.sh$"
```

### Nested Directories

```yaml
directories:
  src/api:
    allow:
      - ".*_api\\.py$"      # API endpoints only
      - "__init__\\.py$"

  src/models:
    allow:
      - ".*_model\\.py$"    # Models only
      - "__init__\\.py$"

  src/utils:
    allow:
      - ".*\\.py$"          # Any Python file
```

## Pattern Syntax

### Basic Patterns

```yaml
# File extensions
".*\\.py$"           # .py files
".*\\.js$"           # .js files
".*\\.(ts|tsx)$"     # .ts or .tsx files

# Naming prefixes
"test_.*"            # Files starting with test_
"^test_.*\\.py$"     # Python files starting with test_

# Naming suffixes
".*_test\\.py$"      # Python files ending with _test
".*\\.test\\.ts$"    # TypeScript test files

# Exact matches
"conftest\\.py$"     # Exactly conftest.py
"__init__\\.py$"     # Exactly __init__.py
```

### Advanced Patterns

```yaml
# Path patterns
"^src/.*\\.py$"                # Python files in src/
"^(?!src/).*\\.py$"            # Python files NOT in src/
"^(src|lib)/.*\\.py$"          # Python files in src/ OR lib/

# Character classes
"[A-Z].*\\.py$"                # Files starting with uppercase
"[a-z_][a-z0-9_]*\\.py$"       # Snake case files

# Negation
"^(?!test_|.*_test).*\\.py$"   # Python files NOT starting with test_ or ending with _test

# Complex patterns
"^src/(api|models)/.*\\.py$"   # Python files in src/api/ or src/models/
```

### Pattern Examples

```yaml
directories:
  src/components:
    # React components: PascalCase.tsx
    allow:
      - "^[A-Z][a-zA-Z0-9]*\\.tsx$"
      - "index\\.tsx?$"

  src/utils:
    # Utilities: snake_case.py
    allow:
      - "^[a-z][a-z0-9_]*\\.py$"

  src/api:
    # API endpoints: *_api.py
    allow:
      - ".*_api\\.py$"
      - "__init__\\.py$"
```

## Common Configurations

### Python Project

```yaml
global_patterns:
  deny:
    - pattern: "^(?!src/|tests/|scripts/).*\\.py$"
      message: "Python files must be in src/, tests/, or scripts/"

directories:
  src:
    allow:
      - ".*\\.py$"
      - "__init__\\.py$"
    deny:
      - "test_.*\\.py$"
      - ".*_test\\.py$"

  tests:
    allow:
      - "test_.*\\.py$"
      - ".*_test\\.py$"
      - "conftest\\.py$"
      - "__init__\\.py$"

  scripts:
    allow:
      - ".*\\.py$"
      - ".*\\.sh$"

ignore:
  - "__pycache__/"
  - "*.pyc"
  - ".venv/"
  - ".pytest_cache/"
  - "*.egg-info/"
```

### TypeScript/React Project

```yaml
global_patterns:
  deny:
    - pattern: "^(?!src/|tests/).*\\.(ts|tsx|js|jsx)$"
      message: "Code files must be in src/ or tests/"

directories:
  src/components:
    allow:
      - "^[A-Z][a-zA-Z0-9]*\\.tsx$"  # PascalCase components
      - "index\\.tsx?$"
      - ".*\\.module\\.css$"
    deny:
      - ".*\\.test\\.tsx$"
      - ".*\\.spec\\.tsx$"

  src/utils:
    allow:
      - ".*\\.(ts|js)$"
    deny:
      - ".*\\.test\\.(ts|js)$"

  tests:
    allow:
      - ".*\\.test\\.(ts|tsx)$"
      - ".*\\.spec\\.(ts|tsx)$"
      - "setup\\.ts$"

ignore:
  - "node_modules/"
  - "dist/"
  - "build/"
  - "*.d.ts"
```

### Monorepo

```yaml
directories:
  # Backend service
  services/api/src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*"

  services/api/tests:
    allow:
      - "test_.*\\.py$"

  # Frontend app
  apps/web/src:
    allow:
      - ".*\\.(tsx?|jsx?|css)$"
    deny:
      - ".*\\.(test|spec)\\."

  apps/web/tests:
    allow:
      - ".*\\.(test|spec)\\.(tsx?|jsx?)$"

  # Shared packages
  packages/shared:
    allow:
      - ".*\\.(ts|js|py)$"

ignore:
  - "**/node_modules/"
  - "**/__pycache__/"
  - "**/dist/"
  - "**/build/"
```

## Running the Linter

### CLI

```bash
# Basic
thai-lint file-placement .

# With config
thai-lint file-placement --config .thailint.yaml .

# Specific directory
thai-lint file-placement src/

# Non-recursive
thai-lint file-placement --no-recursive src/

# JSON output
thai-lint file-placement --format json .
```

### Library

```python
from src import Linter

linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])

for v in violations:
    print(f"{v.file_path}: {v.message}")
```

### Docker

```bash
docker run --rm -v $(pwd):/workspace \
  washad/thailint lint file-placement /workspace
```

## Understanding Violations

### Violation Structure

Each violation contains:

```python
violation.rule_id      # "file-placement"
violation.file_path    # Path to violating file
violation.message      # Description of violation
violation.severity     # Severity.ERROR
```

### Example Violation

```
src/test_example.py:
  Rule: file-placement
  Message: Test files should be in tests/ directory
  Severity: ERROR
```

### Custom Messages

```yaml
global_patterns:
  deny:
    - pattern: "secret.*"
      message: "Files containing 'secret' are forbidden for security"

    - pattern: ".*\\.bak$"
      message: "Backup files (.bak) should not be committed"
```

## Violation Resolution

### 1. Move File

```bash
# Violation: src/test_example.py
# Message: Test files should be in tests/

# Fix: Move to tests/
mv src/test_example.py tests/test_example.py
```

### 2. Rename File

```bash
# Violation: src/api/handler.py
# Message: API files should end with _api.py

# Fix: Rename file
mv src/api/handler.py src/api/handler_api.py
```

### 3. Update Config

```yaml
# If file placement is intentional, update config

directories:
  src:
    allow:
      - ".*\\.py$"
      - "setup\\.py$"  # Add exception for setup.py
```

### 4. Add to Ignore

```yaml
# If file should be ignored

ignore:
  - "src/generated/*"  # Ignore generated files
  - "src/legacy/*"     # Ignore legacy code
```

## Debugging

### Verbose Mode

```bash
thai-lint --verbose lint file-placement .
```

Output:
```
2025-10-06 12:34:56 | DEBUG | Loading config from .thailint.yaml
2025-10-06 12:34:56 | DEBUG | Scanning directory: src/
2025-10-06 12:34:56 | DEBUG | Checking file: src/main.py
2025-10-06 12:34:56 | DEBUG | Pattern '.*\.py$' matches: True
2025-10-06 12:34:56 | DEBUG | Pattern 'test_.*' matches: False
2025-10-06 12:34:56 | DEBUG | File allowed: src/main.py
```

### Test Patterns

```python
import re

pattern = r"^(?!src/|tests/).*\.py$"
test_files = ["main.py", "src/api.py", "tests/test_api.py"]

for file in test_files:
    match = re.match(pattern, file)
    print(f"{file}: {'MATCH' if match else 'NO MATCH'}")
```

Output:
```
main.py: MATCH
src/api.py: NO MATCH
tests/test_api.py: NO MATCH
```

### Validate Config

```bash
# Check config syntax
python -c "import yaml; yaml.safe_load(open('.thailint.yaml'))"

# Show loaded config
thai-lint config show --format yaml
```

## Best Practices

### 1. Start Simple

```yaml
# Begin with basic rules
directories:
  src:
    allow:
      - ".*\\.py$"

# Expand gradually
directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"
```

### 2. Use Meaningful Messages

```yaml
global_patterns:
  deny:
    # Bad: Generic message
    - pattern: ".*secret.*"
      message: "Not allowed"

    # Good: Specific, actionable message
    - pattern: ".*secret.*"
      message: "Files containing 'secret' are forbidden. Use environment variables instead."
```

### 3. Document Complex Patterns

```yaml
directories:
  src/api:
    # API endpoints must follow naming convention: <resource>_api.py
    # Examples: user_api.py, product_api.py
    allow:
      - ".*_api\\.py$"
      - "__init__\\.py$"
```

### 4. Test Before Enforcing

```bash
# Test on subset
thai-lint file-placement src/

# Review violations
thai-lint file-placement . --format json | jq

# Then enforce in CI
```

### 5. Use Ignore Wisely

```yaml
ignore:
  # Good: Generated or temporary files
  - "__pycache__/"
  - "*.pyc"
  - "dist/"

  # Avoid: Hiding real issues
  # - "src/legacy/"  # Fix instead of ignoring
```

## Troubleshooting

### Issue: No Violations Detected

**Cause**: Pattern doesn't match files

**Solution**:
1. Check pattern syntax
2. Test pattern with Python regex
3. Use verbose mode
4. Verify config is loaded

```bash
# Debug
thai-lint --verbose lint file-placement .

# Test pattern
python -c "import re; print(re.match(r'.*\.py$', 'test.py'))"
```

### Issue: Too Many Violations

**Cause**: Overly strict rules

**Solution**:
1. Add specific exceptions
2. Use ignore patterns
3. Refine regex patterns

```yaml
# Before: Too strict
directories:
  src:
    deny:
      - ".*"  # Denies everything

# After: More specific
directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"
```

### Issue: Pattern Not Working as Expected

**Cause**: Regex escaping or precedence

**Solution**:
```yaml
# Wrong: Dot matches any character
allow:
  - "file.py"  # Matches "file.py" AND "fileXpy"

# Correct: Escape dot
allow:
  - "file\\.py$"  # Matches only "file.py"

# Wrong: Deny doesn't work
allow:
  - ".*\\.py$"
deny:
  - "test.*"  # test.* matches "test", not "test_file.py"

# Correct: More specific deny
allow:
  - ".*\\.py$"
deny:
  - "test_.*\\.py$"  # Matches "test_file.py"
```

### Issue: Directory Rules Not Applied

**Cause**: Path mismatch or wrong directory name

**Solution**:
```yaml
# Check exact directory names
# Run with --verbose to see actual paths

# Wrong: Doesn't match subdirectories
directories:
  src:  # Matches src/ but not src/api/

# Correct: Matches all under src/
directories:
  src:  # Automatically matches src/ and all subdirectories
```

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

thai-lint file-placement .
if [ $? -ne 0 ]; then
    echo "File placement violations found"
    echo "Fix violations or use 'git commit --no-verify'"
    exit 1
fi
```

### CI/CD (GitHub Actions)

```yaml
- name: Check file placement
  run: |
    thai-lint file-placement . --format json > placement-report.json
    if [ $? -ne 0 ]; then
      echo "::error::File placement violations found"
      jq -r '.[] | "::error file=\(.file_path)::\(.message)"' placement-report.json
      exit 1
    fi
```

### VS Code Task

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check File Placement",
      "type": "shell",
      "command": "thai-lint file-placement .",
      "problemMatcher": [],
      "group": {
        "kind": "test",
        "isDefault": true
      }
    }
  ]
}
```

## Next Steps

- **[Configuration](configuration.md)** - Complete config reference
- **[CLI Reference](cli-reference.md)** - CLI commands and options
- **[API Reference](api-reference.md)** - Programmatic usage
- **[Getting Started](getting-started.md)** - Quick start guide
