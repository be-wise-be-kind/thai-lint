# Stringly-Typed Linter

**Purpose**: Complete guide to using the stringly-typed linter for detecting string-based type patterns that should use enums

**Scope**: Configuration, usage, refactoring patterns, and best practices for stringly-typed code detection

**Overview**: Comprehensive documentation for the stringly-typed linter that detects code patterns where plain strings are used instead of proper enums or typed alternatives. Covers how the linter works using AST and tree-sitter analysis, configuration options, CLI and library usage, false positive filtering, ignore directives, and common refactoring patterns. Helps teams improve type safety by identifying repeated string validation patterns that indicate missing enum types.

**Dependencies**: ast module (Python parser), tree-sitter-typescript (TypeScript parser), SQLite (cross-file storage)

**Exports**: Usage documentation, configuration examples, refactoring patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

**Implementation**: AST-based detection with cross-file analysis using SQLite for pattern aggregation

---

## Try It Now

```bash
pip install thai-lint
thailint stringly-typed src/
```

**Example output:**
```
src/models.py:28 - String 'active' appears in membership test pattern
  Found in: if status in ['active', 'pending', 'cancelled']
  Suggestion: Consider creating a Status enum
```

**Fix it:** Replace repeated string literals with enums or typed constants.

---

## Overview

The stringly-typed linter detects code patterns where plain strings are used in ways that suggest a missing enum or type definition. It analyzes Python and TypeScript code to find repeated string validation patterns across multiple files.

### What is "Stringly-Typed" Code?

**Stringly-typed** code uses plain strings where enums or typed constants would be more appropriate:

```python
# Bad - Stringly-typed code
def process_order(status: str) -> None:
    if status in ("pending", "shipped", "delivered"):
        handle_status(status)

def update_order(status: str) -> None:
    if status == "pending":
        schedule_shipment()
    elif status == "shipped":
        send_notification()

# Good - Properly typed with enum
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

def process_order(status: OrderStatus) -> None:
    handle_status(status)

def update_order(status: OrderStatus) -> None:
    if status == OrderStatus.PENDING:
        schedule_shipment()
    elif status == OrderStatus.SHIPPED:
        send_notification()
```

### Why Eliminate Stringly-Typed Code?

Stringly-typed code is problematic because:

- **No type safety**: Typos like `"pening"` instead of `"pending"` won't be caught
- **No IDE support**: No autocomplete or refactoring support for string values
- **Hard to maintain**: Adding a new status requires finding all validation points
- **Inconsistent**: Different parts of code may use different string sets
- **No documentation**: The valid values aren't discoverable from type signatures

### Benefits of Enums

- **Type safety**: Compiler/interpreter catches invalid values
- **IDE support**: Autocomplete shows all valid options
- **Refactoring**: Rename enum value, all uses update
- **Documentation**: Valid values are explicit in the type
- **Consistency**: Single source of truth for valid values

## How It Works

### Detection Patterns

The linter detects three main patterns:

#### Pattern 1: Membership Validation

```python
# Detected patterns
if env in ("staging", "production"):
    deploy()

if status not in {"pending", "completed", "failed"}:
    raise ValueError()
```

#### Pattern 2: Equality Chains

```python
# Detected patterns
if status == "success":
    celebrate()
elif status == "failure":
    retry()
elif status == "pending":
    wait()

# Also detected: match statements (Python 3.10+)
match mode:
    case "debug":
        enable_logging()
    case "release":
        optimize()
```

#### Pattern 3: Function Call Tracking

```python
# Detected: Function called with limited string values
set_status("active")
set_status("inactive")
set_status("pending")
# If called across multiple files with only 2-6 unique values → violation
```

### Cross-File Analysis

The linter uses **SQLite storage** to track patterns across your entire codebase:

1. **check() phase**: Each file is analyzed, patterns are stored in SQLite
2. **finalize() phase**: Cross-file duplicates are detected and violations generated

This means the same string validation in `module_a.py` and `module_b.py` will be flagged as a repeated pattern suggesting an enum.

### Language Support

| Language | Membership Validation | Equality Chains | Function Calls |
|----------|----------------------|-----------------|----------------|
| Python | ✅ Full | ✅ Full | ✅ Full |
| TypeScript | ✅ Full | ✅ Full | ✅ Full |
| JavaScript | ✅ Via TypeScript | ✅ Via TypeScript | ✅ Via TypeScript |

## Configuration

### Quick Start: Generate Configuration File

```bash
# Interactive mode
thailint init-config

# Non-interactive mode
thailint init-config --non-interactive
```

### Basic Configuration

Create `.thailint.yaml`:

```yaml
stringly_typed:
  enabled: true
  min_occurrences: 2           # Min files where pattern must appear
  min_values_for_enum: 2       # Min unique values to suggest enum
  max_values_for_enum: 6       # Max values (above this, probably not enum-worthy)
  require_cross_file: true     # Only flag if pattern appears in multiple files
  ignore: []                   # File patterns to ignore
  allowed_string_sets: []      # String sets that are intentionally allowed
  exclude_variables: []        # Variable names to exclude
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable stringly-typed linter |
| `min_occurrences` | integer | `2` | Minimum files where pattern must appear |
| `min_values_for_enum` | integer | `2` | Minimum unique string values to flag |
| `max_values_for_enum` | integer | `6` | Maximum values (above this, probably not enum-worthy) |
| `require_cross_file` | boolean | `true` | Only flag patterns appearing in multiple files |
| `ignore` | array | `[]` | File patterns to ignore (glob syntax) |
| `allowed_string_sets` | array | `[]` | Intentionally allowed string sets |
| `exclude_variables` | array | `[]` | Variable names to exclude from detection |

### Recommended Values

**For strict enforcement:**
```yaml
stringly_typed:
  min_occurrences: 2
  min_values_for_enum: 2
  max_values_for_enum: 6
  require_cross_file: true
```

**For lenient enforcement:**
```yaml
stringly_typed:
  min_occurrences: 3
  min_values_for_enum: 3
  max_values_for_enum: 8
  require_cross_file: true
```

### Allowed String Sets

If you have intentional string sets that shouldn't be flagged:

```yaml
stringly_typed:
  allowed_string_sets:
    - ["debug", "info", "warning", "error"]  # Log levels
    - ["GET", "POST", "PUT", "DELETE"]       # HTTP methods
    - ["asc", "desc"]                         # Sort orders
```

### Ignoring Files

```yaml
stringly_typed:
  ignore:
    - "tests/**"              # Ignore test files
    - "**/fixtures.py"        # Ignore fixture files
    - "migrations/**"         # Ignore migrations
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint stringly-typed .

# Check specific directory
thailint stringly-typed src/

# Check specific file
thailint stringly-typed src/handlers.py
```

#### With Configuration

```bash
# Use config file
thailint stringly-typed --config .thailint.yaml src/

# Auto-discover config
thailint stringly-typed src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint stringly-typed src/

# JSON output for CI/CD
thailint stringly-typed --format json src/

# SARIF output for IDE integration
thailint stringly-typed --format sarif src/ > report.sarif
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with stringly-typed rule
violations = linter.lint('src/', rules=['stringly-typed'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

#### Direct Linter API

```python
from src.linters.stringly_typed import StringlyTypedRule
from src.core.base import BaseLintContext

# Create rule instance
rule = StringlyTypedRule()

# Analyze files (check phase)
for file_path in python_files:
    context = BaseLintContext(
        file_path=str(file_path),
        file_content=file_path.read_text(),
        metadata={}
    )
    rule.check_python(context)

# Generate violations (finalize phase)
violations = rule.finalize()
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest stringly-typed /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest stringly-typed \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Repeated Membership Validation

**Code with violations:**

File: `src/handlers/order.py`
```python
def validate_order_status(status: str) -> bool:
    if status in ("pending", "shipped", "delivered"):
        return True
    return False
```

File: `src/services/order_service.py`
```python
def process_order(status: str) -> None:
    if status in ("pending", "shipped", "delivered"):
        handle_order(status)
```

**Violation message:**
```
src/handlers/order.py:2 - Stringly-typed pattern with values ['delivered', 'pending', 'shipped'] appears in 2 files. Also found in: order_service.py:2.
Suggestion: Consider defining an enum or type union for 'status' with the 3 possible values instead of using string literals.
```

### Example 2: Function Call with Limited Values

**Code with violations:**

File: `src/api/users.py`
```python
user.set_role("admin")
user.set_role("editor")
```

File: `src/api/permissions.py`
```python
user.set_role("viewer")
user.set_role("admin")
```

**Violation message:**
```
src/api/users.py:1 - Function 'set_role' first parameter is called with only 3 unique string values ['admin', 'editor', 'viewer'] across 2 file(s). Also called in: permissions.py:1, permissions.py:2.
Suggestion: Consider defining an enum or type union with the 3 possible values for 'set_role' parameter 0.
```

### Example 3: TypeScript Switch Statement

**Code with violations:**

```typescript
// File: src/handlers/status.ts
function handleStatus(status: string): void {
    switch (status) {
        case "active":
            activate();
            break;
        case "inactive":
            deactivate();
            break;
        case "pending":
            wait();
            break;
    }
}

// File: src/utils/status.ts
function validateStatus(status: string): boolean {
    return ["active", "inactive", "pending"].includes(status);
}
```

**Violation message:**
```
src/handlers/status.ts:2 - Stringly-typed pattern with values ['active', 'inactive', 'pending'] appears in 2 files.
Suggestion: Consider defining an enum or type union with the 3 possible values instead of using string literals.
```

**Refactored TypeScript:**

```typescript
// File: src/types/status.ts
export type Status = "active" | "inactive" | "pending";

// Or with enum:
export enum Status {
    ACTIVE = "active",
    INACTIVE = "inactive",
    PENDING = "pending"
}

// File: src/handlers/status.ts
import { Status } from "../types/status";

function handleStatus(status: Status): void {
    switch (status) {
        case Status.ACTIVE:
            activate();
            break;
        case Status.INACTIVE:
            deactivate();
            break;
        case Status.PENDING:
            wait();
            break;
    }
}
```

## Refactoring Patterns

### Pattern 1: Python Enum

**Before:**
```python
def process_order(status: str) -> None:
    if status in ("pending", "shipped", "delivered"):
        handle_order(status)
```

**After:**
```python
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

def process_order(status: OrderStatus) -> None:
    handle_order(status)
```

### Pattern 2: Python StrEnum (3.11+)

**Before:**
```python
def log_level(level: str) -> None:
    if level in ("debug", "info", "warning", "error"):
        log(level)
```

**After:**
```python
from enum import StrEnum

class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

def log_level(level: LogLevel) -> None:
    log(level)
```

### Pattern 3: TypeScript Union Type

**Before:**
```typescript
function setMode(mode: string): void {
    if (!["debug", "release"].includes(mode)) {
        throw new Error("Invalid mode");
    }
}
```

**After:**
```typescript
type Mode = "debug" | "release";

function setMode(mode: Mode): void {
    // Type system ensures valid values
}
```

### Pattern 4: TypeScript Enum

**Before:**
```typescript
function handleStatus(status: string): void {
    switch (status) {
        case "active": break;
        case "inactive": break;
    }
}
```

**After:**
```typescript
enum Status {
    ACTIVE = "active",
    INACTIVE = "inactive"
}

function handleStatus(status: Status): void {
    switch (status) {
        case Status.ACTIVE: break;
        case Status.INACTIVE: break;
    }
}
```

### Pattern 5: TypeScript const Object

**Before:**
```typescript
if (env === "staging" || env === "production") {
    deploy();
}
```

**After:**
```typescript
const Environment = {
    STAGING: "staging",
    PRODUCTION: "production"
} as const;

type Environment = typeof Environment[keyof typeof Environment];

if (env === Environment.STAGING || env === Environment.PRODUCTION) {
    deploy();
}
```

## False Positive Filtering

The linter includes extensive false positive filtering to reduce noise:

### Excluded Contexts

| Context | Example | Why Excluded |
|---------|---------|--------------|
| Dict methods | `d.get("key")` | Key access, not validation |
| String operations | `s.split(",")` | Data manipulation |
| Logging calls | `logger.info("message")` | Log messages |
| Exception constructors | `ValueError("msg")` | Error messages |
| HTTP methods | `requests.get(url)` | Framework conventions |
| Framework validators | `Field(regex="...")` | Validation patterns |
| File modes | `open(f, "r")` | Standard Python I/O |

### Excluded Value Patterns

| Pattern | Examples | Why Excluded |
|---------|----------|--------------|
| Numeric strings | `"0"`, `"123"` | Often IDs or counts |
| HTTP methods | `"GET"`, `"POST"` | Standard protocol |
| File modes | `"r"`, `"w"`, `"rb"` | Standard I/O |
| strftime formats | `"%Y-%m-%d"` | Date formatting |
| Empty strings | `""` | Common default |

## Ignore Directives

### Line-Level Ignore

Suppress a single line:

```python
if status in ("pending", "shipped"):  # thailint: ignore[stringly-typed]
    process()
```

### Next-Line Ignore

Suppress the next line:

```python
# thailint: ignore-next-line[stringly-typed]
if status in ("pending", "shipped"):
    process()
```

### Block-Level Ignore

Suppress a region:

```python
# thailint: ignore-start stringly-typed
if status in ("pending", "shipped"):
    process()
if mode in ("debug", "release"):
    configure()
# thailint: ignore-end
```

### File-Level Ignore

Suppress entire file:

```python
# thailint: ignore-file[stringly-typed]
# At top of file, within first 10 lines
```

### TypeScript Syntax

```typescript
// Line-level
if (status === "active") {  // thailint: ignore[stringly-typed]
    activate();
}

// File-level (use # comment)
# thailint: ignore-file[stringly-typed]
```

### Wildcard Matching

```python
# Ignore all stringly-typed sub-rules
if status in ("a", "b"):  # thailint: ignore[stringly-typed.*]
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  stringly-typed-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for stringly-typed patterns
        run: thailint stringly-typed src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: stringly-typed-check
        name: Check for stringly-typed patterns
        entry: thailint stringly-typed
        language: python
        types: [python, javascript, typescript]
        pass_filenames: false
        args: ["src/"]
```

### Makefile Integration

```makefile
lint-stringly-typed:
	@echo "=== Checking for stringly-typed patterns ==="
	@poetry run thailint stringly-typed src/ || exit 1

lint-all: lint-stringly-typed
	@echo "All checks passed"
```

## Performance

The stringly-typed linter is designed for speed with cross-file analysis:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse | ~10-30ms | <100ms |
| Single file analysis | ~5-15ms | <50ms |
| 100 files (check phase) | ~1-2s | <5s |
| Finalize (cross-file) | ~100-500ms | <1s |
| 1000 files total | ~5-10s | <30s |

**Optimizations:**
- SQLite in-memory database for fast pattern storage
- Hash-based duplicate detection
- Efficient AST traversal

## Troubleshooting

### Common Issues

**Issue: Valid string constants flagged**

```python
# Problem - Log levels appear stringly-typed
logger.setLevel("DEBUG")

# Solution 1: Add to allowed_string_sets
stringly_typed:
  allowed_string_sets:
    - ["DEBUG", "INFO", "WARNING", "ERROR"]

# Solution 2: Use ignore directive
logger.setLevel("DEBUG")  # thailint: ignore[stringly-typed]
```

**Issue: Too many violations initially**

```yaml
# Solution: Start with lenient settings
stringly_typed:
  min_occurrences: 3      # Require 3+ files
  min_values_for_enum: 3  # Require 3+ values
  max_values_for_enum: 8  # Allow larger sets
```

**Issue: Single-file patterns flagged**

```yaml
# Solution: Enable require_cross_file
stringly_typed:
  require_cross_file: true  # Only flag cross-file patterns
```

**Issue: Test files flagged**

```yaml
# Solution: Add tests to ignore patterns
stringly_typed:
  ignore:
    - "tests/**"
    - "**/*_test.py"
    - "**/*.test.ts"
```

## Best Practices

### 1. Start with Cross-File Detection

```yaml
stringly_typed:
  require_cross_file: true
  min_occurrences: 2
```

Cross-file patterns are the strongest signal that an enum is needed.

### 2. Use Allowed String Sets for Intentional Patterns

```yaml
stringly_typed:
  allowed_string_sets:
    - ["debug", "info", "warning", "error"]  # Log levels
    - ["GET", "POST", "PUT", "DELETE", "PATCH"]  # HTTP methods
```

### 3. Define Enums Near First Use

```python
# Good - Define enum where it's first needed
# src/orders/status.py
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
```

### 4. Use StrEnum for String Compatibility (Python 3.11+)

```python
from enum import StrEnum

class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Works like a string
print(f"Status: {Status.ACTIVE}")  # "Status: active"
```

### 5. Use Type Unions for Simple Cases (TypeScript)

```typescript
// For 2-3 values, type unions are simpler than enums
type Status = "active" | "inactive" | "pending";

// For 4+ values, consider enums
enum Permission {
    READ = "read",
    WRITE = "write",
    DELETE = "delete",
    ADMIN = "admin",
    OWNER = "owner"
}
```

## When to Ignore Violations

### Legitimate Uses of String Literals

1. **API contracts** (when API requires specific strings):
   ```python
   response["status"] = "success"  # thailint: ignore[stringly-typed] - API contract
   ```

2. **Third-party library requirements**:
   ```python
   client.set_mode("batch")  # thailint: ignore[stringly-typed] - Library requirement
   ```

3. **Database values** (when stored as strings):
   ```python
   record.status = "pending"  # thailint: ignore[stringly-typed] - DB schema
   ```

4. **Configuration values** (loaded from config):
   ```python
   if config.env in ("dev", "staging", "prod"):  # thailint: ignore[stringly-typed]
       setup_environment(config.env)
   ```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation
- **[SARIF Output](sarif-output.md)** - CI/CD integration with SARIF

## Version History

- **v0.5.0**: Stringly-typed linter release
  - Python and TypeScript support
  - Three detection patterns (membership, equality chains, function calls)
  - Cross-file analysis with SQLite storage
  - False positive filtering (200+ patterns)
  - Ignore directive support
  - 207 tests passing
  - Self-dogfooded on thai-lint codebase (<5% false positive rate)
