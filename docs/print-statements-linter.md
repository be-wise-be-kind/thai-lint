# Print Statements Linter

!!! warning "Deprecated - Use improper-logging"
    The `print-statements` command has been renamed to `improper-logging`. The new command includes additional features like conditional verbose detection. See **[Improper Logging Linter](improper-logging-linter.md)** for the updated documentation.

    **Migration:**
    - Replace `thailint print-statements` with `thailint improper-logging`
    - The old command continues to work as an alias
    - Configuration key `print-statements:` is still supported
    - Rule ID `print-statements.detected` is aliased to `improper-logging.print-statement`

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the print statements linter for detecting debug print and console statements that should be replaced with proper logging

    **Scope**: Configuration, usage, language support, and best practices for print/console statement detection

    **Overview**: Comprehensive documentation for the print statements linter that detects print() calls in Python and console.* calls in TypeScript/JavaScript. Covers how the linter works using AST analysis for Python and tree-sitter for TypeScript, configuration options including allow_in_scripts and console_methods, CLI and library usage, ignore patterns, and integration with CI/CD pipelines. Helps teams maintain production-ready code by replacing debug statements with proper logging.

    **Dependencies**: Python AST (Python), tree-sitter (TypeScript/JavaScript)

    **Exports**: Usage documentation, configuration examples, violation messages, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: AST-based analysis for Python print() calls, tree-sitter for TypeScript/JavaScript console.* methods

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint print-statements src/
```

**Example output:**
```
src/handlers.py:42 - print() call found - use logging instead
  Suggestion: Replace print("Debug: user={user}") with logger.debug("user=%s", user)
```

**Fix it:** Replace print statements with proper logging calls.

---

## Overview

The print statements linter detects `print()` calls in Python and `console.*` calls in TypeScript/JavaScript that should be replaced with proper logging. These debug statements are common in development but should not appear in production code.

### Why Detect Print Statements?

Print statements are problematic in production code for several reasons:

- **No log levels**: `print()` doesn't distinguish between debug, info, warning, and error messages
- **No timestamps**: Logs lack timing information for debugging issues
- **No context**: Missing file, line, and function context that logging provides
- **Performance**: Unbuffered I/O can slow down applications
- **Security**: Sensitive data may be accidentally exposed
- **Professionalism**: Print statements signal incomplete code review

### What It Detects

**Python:**
```python
# Detected (violations)
print("Debug message")
print(f"User data: {user}")
print("Processing...", end="")

# Not detected (allowed)
logging.info("Debug message")
logger.debug(f"User data: {user}")
```

**TypeScript/JavaScript:**
```typescript
// Detected (violations)
console.log("Debug message");
console.warn("Warning!");
console.error("Error occurred");
console.debug("Debug info");
console.info("Information");

// Not detected (allowed)
logger.info("Debug message");
winston.warn("Warning!");
```

### AI-Generated Code Pattern

AI coding assistants frequently add print statements for debugging:

```python
# Common AI pattern - quick debugging
def process_data(items):
    print(f"Processing {len(items)} items")  # AI debugging
    for item in items:
        print(f"Item: {item}")  # AI debugging
        result = transform(item)
        print(f"Result: {result}")  # AI debugging
    return results
```

This linter catches these patterns before they reach production.

## How It Works

### Python Analysis

The linter uses Python's `ast` module to find `print()` function calls:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Parse Python file into Abstract Syntax Tree (AST)        │
├─────────────────────────────────────────────────────────────┤
│ 2. Walk AST looking for Call nodes                          │
├─────────────────────────────────────────────────────────────┤
│ 3. Check if call is to print() function                     │
├─────────────────────────────────────────────────────────────┤
│ 4. Check if inside __main__ block (if allow_in_scripts)     │
├─────────────────────────────────────────────────────────────┤
│ 5. Check ignore directives (line, file, pattern)            │
├─────────────────────────────────────────────────────────────┤
│ 6. Report violations with line numbers and suggestions      │
└─────────────────────────────────────────────────────────────┘
```

### TypeScript/JavaScript Analysis

The linter uses tree-sitter for TypeScript/JavaScript analysis:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Parse file using tree-sitter TypeScript grammar          │
├─────────────────────────────────────────────────────────────┤
│ 2. Find call_expression nodes                               │
├─────────────────────────────────────────────────────────────┤
│ 3. Check if calling console.* method                        │
├─────────────────────────────────────────────────────────────┤
│ 4. Verify method is in configured console_methods set       │
├─────────────────────────────────────────────────────────────┤
│ 5. Skip test files (.test., .spec., test_, etc.)            │
├─────────────────────────────────────────────────────────────┤
│ 6. Check ignore directives                                  │
├─────────────────────────────────────────────────────────────┤
│ 7. Report violations with line numbers and suggestions      │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Quick Start: Generate Configuration

```bash
# Interactive mode
thailint init-config

# Non-interactive mode
thailint init-config --non-interactive
```

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
print-statements:
  enabled: true

  # Allow print() in if __name__ == "__main__": blocks (Python only)
  # Default: true
  allow_in_scripts: true

  # Console methods to detect in TypeScript/JavaScript
  # Default: [log, warn, error, debug, info]
  console_methods:
    - log
    - warn
    - error
    - debug
    - info

  # File patterns to ignore (glob syntax)
  ignore:
    - "scripts/**"           # CLI scripts may use print()
    - "**/debug.py"          # Debug utilities
    - "**/cli.py"            # CLI entry points
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable print statements linter |
| `allow_in_scripts` | boolean | `true` | Allow print() in `__main__` blocks (Python) |
| `console_methods` | array | `[log, warn, error, debug, info]` | Console methods to detect (TypeScript/JS) |
| `ignore` | array | `[]` | Glob patterns for files to skip |

### Language-Specific Configuration

```yaml
print-statements:
  enabled: true

  # Global settings
  allow_in_scripts: true

  # Python-specific settings
  python:
    allow_in_scripts: false  # Override: stricter for Python

  # TypeScript-specific settings
  typescript:
    console_methods:
      - log
      - warn
      - error
      # Exclude debug and info for TypeScript
```

### JSON Configuration

```json
{
  "print-statements": {
    "enabled": true,
    "allow_in_scripts": true,
    "console_methods": ["log", "warn", "error", "debug", "info"],
    "ignore": [
      "scripts/**",
      "**/debug.py"
    ]
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete guide.

**Quick examples:**

```python
# File-level ignore (entire file exempt)
# thailint: ignore-file[print-statements]

# Line-level ignore
print("Debug info")  # thailint: ignore[print-statements]

# Generic ignore (works for all rules)
print("Debug info")  # noqa
```

```typescript
// Line-level ignore
console.log("Debug info"); // thailint: ignore[print-statements]

// Generic ignore
console.log("Debug info"); // noqa
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory (recursive by default)
thailint print-statements .

# Check specific directory
thailint print-statements src/

# Check specific file
thailint print-statements src/app.py

# Check multiple paths
thailint print-statements src/ lib/ utils/
```

#### With Configuration

```bash
# Use config file
thailint print-statements --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint print-statements src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint print-statements src/

# JSON output for CI/CD
thailint print-statements --format json src/

# SARIF output for GitHub Code Scanning
thailint print-statements --format sarif src/ > results.sarif
```

#### CLI Options

```bash
Options:
  -c, --config PATH               Path to config file
  -f, --format [text|json|sarif]  Output format
  --recursive / --no-recursive    Scan directories recursively
  --help                          Show this message and exit
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with print-statements rule
violations = linter.lint('src/', rules=['print-statements'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest print-statements /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest print-statements \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Python print() Statement

**Code with violation:**
```python
def process_order(order):
    print(f"Processing order: {order.id}")
    validate(order)
    print("Validation complete")
    return save(order)
```

**Violation messages:**
```
src/orders.py:2 - print() statement should be replaced with proper logging
  Suggestion: Use logging.info(), logging.debug(), or similar instead of print()
src/orders.py:4 - print() statement should be replaced with proper logging
  Suggestion: Use logging.info(), logging.debug(), or similar instead of print()
```

**Refactored code:**
```python
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(f"Processing order: {order.id}")
    validate(order)
    logger.debug("Validation complete")
    return save(order)
```

### Example 2: TypeScript console.log()

**Code with violation:**
```typescript
async function fetchUser(id: string): Promise<User> {
    console.log(`Fetching user: ${id}`);
    const response = await api.get(`/users/${id}`);
    console.debug("Response received");
    if (!response.ok) {
        console.error(`Failed to fetch user: ${response.status}`);
    }
    return response.data;
}
```

**Violation messages:**
```
src/users.ts:2 - console.log() should be replaced with proper logging
  Suggestion: Use a logging library instead of console.log()
src/users.ts:4 - console.debug() should be replaced with proper logging
  Suggestion: Use a logging library instead of console.debug()
src/users.ts:6 - console.error() should be replaced with proper logging
  Suggestion: Use a logging library instead of console.error()
```

**Refactored code:**
```typescript
import { logger } from './logging';

async function fetchUser(id: string): Promise<User> {
    logger.info(`Fetching user: ${id}`);
    const response = await api.get(`/users/${id}`);
    logger.debug("Response received");
    if (!response.ok) {
        logger.error(`Failed to fetch user: ${response.status}`);
    }
    return response.data;
}
```

### Example 3: Allowed in __main__ Block

**Code (no violation with default config):**
```python
def main():
    """Main entry point."""
    process_all_items()

if __name__ == "__main__":
    print("Starting application...")  # Allowed by default
    main()
    print("Complete!")  # Allowed by default
```

With `allow_in_scripts: true` (default), print statements in `if __name__ == "__main__":` blocks are allowed. Set to `false` to flag these as violations.

## Refactoring Patterns

### Pattern 1: Python - Add Logging Module

**Before:**
```python
def calculate(x, y):
    print(f"Inputs: x={x}, y={y}")
    result = x + y
    print(f"Result: {result}")
    return result
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

def calculate(x, y):
    logger.debug(f"Inputs: x={x}, y={y}")
    result = x + y
    logger.info(f"Result: {result}")
    return result
```

### Pattern 2: TypeScript - Use Winston or Pino

**Before:**
```typescript
export class UserService {
    async createUser(data: UserData): Promise<User> {
        console.log("Creating user...");
        const user = await this.repository.create(data);
        console.log(`User created: ${user.id}`);
        return user;
    }
}
```

**After (using Winston):**
```typescript
import winston from 'winston';

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [new winston.transports.Console()],
});

export class UserService {
    async createUser(data: UserData): Promise<User> {
        logger.info("Creating user...");
        const user = await this.repository.create(data);
        logger.info(`User created: ${user.id}`, { userId: user.id });
        return user;
    }
}
```

### Pattern 3: Replace Debug Print with Conditional Logging

**Before:**
```python
DEBUG = True

def process(data):
    if DEBUG:
        print(f"Processing: {data}")
    return transform(data)
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

def process(data):
    logger.debug(f"Processing: {data}")
    return transform(data)
```

### Pattern 4: CLI Scripts - Keep print() in __main__

**Acceptable pattern:**
```python
import logging

logger = logging.getLogger(__name__)

def run_analysis(path: str) -> dict:
    """Run analysis on path. Uses logging for library code."""
    logger.info(f"Analyzing: {path}")
    results = analyze(path)
    logger.debug(f"Found {len(results)} items")
    return results

if __name__ == "__main__":
    # print() is acceptable in CLI entry points
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <path>")
        sys.exit(1)

    results = run_analysis(sys.argv[1])
    print(f"Analysis complete: {len(results)} items found")
```

## Language Support

### Python Support

**Fully Supported**

**Detection:** `print()` function calls using AST analysis

**Parser:** Python `ast` module for reliable detection

**Features:**
- Detects all `print()` calls
- `allow_in_scripts` option for `__main__` blocks
- Proper handling of print as function (Python 3)

**Supported constructs:**
```python
print("message")
print(f"formatted {var}")
print("msg", end="")
print(*args, **kwargs)
```

### TypeScript Support

**Fully Supported**

**Detection:** `console.*` method calls using tree-sitter

**Parser:** tree-sitter with TypeScript grammar

**Configurable methods:**
- `console.log()` (default)
- `console.warn()` (default)
- `console.error()` (default)
- `console.debug()` (default)
- `console.info()` (default)

**Supported extensions:** `.ts`, `.tsx`

### JavaScript Support

**Fully Supported**

**Detection:** Same as TypeScript (uses TypeScript parser)

**Supported extensions:** `.js`, `.jsx`

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  print-statement-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for print statements
        run: |
          thailint print-statements src/

      - name: Check print statements (SARIF for Code Scanning)
        run: |
          thailint print-statements --format sarif src/ > results.sarif

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: print-statement-check
        name: Check for print statements
        entry: thailint print-statements
        language: python
        types: [python, javascript, typescript]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-print:
	@echo "=== Checking for print statements ==="
	@poetry run thailint print-statements src/ || exit 1

lint-all: lint-print
	@echo "All checks passed"
```

## Performance

The print statements linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single Python file | ~5-15ms | <50ms |
| Single TypeScript file | ~10-20ms | <50ms |
| 100 files | ~200-500ms | <1s |
| 1000 files | ~1-3s | <5s |

**Optimizations:**
- Language detection via file extension (O(1))
- AST parsing only for supported languages
- Early exit on ignore pattern matches
- Test files automatically skipped for TypeScript/JavaScript

## Troubleshooting

### Common Issues

**Issue: False positive in CLI script**

```bash
# Problem
scripts/deploy.py:15 - print() statement should be replaced with proper logging
```

**Solution:** Add to ignore patterns:
```yaml
print-statements:
  ignore:
    - "scripts/**"
```

Or allow in scripts:
```yaml
print-statements:
  allow_in_scripts: true
```

**Issue: Test file flagged (TypeScript)**

```bash
# Problem
src/user.test.ts:42 - console.log() should be replaced with proper logging
```

**Solution:** Test files are automatically skipped. If still flagged, ensure filename contains `.test.` or `.spec.`:
- `user.test.ts` ✓
- `user.spec.ts` ✓
- `test_user.ts` ✓
- `userTests.ts` ✗ (not recognized as test file)

**Issue: Need to keep specific console.error()**

```typescript
// Use inline ignore
console.error("Critical error"); // thailint: ignore[print-statements]
```

**Issue: Want to allow console.warn but flag console.log**

```yaml
print-statements:
  console_methods:
    - log
    - error
    - debug
    - info
    # Removed: warn (now allowed)
```

## Best Practices

### 1. Set Up Logging Early

Configure logging at project start, not when print statements accumulate:

```python
# logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Use Appropriate Log Levels

```python
logger.debug("Detailed debugging info")    # Development only
logger.info("General information")          # Normal operation
logger.warning("Something unexpected")      # Potential issues
logger.error("Something failed")            # Errors
logger.critical("System failure")           # Critical failures
```

### 3. Include Context in Logs

```python
# Bad - no context
logger.info("User created")

# Good - includes context
logger.info(f"User created", extra={'user_id': user.id, 'email': user.email})
```

### 4. Keep print() for CLI Output

It's appropriate to use `print()` for:
- CLI tool output to users
- `if __name__ == "__main__":` blocks
- Scripts meant for human consumption

### 5. Use Structured Logging for Production

```python
import structlog

logger = structlog.get_logger()

logger.info("user_created", user_id=user.id, email=user.email)
```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation

## Version History

- **v0.6.0**: Print statements linter release
  - Python print() detection with AST analysis
  - TypeScript/JavaScript console.* detection with tree-sitter
  - Configurable `allow_in_scripts` for `__main__` blocks
  - Configurable `console_methods` set
  - Automatic test file exclusion
  - SARIF output for CI/CD integration
