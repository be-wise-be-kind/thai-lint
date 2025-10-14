# Magic Numbers Linter

**Purpose**: Complete guide to using the magic numbers linter for detecting and eliminating unnamed numeric literals

**Scope**: Configuration, usage, refactoring patterns, and best practices for magic number detection

**Overview**: Comprehensive documentation for the magic numbers linter that detects unnamed numeric literals (magic numbers) in Python and TypeScript code. Covers how the linter works using AST analysis, configuration options, CLI and library usage, acceptable contexts, common refactoring patterns, and integration with CI/CD pipelines. Helps teams improve code maintainability by encouraging named constants instead of magic numbers.

**Dependencies**: ast module (Python parser), tree-sitter-typescript (TypeScript parser)

**Exports**: Usage documentation, configuration examples, refactoring patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

**Implementation**: AST-based detection with context-aware filtering and configurable acceptable numbers

---

## Overview

The magic numbers linter detects unnamed numeric literals (magic numbers) that should be extracted to named constants. It analyzes Python and TypeScript code using Abstract Syntax Tree (AST) parsing to identify numeric literals that lack meaningful context.

### What are Magic Numbers?

**Magic numbers** are unnamed numeric literals that appear directly in code without explanation:

```python
# Bad - Magic numbers
def process_data():
    timeout = 3600
    max_retries = 5
    buffer_size = 1024

# Good - Named constants
TIMEOUT_SECONDS = 3600
MAX_RETRY_ATTEMPTS = 5
BUFFER_SIZE_BYTES = 1024

def process_data():
    timeout = TIMEOUT_SECONDS
    max_retries = MAX_RETRY_ATTEMPTS
    buffer_size = BUFFER_SIZE_BYTES
```

### Why Eliminate Magic Numbers?

Magic numbers are problematic because:
- **Unclear meaning**: `3600` doesn't explain it's seconds in an hour
- **Hard to maintain**: Changing `3600` to `7200` requires finding all occurrences
- **Error-prone**: Easy to use wrong value (`3600` vs `36000`)
- **Duplication**: Same value repeated makes updates difficult
- **Lack of context**: Future developers won't understand significance

### Benefits

- **Improved readability**: Named constants are self-documenting
- **Easier maintenance**: Change constant definition, not all occurrences
- **Reduced errors**: Use wrong constant name, not wrong number
- **Better search**: Find all uses of `TIMEOUT_SECONDS`
- **Team consistency**: Enforces shared code quality standards

## How It Works

### AST-Based Detection

The linter uses Abstract Syntax Tree (AST) parsing to analyze code structure:

1. **Parse source code** into AST using language-specific parsers:
   - Python: Built-in `ast` module
   - TypeScript: `tree-sitter-typescript` library

2. **Find numeric literals** in the AST:
   - Integer literals: `42`, `1000`, `-5`
   - Float literals: `3.14`, `2.5`, `1.414`

3. **Filter acceptable contexts**:
   - Constants: `MAX_SIZE = 100` (UPPERCASE names)
   - Small integers in `range()`: `range(5)`, `enumerate(items, 1)`
   - Test files: `test_*.py`, `*.test.ts`
   - Allowed numbers: `-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000` (configurable)

4. **Report violations** for unexplained numeric literals

### Acceptable Contexts

The linter **does not** flag numbers in these contexts:

| Context | Example | Why Acceptable |
|---------|---------|----------------|
| Constant definitions | `MAX_SIZE = 100` | UPPERCASE name provides context |
| Small `range()` | `range(5)` | Small loop bounds are clear |
| Small `enumerate()` | `enumerate(items, 1)` | Start index is obvious |
| Test files | `test_*.py`, `*.test.ts` | Test data can be literal |
| Allowed numbers | `-1, 0, 1, 2, 3, 4, 5, 10` | Common values are self-explanatory |
| String repetition | `"-" * 40` | Repetition count is obvious |

**Note**: Only **numeric literals** (integers and floats) are detected. String literals are not magic numbers.

## Configuration

### Quick Start: Generate Configuration File

The easiest way to get started is to use the `init-config` command to generate a `.thailint.yaml` file:

```bash
# Interactive mode (for humans - asks questions)
thailint init-config

# Non-interactive mode (for AI agents)
thailint init-config --non-interactive

# With preset
thailint init-config --preset lenient --non-interactive
```

**Available presets:**
- `strict`: Only `-1, 0, 1` allowed (strictest)
- `standard` (**default**): `-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000` (balanced)
- `lenient`: Adds time conversions `60, 3600` (most permissive)

The generated file includes rich comments explaining all options and common customizations.

### Basic Configuration

Alternatively, manually create `.thailint.yaml`:

```yaml
magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000]  # Numbers that won't be flagged
  max_small_integer: 10  # Max value for range() to be acceptable
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable magic numbers linter |
| `allowed_numbers` | array | `[-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000]` | Numbers that are acceptable without constants |
| `max_small_integer` | integer | `10` | Maximum value allowed in `range()` or `enumerate()` |

### Recommended Values

**Allowed Numbers:**
- **Strict**: `[-1, 0, 1]` - Only very common values
- **Standard**: `[-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000]` - Recommended (default)
- **Lenient**: `[-1, 0, 1, 2, 3, 4, 5, 10, 60, 100, 1000, 3600]` - Include time conversions

**Rationale for Default Numbers:**
- `-1, 0, 1, 2`: Ubiquitous values (return codes, boolean-like, counters)
- `3, 4, 5`: Self-documenting in array indexing, small loops, geometry (triangles, squares, pentagons)
- `10, 100, 1000`: Common powers of 10, often self-documenting in context
- `60, 3600` (lenient only): Universal time constants (seconds/minute, seconds/hour)

**Max Small Integer:**
- **Strict**: `3` - Very small loop bounds only
- **Standard**: `10` - Recommended (default)
- **Lenient**: `20` - Allow larger explicit loop bounds

### JSON Configuration

```json
{
  "magic-numbers": {
    "enabled": true,
    "allowed_numbers": [-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000],
    "max_small_integer": 10
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete ignore guide.

**Quick examples:**

```python
# Line-level ignore
timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard timeout

# Method-level ignore
def get_http_codes():  # thailint: ignore[magic-numbers] - HTTP codes are self-documenting
    return {200: "OK", 404: "Not Found"}

# File-level ignore
# thailint: ignore-file[magic-numbers]
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint magic-numbers .

# Check specific directory
thailint magic-numbers src/

# Check specific file
thailint magic-numbers src/config.py
```

#### With Configuration

```bash
# Use config file
thailint magic-numbers --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint magic-numbers src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint magic-numbers src/

# JSON output for CI/CD
thailint magic-numbers --format json src/

# JSON with exit code check
thailint magic-numbers --format json src/ > report.json
echo "Exit code: $?"
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with magic-numbers rule
violations = linter.lint('src/', rules=['magic-numbers'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_number} - {v.message}")
```

#### Direct Magic Numbers Linter API

```python
from src.linters.magic_numbers import lint

# Lint specific path
violations = lint('src/config.py')

# With custom configuration
violations = lint(
    'src/',
    config={
        'allowed_numbers': [0, 1, 2, 60, 3600],
        'max_small_integer': 10
    }
)

# Process results
for violation in violations:
    print(f"Line {violation.line_number}: {violation.message}")
```

#### Advanced: Direct Rule Usage

```python
from src.linters.magic_numbers import MagicNumberRule
from src.orchestrator.core import Orchestrator

# Create rule instance
rule = MagicNumberRule()

# Use orchestrator for file processing
orchestrator = Orchestrator(
    config={'magic-numbers': {'allowed_numbers': [0, 1, 2]}}
)
violations = orchestrator.lint_file('src/example.py', rules=[rule])
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest magic-numbers /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest magic-numbers \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Python Magic Numbers

**Code with violations:**
```python
def calculate_timeout():
    return 3600  # Magic number - what is 3600?

def process_items(items):
    for i in range(100):  # Magic number - why 100?
        items[i] *= 1.5  # Magic number - what is 1.5?
```

**Violation messages:**
```
src/example.py:2 - Magic number 3600 should be a named constant
Consider: TIMEOUT_SECONDS = 3600

src/example.py:5 - Magic number 100 should be a named constant
Consider: MAX_ITEMS = 100

src/example.py:6 - Magic number 1.5 should be a named constant
Consider: MULTIPLIER = 1.5
```

**Refactored code:**
```python
TIMEOUT_SECONDS = 3600
MAX_ITEMS = 100
PRICE_MULTIPLIER = 1.5

def calculate_timeout():
    return TIMEOUT_SECONDS

def process_items(items):
    for i in range(MAX_ITEMS):
        items[i] *= PRICE_MULTIPLIER
```

### Example 2: TypeScript Magic Numbers

**Code with violations:**
```typescript
function validatePort(port: number): boolean {
  if (port < 1024 || port > 65535) {  // Magic numbers
    return false;
  }
  return true;
}

const timeout = 5000;  // Magic number
```

**Violation messages:**
```
src/example.ts:2 - Magic number 1024 should be a named constant
src/example.ts:2 - Magic number 65535 should be a named constant
src/example.ts:7 - Magic number 5000 should be a named constant
```

**Refactored code:**
```typescript
const MIN_USER_PORT = 1024;
const MAX_PORT_NUMBER = 65535;
const DEFAULT_TIMEOUT_MS = 5000;

function validatePort(port: number): boolean {
  if (port < MIN_USER_PORT || port > MAX_PORT_NUMBER) {
    return false;
  }
  return true;
}

const timeout = DEFAULT_TIMEOUT_MS;
```

### Example 3: Acceptable Contexts (No Violations)

```python
# Constants (UPPERCASE names) - OK
MAX_RETRIES = 5
TIMEOUT_SECONDS = 30

# Small integers in range() - OK
for i in range(5):
    process(i)

# Small integers in enumerate() - OK
for idx, item in enumerate(items, 1):
    print(f"{idx}: {item}")

# Allowed numbers - OK
if status == -1:  # -1 is in allowed_numbers
    return None

# String repetition - OK
print("-" * 40)

# Test files (test_*.py) - OK
def test_calculation():
    assert calculate(5, 10) == 15  # Numbers OK in tests
```

## Refactoring Patterns

### Pattern 1: Extract to Module-Level Constants

**Before:**
```python
def connect_to_database():
    timeout = 30
    max_retries = 3
    backoff_multiplier = 2.0
```

**After:**
```python
# Module-level constants
DEFAULT_DB_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
EXPONENTIAL_BACKOFF_MULTIPLIER = 2.0

def connect_to_database():
    timeout = DEFAULT_DB_TIMEOUT_SECONDS
    max_retries = DEFAULT_MAX_RETRIES
    backoff_multiplier = EXPONENTIAL_BACKOFF_MULTIPLIER
```

**Benefits**: Constants can be reused across functions, easier to update

### Pattern 2: Extract to Configuration Class

**Before:**
```python
def fetch_data():
    timeout = 10
    max_size = 1000
    buffer_size = 4096

def save_data():
    timeout = 10  # Duplicated magic number
    chunk_size = 4096  # Duplicated magic number
```

**After:**
```python
class Config:
    """Application configuration constants."""
    NETWORK_TIMEOUT_SECONDS = 10
    MAX_DATA_SIZE = 1000
    BUFFER_SIZE_BYTES = 4096

def fetch_data():
    timeout = Config.NETWORK_TIMEOUT_SECONDS
    max_size = Config.MAX_DATA_SIZE
    buffer_size = Config.BUFFER_SIZE_BYTES

def save_data():
    timeout = Config.NETWORK_TIMEOUT_SECONDS
    chunk_size = Config.BUFFER_SIZE_BYTES
```

**Benefits**: Centralized configuration, no duplication, clear organization

### Pattern 3: Extract with Units in Name

**Before:**
```python
def schedule_task():
    delay = 3600  # Is this seconds? Minutes? Milliseconds?
    max_age = 86400  # What unit?
```

**After:**
```python
TASK_DELAY_SECONDS = 3600  # 1 hour
CACHE_MAX_AGE_SECONDS = 86400  # 24 hours

def schedule_task():
    delay = TASK_DELAY_SECONDS
    max_age = CACHE_MAX_AGE_SECONDS
```

**Benefits**: Units are clear, conversion is documented

### Pattern 4: Extract with Calculation Comment

**Before:**
```python
def get_timeout():
    return 604800  # What is this?
```

**After:**
```python
WEEK_IN_SECONDS = 7 * 24 * 60 * 60  # 604800

def get_timeout():
    return WEEK_IN_SECONDS
```

**Benefits**: Shows how value was calculated, easier to verify

### Pattern 5: Extract HTTP/Network Constants

**Before:**
```python
def check_status(code):
    if code == 200:
        return "success"
    if code == 404:
        return "not_found"
    if code == 500:
        return "error"
```

**After:**
```python
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

def check_status(code):
    if code == HTTP_OK:
        return "success"
    if code == HTTP_NOT_FOUND:
        return "not_found"
    if code == HTTP_INTERNAL_ERROR:
        return "error"
```

**Alternative** - Use standard library:
```python
from http import HTTPStatus

def check_status(code):
    if code == HTTPStatus.OK:
        return "success"
    if code == HTTPStatus.NOT_FOUND:
        return "not_found"
    if code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return "error"
```

**Benefits**: Self-documenting, uses industry standard codes

## Language Support

### Python Support

**Fully Supported**

**Numeric literals detected:**
- Integer literals: `42`, `1000`, `-5`
- Float literals: `3.14`, `2.5`, `1.414`
- Scientific notation: `1e6`, `2.5e-3`

**Acceptable contexts:**
- Constant definitions: `MAX_SIZE = 100` (UPPERCASE)
- Small integers in `range()`: `range(10)`
- Small integers in `enumerate()`: `enumerate(items, 1)`
- Test files: `test_*.py`, `*_test.py`
- Allowed numbers: `-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000` (default)
- String repetition: `"-" * 40`

### TypeScript Support

**Fully Supported**

**Numeric literals detected:**
- Integer literals: `42`, `1000`, `-5`
- Float literals: `3.14`, `2.5`, `1.414`
- Scientific notation: `1e6`, `2.5e-3`

**Acceptable contexts:**
- Constant definitions: `const MAX_SIZE = 100` (UPPERCASE)
- Enum values: `enum Status { ACTIVE = 1 }`
- Test files: `*.test.ts`, `*.spec.ts`, `*.test.tsx`
- Allowed numbers: `-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000` (default)

### JavaScript Support

**Supported** (via TypeScript parser)

JavaScript files are analyzed using the TypeScript parser, which handles JavaScript syntax.

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  magic-numbers-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for magic numbers
        run: |
          thailint magic-numbers src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: magic-numbers-check
        name: Check for magic numbers
        entry: thailint magic-numbers
        language: python
        types: [python, javascript, typescript]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-magic-numbers:
	@echo "=== Checking for magic numbers ==="
	@poetry run thailint magic-numbers src/ || exit 1

lint-all: lint-magic-numbers
	@echo "All checks passed"
```

## Performance

The magic numbers linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse | ~10-30ms | <100ms |
| Single file analysis | ~5-15ms | <50ms |
| 100 files | ~500ms | <2s |
| 1000 files | ~2-3s | <10s |

**Optimizations:**
- AST parsing is cached during file processing
- Context checks use efficient parent node inspection
- Violations are reported immediately (fail-fast)

## Troubleshooting

### Common Issues

**Issue: Numbers in constants are flagged**

```python
# Problem - lowercase constant name
max_size = 100  # ← Flagged as magic number

# Solution - use UPPERCASE for constants
MAX_SIZE = 100  # ← Not flagged
```

**Issue: Small numbers in loops are flagged**

```python
# Problem - number too large
for i in range(50):  # ← Flagged if max_small_integer=10

# Solution 1: Extract to constant
MAX_ITERATIONS = 50
for i in range(MAX_ITERATIONS):

# Solution 2: Increase max_small_integer in config
# .thailint.yaml
magic-numbers:
  max_small_integer: 50
```

**Issue: HTTP status codes flagged**

```python
# Problem - bare numbers
if status == 200:  # ← Flagged

# Solution 1: Extract constants
HTTP_OK = 200
if status == HTTP_OK:

# Solution 2: Use standard library
from http import HTTPStatus
if status == HTTPStatus.OK:

# Solution 3: Add to allowed_numbers
# .thailint.yaml
magic-numbers:
  allowed_numbers: [-1, 0, 1, 2, 10, 100, 200, 201, 404, 500]
```

**Issue: Test file still flagged**

```bash
# Problem - file doesn't match test pattern
tests/helpers.py  # ← Not recognized as test file

# Solution 1: Rename to match pattern
tests/test_helpers.py  # ← Recognized as test file

# Solution 2: Add file-level ignore
# tests/helpers.py
# thailint: ignore-file[magic-numbers]
```

## Best Practices

### 1. Use Descriptive Constant Names

```python
# Bad - unclear names
N = 100
X = 3.14
T = 5000

# Good - descriptive names
MAX_USERS_PER_PAGE = 100
CIRCLE_PI_APPROXIMATION = 3.14
DEFAULT_TIMEOUT_MS = 5000
```

### 2. Include Units in Names

```python
# Bad - ambiguous units
TIMEOUT = 30
SIZE = 1024

# Good - explicit units
TIMEOUT_SECONDS = 30
BUFFER_SIZE_BYTES = 1024
MAX_FILE_SIZE_MB = 10
```

### 3. Group Related Constants

```python
# Good - logical grouping
class TimeConstants:
    SECOND_IN_MS = 1000
    MINUTE_IN_SECONDS = 60
    HOUR_IN_SECONDS = 3600
    DAY_IN_SECONDS = 86400

class HTTPStatusCodes:
    OK = 200
    CREATED = 201
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
```

### 4. Add Comments for Calculations

```python
# Good - show calculation
WEEK_IN_SECONDS = 7 * 24 * 60 * 60  # 7 days * 24 hours * 60 min * 60 sec
MAX_BUFFER_SIZE = 1024 * 1024  # 1 MB in bytes
```

### 5. Use Standard Library When Available

```python
# Good - use Python standard library
from http import HTTPStatus
import math

status = HTTPStatus.OK  # Instead of 200
pi = math.pi  # Instead of 3.14159
```

### 6. Consider Configuration Files

For values that change between environments:

```python
# config.py
import os

# Good - environment-based configuration
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '100'))
TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '30'))
```

## When to Ignore Violations

### Legitimate Uses of Magic Numbers

1. **Array indices** (if context is clear):
   ```python
   rgb = [255, 128, 0]
   red = rgb[0]  # thailint: ignore[magic-numbers] - RGB red channel
   ```

2. **Industry standards** (well-known values):
   ```python
   http_port = 80  # thailint: ignore[magic-numbers] - Standard HTTP port
   https_port = 443  # thailint: ignore[magic-numbers] - Standard HTTPS port
   ```

3. **Mathematical constants** (when not using library):
   ```python
   pi = 3.14159  # thailint: ignore[magic-numbers] - Pi constant
   e = 2.71828  # thailint: ignore[magic-numbers] - Euler's number
   ```

4. **Test data** (when values are arbitrary):
   ```python
   def test_calculation():
       result = add(5, 10)  # thailint: ignore[magic-numbers] - Arbitrary test values
       assert result == 15
   ```

## Examples Repository

See **[examples/magic_numbers_usage.py](../examples/magic_numbers_usage.py)** for complete working examples.

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation

## Version History

- **v0.3.0**: Magic numbers linter release
  - Python and TypeScript support
  - AST-based detection with tree-sitter
  - Context-aware filtering (constants, range, test files)
  - Configurable allowed_numbers and max_small_integer
  - 71/71 tests passing (47 Python + 24 TypeScript)
  - Self-dogfooded on thai-lint codebase (0 violations)
