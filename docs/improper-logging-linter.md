# Improper Logging Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the improper logging linter for detecting print/console statements and conditional verbose patterns that indicate improper logging practices

    **Scope**: Configuration, usage, language support, and best practices for improper logging detection

    **Overview**: Comprehensive documentation for the improper logging linter that detects two types of violations: (1) print() calls in Python and console.* calls in TypeScript/JavaScript that should use proper logging, and (2) conditional verbose patterns like `if verbose: logger.debug()` that should use log level configuration instead. Covers how the linter works using AST analysis, configuration options, CLI and library usage, ignore patterns, and integration with CI/CD pipelines.

    **Dependencies**: Python AST (Python), tree-sitter (TypeScript/JavaScript)

    **Exports**: Usage documentation, configuration examples, violation messages, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns, print-statements-linter.md (deprecated alias)

    **Implementation**: AST-based analysis for Python print() calls and conditional verbose patterns, tree-sitter for TypeScript/JavaScript console.* methods

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thai-lint
thailint improper-logging src/
```

**Example output:**
```
src/handlers.py:42 - print() call found - use logging instead
  Suggestion: Replace print("Debug: user={user}") with logger.debug("user=%s", user)

src/utils.py:15 - Conditional verbose check around logger.debug() should be removed
  Suggestion: Remove the 'if verbose:' condition and configure logging level instead
```

**Fix it:** Replace print statements with proper logging calls, and remove conditional verbose guards.

---

## Overview

The improper logging linter detects two types of anti-patterns:

1. **Print Statements** (`improper-logging.print-statement`): `print()` calls in Python and `console.*` calls in TypeScript/JavaScript that should be replaced with proper logging.

2. **Conditional Verbose** (`improper-logging.conditional-verbose`): Patterns like `if verbose: logger.debug()` where logging calls are guarded by verbose flags instead of using proper log level configuration.

!!! note "Command Alias"
    The `print-statements` command is a deprecated alias for `improper-logging`. Both commands work identically, but new code should use `improper-logging`.

### Why Detect Improper Logging?

**Print statements** are problematic in production code for several reasons:

- **No log levels**: `print()` doesn't distinguish between debug, info, warning, and error messages
- **No timestamps**: Logs lack timing information for debugging issues
- **No context**: Missing file, line, and function context that logging provides
- **Performance**: Unbuffered I/O can slow down applications
- **Security**: Sensitive data may be accidentally exposed

**Conditional verbose patterns** are problematic because:

- **Cluttered code**: Verbose checks add noise and reduce readability
- **Inconsistent behavior**: Log levels should be controlled centrally, not per-call
- **Performance**: Runtime conditionals are slower than letting the logging framework handle levels
- **Maintainability**: Changing verbosity requires code changes instead of configuration

### What It Detects

#### Print Statement Detection

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

// Not detected (allowed)
logger.info("Debug message");
winston.warn("Warning!");
```

#### Conditional Verbose Detection (Python only)

```python
# Detected (violations)
if verbose:
    logger.debug("Processing started")

if self.verbose:
    logger.info("User created")

if ctx.obj.get("verbose"):
    logger.debug("Config loaded")

# Not detected (allowed - proper logging)
logger.debug("Processing started")  # Let log level handle verbosity
logger.info("User created")
```

## Rule IDs

| Rule ID | Description |
|---------|-------------|
| `improper-logging.print-statement` | Print/console statements that should use proper logging |
| `improper-logging.conditional-verbose` | Conditional verbose guards around logging calls |

!!! info "Backward Compatibility"
    The old rule ID `print-statements.detected` is aliased to `improper-logging.print-statement` for backward compatibility. Ignore directives using the old ID continue to work.

## How It Works

### Print Statement Analysis

**Python:** Uses Python's `ast` module to find `print()` function calls.

**TypeScript/JavaScript:** Uses tree-sitter to find `console.*` method calls.

### Conditional Verbose Analysis

The linter uses Python AST to find `if` statements with verbose-like conditions that contain logger method calls:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Parse Python file into Abstract Syntax Tree (AST)        │
├─────────────────────────────────────────────────────────────┤
│ 2. Find If nodes with verbose-like conditions:              │
│    - if verbose:                                            │
│    - if self.verbose:                                       │
│    - if config.verbose:                                     │
│    - if ctx.obj.get("verbose"):                             │
├─────────────────────────────────────────────────────────────┤
│ 3. Check if body contains logger method calls:              │
│    - logger.debug(), logger.info()                          │
│    - logging.debug(), logging.info()                        │
│    - etc.                                                   │
├─────────────────────────────────────────────────────────────┤
│ 4. Report violations with suggestions                       │
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
improper-logging:
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

!!! note "Legacy Configuration"
    The configuration key `print-statements` is also supported for backward compatibility.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable improper logging linter |
| `allow_in_scripts` | boolean | `true` | Allow print() in `__main__` blocks (Python) |
| `console_methods` | array | `[log, warn, error, debug, info]` | Console methods to detect (TypeScript/JS) |
| `ignore` | array | `[]` | Glob patterns for files to skip |

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete guide.

**Quick examples:**

```python
# File-level ignore (entire file exempt)
# thailint: ignore-file[improper-logging]

# Line-level ignore - works with both old and new rule IDs
print("Debug info")  # thailint: ignore[improper-logging]
print("Debug info")  # thailint: ignore[print-statements]  # Also works

# Ignore conditional verbose
if verbose:
    logger.debug("info")  # thailint: ignore[improper-logging.conditional-verbose]

# Generic ignore (works for all rules)
print("Debug info")  # noqa
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory (recursive by default)
thailint improper-logging .

# Check specific directory
thailint improper-logging src/

# Check specific file
thailint improper-logging src/app.py

# Check multiple paths
thailint improper-logging src/ lib/ utils/
```

#### Using the Deprecated Alias

```bash
# Both commands work identically
thailint print-statements src/
thailint improper-logging src/
```

#### With Configuration

```bash
# Use config file
thailint improper-logging --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint improper-logging src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint improper-logging src/

# JSON output for CI/CD
thailint improper-logging --format json src/

# SARIF output for GitHub Code Scanning
thailint improper-logging --format sarif src/ > results.sarif
```

#### CLI Options

```bash
Options:
  -c, --config PATH               Path to config file
  -f, --format [text|json|sarif]  Output format
  --recursive / --no-recursive    Scan directories recursively
  --help                          Show this message and exit
```

## Violation Examples

### Example 1: Python print() Statement

**Code with violation:**
```python
def process_order(order):
    print(f"Processing order: {order.id}")
    validate(order)
    return save(order)
```

**Violation message:**
```
src/orders.py:2 - print() statement should be replaced with proper logging
  Suggestion: Use logging.info(), logging.debug(), or similar instead of print()
```

**Refactored code:**
```python
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(f"Processing order: {order.id}")
    validate(order)
    return save(order)
```

### Example 2: Conditional Verbose Pattern

**Code with violation:**
```python
def process_data(data, verbose=False):
    if verbose:
        logger.debug(f"Processing {len(data)} items")
    result = transform(data)
    if verbose:
        logger.debug(f"Transformation complete")
    return result
```

**Violation messages:**
```
src/processor.py:3 - Conditional verbose check around logger.debug() should be removed
  Suggestion: Remove the 'if verbose:' condition and configure logging level instead.
  Use logger.setLevel(logging.DEBUG) to control verbosity.

src/processor.py:6 - Conditional verbose check around logger.debug() should be removed
  Suggestion: Remove the 'if verbose:' condition and configure logging level instead.
  Use logger.setLevel(logging.DEBUG) to control verbosity.
```

**Refactored code:**
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing {len(data)} items")
    result = transform(data)
    logger.debug(f"Transformation complete")
    return result

# Configure verbosity at application level
if verbose:
    logging.getLogger().setLevel(logging.DEBUG)
```

### Example 3: TypeScript console.log()

**Code with violation:**
```typescript
async function fetchUser(id: string): Promise<User> {
    console.log(`Fetching user: ${id}`);
    const response = await api.get(`/users/${id}`);
    return response.data;
}
```

**Violation message:**
```
src/users.ts:2 - console.log() should be replaced with proper logging
  Suggestion: Use a logging library instead of console.log()
```

**Refactored code:**
```typescript
import { logger } from './logging';

async function fetchUser(id: string): Promise<User> {
    logger.info(`Fetching user: ${id}`);
    const response = await api.get(`/users/${id}`);
    return response.data;
}
```

## Refactoring Patterns

### Pattern 1: Remove Verbose Guards

**Before:**
```python
def analyze(data, verbose=False):
    if verbose:
        logger.debug(f"Analyzing {len(data)} items")
    result = do_analysis(data)
    if verbose:
        logger.debug(f"Analysis complete: {result}")
    return result
```

**After:**
```python
def analyze(data):
    logger.debug(f"Analyzing {len(data)} items")
    result = do_analysis(data)
    logger.debug(f"Analysis complete: {result}")
    return result
```

### Pattern 2: Centralize Verbosity Control

**Before (scattered verbose checks):**
```python
class Processor:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def step1(self, data):
        if self.verbose:
            logger.debug("Step 1 starting")
        # ...

    def step2(self, data):
        if self.verbose:
            logger.debug("Step 2 starting")
        # ...
```

**After (centralized log level):**
```python
import logging

class Processor:
    def __init__(self, verbose=False):
        if verbose:
            logging.getLogger(__name__).setLevel(logging.DEBUG)

    def step1(self, data):
        logger.debug("Step 1 starting")
        # ...

    def step2(self, data):
        logger.debug("Step 2 starting")
        # ...
```

### Pattern 3: Click CLI Verbose Flag

**Before:**
```python
@click.command()
@click.option('--verbose', is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj = {'verbose': verbose}

@click.command()
@click.pass_context
def process(ctx):
    if ctx.obj.get('verbose'):
        logger.debug("Processing...")
    do_work()
```

**After:**
```python
@click.command()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

@click.command()
def process():
    logger.debug("Processing...")  # Controlled by log level
    do_work()
```

## Language Support

### Python Support

**Fully Supported**

Both rules apply to Python:
- Print statement detection (`improper-logging.print-statement`)
- Conditional verbose detection (`improper-logging.conditional-verbose`)

### TypeScript/JavaScript Support

**Partially Supported**

Only print statement detection applies:
- Console statement detection (`improper-logging.print-statement`)

The conditional verbose rule does not apply to TypeScript/JavaScript as the pattern is Python-specific.

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  improper-logging-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for improper logging
        run: |
          thailint improper-logging src/

      - name: Check improper logging (SARIF for Code Scanning)
        run: |
          thailint improper-logging --format sarif src/ > results.sarif

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
      - id: improper-logging-check
        name: Check for improper logging
        entry: thailint improper-logging
        language: python
        types: [python, javascript, typescript]
        pass_filenames: true
```

## Best Practices

### 1. Configure Log Levels at Application Startup

```python
import logging

def configure_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### 2. Use Module-Level Loggers

```python
import logging

logger = logging.getLogger(__name__)

def process(data):
    logger.debug("Processing data")  # Module's log level controls output
```

### 3. Keep print() for CLI User Output

It's appropriate to use `print()` for:
- CLI tool output to users
- `if __name__ == "__main__":` blocks
- Scripts meant for human consumption

### 4. Use Structured Logging for Production

```python
import structlog

logger = structlog.get_logger()

logger.info("user_created", user_id=user.id, email=user.email)
```

## Migration from print-statements

If you were using the `print-statements` command:

1. **CLI**: Replace `thailint print-statements` with `thailint improper-logging` (optional - the old command still works)

2. **Configuration**: You can keep using `print-statements:` in config, or update to `improper-logging:`

3. **Ignore directives**: Both `# thailint: ignore[print-statements]` and `# thailint: ignore[improper-logging]` work

4. **Rule IDs**: The old rule ID `print-statements.detected` is automatically aliased to `improper-logging.print-statement`

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[Print Statements Linter](print-statements-linter.md)** - Deprecated alias documentation

## Version History

- **v0.16.0**: Renamed to improper-logging, added conditional verbose detection
  - New command `improper-logging` (alias `print-statements` preserved)
  - New rule `improper-logging.conditional-verbose` for Python
  - Renamed `print-statements.detected` to `improper-logging.print-statement`
  - Full backward compatibility with old rule IDs and configuration

- **v0.6.0**: Initial print statements linter release
  - Python print() detection with AST analysis
  - TypeScript/JavaScript console.* detection with tree-sitter
  - Configurable `allow_in_scripts` for `__main__` blocks
  - SARIF output for CI/CD integration
