# DRY Linter (Don't Repeat Yourself)

**Purpose**: Complete guide to using the DRY linter for detecting and eliminating duplicate code

**Scope**: Configuration, usage, storage modes, refactoring patterns, and best practices for duplicate code detection

**Overview**: Comprehensive documentation for the DRY linter that detects duplicate code across projects using token-based hashing with SQLite storage. Covers how the linter works, configuration options, CLI and library usage, storage modes, performance characteristics, language support, and integration with CI/CD pipelines. Helps teams maintain DRY principles by identifying and eliminating code duplication at scale.

**Dependencies**: Python ast module, tree-sitter-typescript, sqlite3 (Python stdlib), tempfile (Python stdlib)

**Exports**: Usage documentation, configuration examples, storage mode guide, refactoring patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, api-reference.md for programmatic usage

**Implementation**: Token-based hash detection with SQLite storage (in-memory or tempfile), extensible false-positive filtering

---

## Try It Now

```bash
pip install thai-lint
thailint dry src/
```

**Example output:**
```
src/auth.py:3 - Duplicate code detected (4 lines, 2 occurrences)
  Locations:
    - src/auth.py:3-6
    - src/admin.py:3-6
  Consider extracting to shared function
```

**Fix it:** Extract the duplicate code to a shared function and import it where needed.

---

## Overview

The DRY linter detects duplicate code blocks across your entire project using token-based hashing. It identifies identical or near-identical code that violates the Don't Repeat Yourself (DRY) principle, helping maintain code quality and reducing maintenance burden.

### Why DRY Matters

Duplicate code leads to:
- **Higher maintenance cost**: Changes must be replicated across multiple locations
- **Increased bug risk**: Fixes applied in one location may be missed in duplicates
- **Code bloat**: Unnecessary increase in codebase size
- **Inconsistency**: Duplicates may diverge over time, causing behavior inconsistencies
- **Reduced readability**: More code to understand and navigate

### Benefits

- **Automated detection**: Find duplicates across thousands of files in seconds
- **Cross-file detection**: Identifies duplicates spanning multiple files and directories
- **Fast duplicate detection**: SQLite indexes enable efficient hash lookups
- **Configurable thresholds**: Adjust sensitivity per language and project needs
- **False positive filtering**: Automatically excludes common non-duplication patterns
- **Language-specific tuning**: Different thresholds for Python, TypeScript, JavaScript
- **CI/CD integration**: JSON output and proper exit codes
- **Memory efficient**: In-memory mode (default) or tempfile for large projects

## How It Works

### Token-Based Hash Detection

The DRY linter uses token-based hashing (Rabin-Karp algorithm) to identify duplicates:

1. **Tokenize code**: Parse source into tokens, stripping comments and normalizing whitespace
2. **Create hash windows**: Generate rolling hash windows of N lines (configurable)
3. **Hash each window**: Compute hash for each N-line block
4. **Store hashes**: Save hash → locations mapping in SQLite database
5. **Find duplicates**: Query for hashes appearing 2+ times across the project

### Architecture

**Two-Phase Processing**:
1. **Collection Phase** (`check()` per file):
   - Analyze file and compute hashes for all code blocks
   - Store hash → location mappings in SQLite database
   - Return [] (no violations yet)

2. **Finalization Phase** (`finalize()` after all files):
   - Query database for all hashes with COUNT >= min_occurrences
   - For each duplicate hash, create violations for all locations
   - Return all violations

### SQLite Storage

**Storage Modes**:
- **In-memory** (default): Fast, RAM-only SQLite database (`:memory:`)
- **Tempfile**: Disk-backed temporary file for large projects, auto-deleted on completion

**Performance**:
- Fast hash indexing: O(log n) lookups via SQLite B-tree indexes
- Efficient duplicate detection: Single query returns all matching hashes
- Scales to large projects: Handles thousands of files efficiently

**Schema**:
```sql
CREATE TABLE files (
    file_path TEXT PRIMARY KEY,
    mtime REAL NOT NULL,
    hash_count INTEGER,
    last_scanned TIMESTAMP
);

CREATE TABLE code_blocks (
    file_path TEXT,
    hash_value INTEGER,
    start_line INTEGER,
    end_line INTEGER,
    snippet TEXT,
    FOREIGN KEY (file_path) REFERENCES files(file_path)
);

CREATE INDEX idx_hash ON code_blocks(hash_value);
```

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
dry:
  enabled: true
  min_duplicate_lines: 4         # Minimum lines to consider duplicate
  min_duplicate_tokens: 30       # Minimum tokens to consider duplicate
  min_occurrences: 2             # Report if appears 2+ times
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable/disable DRY linter |
| `min_duplicate_lines` | integer | `3` | Minimum consecutive lines for duplicate detection |
| `min_duplicate_tokens` | integer | `30` | Minimum token count for duplicate detection |
| `min_occurrences` | integer | `2` | Minimum occurrences to report (2 = report pairs) |
| `storage_mode` | string | `"memory"` | SQLite storage mode: "memory" (fast) or "tempfile" (large projects) |
| `ignore` | array | `["tests/", "__init__.py"]` | Files/directories to skip |
| `filters` | object | See below | False positive filters |

### Language-Specific Thresholds

Override `min_occurrences` per language:

```yaml
dry:
  enabled: true
  min_occurrences: 2  # Global default

  # Language-specific overrides
  python:
    min_occurrences: 3  # Python: require 3+ occurrences

  typescript:
    min_occurrences: 3  # TypeScript: require 3+ occurrences

  javascript:
    min_occurrences: 3  # JavaScript: require 3+ occurrences
```

**Rationale**: Higher thresholds for verbose languages reduce false positives from boilerplate.

### Storage Configuration

```yaml
dry:
  storage_mode: "memory"  # Options: "memory" (default) or "tempfile"
```

**Storage Modes**:
- **memory** (default): In-memory SQLite database (`:memory:`), fast, no disk I/O
- **tempfile**: Temporary file SQLite database, for memory-constrained environments, auto-deleted after run

**When to use tempfile**:
- Large projects (10,000+ files) where memory is constrained
- Environments with limited RAM
- Projects with very large files (lots of code blocks to hash)

### False Positive Filters

Built-in filters automatically exclude common non-duplication patterns:

```yaml
dry:
  filters:
    keyword_argument_filter: true   # Filter function call kwargs (e.g., param=value, ...)
    import_group_filter: true       # Filter import statement groups
    logger_call_filter: true        # Filter single-line logger calls
    exception_reraise_filter: true  # Filter idiomatic exception re-raising
```

**Available Filters:**

| Filter | Description | Example Filtered |
|--------|-------------|------------------|
| `keyword_argument_filter` | Function calls with keyword args | `name=name, value=value,` |
| `import_group_filter` | Import statement blocks | `import os\nimport sys` |
| `logger_call_filter` | Single-line logger calls | `logger.info("Starting...")` |
| `exception_reraise_filter` | Exception re-raising patterns | `except X:\n  raise Y from e` |

**Why Filters?**
- Function calls with keyword arguments often look similar but aren't true duplication
- Import groups naturally repeat across files and aren't violations
- Logger calls are contextually different despite structural similarity
- Exception re-raising is idiomatic Python and shouldn't be flagged
- Extensible: New filters can be added as needed

### Ignore Patterns

```yaml
dry:
  ignore:
    - "tests/"           # Test code often has acceptable duplication
    - "__init__.py"      # Import-only files exempt
    - "*.min.js"         # Minified code
    - "vendor/"          # Third-party code
```

### JSON Configuration

```json
{
  "dry": {
    "enabled": true,
    "min_duplicate_lines": 4,
    "min_duplicate_tokens": 30,
    "min_occurrences": 2,
    "python": {
      "min_occurrences": 3
    },
    "storage_mode": "memory",
    "ignore": ["tests/", "__init__.py"],
    "filters": {
      "keyword_argument_filter": true,
      "import_group_filter": true
    }
  }
}
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint dry .

# Check specific directory
thailint dry src/

# Check specific file
thailint dry src/main.py
```

#### With Configuration

```bash
# Use config file
thailint dry --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint dry src/
```

#### Threshold Overrides

```bash
# Override minimum duplicate lines
thailint dry --min-lines 5 src/

# More strict (fewer lines required)
thailint dry --min-lines 3 src/
```

#### Storage Mode

```bash
# Use memory mode (default - fast)
thailint dry src/

# Use tempfile mode (for large projects)
thailint dry --storage-mode tempfile src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint dry src/

# JSON output for CI/CD
thailint dry --format json src/

# JSON to file
thailint dry --format json src/ > dry-report.json
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with DRY rule
violations = linter.lint('src/', rules=['dry'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_number} - {v.message}")
```

#### Direct DRY Linter API

```python
from src.linters.dry import DRYRule
from src.orchestrator.core import Orchestrator

# Create orchestrator with config
orchestrator = Orchestrator(project_root=".")

# Run DRY linter
violations = orchestrator.lint_directory('src/')
dry_violations = [v for v in violations if v.rule_id.startswith('dry.')]

# Process results
for violation in dry_violations:
    print(f"{violation.file_path}: {violation.message}")
```

#### Programmatic Configuration

```python
from src.orchestrator.core import Orchestrator

# Configure via dictionary
orchestrator = Orchestrator(
    project_root=".",
    config={
        "dry": {
            "enabled": True,
            "min_duplicate_lines": 5,
            "min_occurrences": 3,
            "storage_mode": "memory"
        }
    }
)

violations = orchestrator.lint_directory('src/')
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint dry /workspace/src/

# With custom config
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint dry --config /config/.thailint.yaml /workspace/src/

# With tempfile mode for large projects
docker run --rm -v $(pwd):/workspace \
  washad/thailint dry --storage-mode tempfile /workspace/src/

# JSON output
docker run --rm -v $(pwd):/workspace \
  washad/thailint dry --format json /workspace/src/
```

## Violation Examples

### Example 1: Duplicate Functions (Python)

**Code with duplication:**
```python
# src/auth.py
def validate_user(user_data):
    if not user_data:
        return False
    if not user_data.get('email'):
        return False
    if not user_data.get('password'):
        return False
    return True

# src/admin.py
def validate_admin(admin_data):
    if not admin_data:
        return False
    if not admin_data.get('email'):
        return False
    if not admin_data.get('password'):
        return False
    return True
```

**Violation message:**
```
src/auth.py:3 - Duplicate code detected (4 lines, 2 occurrences)
  Locations:
    - src/auth.py:3-6
    - src/admin.py:3-6
  Consider extracting to shared function
```

**Refactored (DRY):**
```python
# src/validators.py
def validate_credentials(data):
    if not data:
        return False
    if not data.get('email'):
        return False
    if not data.get('password'):
        return False
    return True

# src/auth.py
from src.validators import validate_credentials

def validate_user(user_data):
    return validate_credentials(user_data)

# src/admin.py
from src.validators import validate_credentials

def validate_admin(admin_data):
    return validate_credentials(admin_data)
```

### Example 2: Duplicate TypeScript Logic

**Code with duplication:**
```typescript
// src/user-service.ts
export function formatUserError(error: Error): string {
  if (!error) {
    return 'Unknown error';
  }
  if (error.message) {
    return `Error: ${error.message}`;
  }
  return 'Unknown error';
}

// src/admin-service.ts
export function formatAdminError(error: Error): string {
  if (!error) {
    return 'Unknown error';
  }
  if (error.message) {
    return `Error: ${error.message}`;
  }
  return 'Unknown error';
}
```

**Refactored (DRY):**
```typescript
// src/utils/error-formatter.ts
export function formatError(error: Error): string {
  if (!error) {
    return 'Unknown error';
  }
  if (error.message) {
    return `Error: ${error.message}`;
  }
  return 'Unknown error';
}

// src/user-service.ts
import { formatError } from './utils/error-formatter';

export function formatUserError(error: Error): string {
  return formatError(error);
}

// src/admin-service.ts
import { formatError } from './utils/error-formatter';

export function formatAdminError(error: Error): string {
  return formatError(error);
}
```

## Duplicate Constants Detection

The DRY linter includes an optional sub-feature to detect when the same constant name appears in multiple files. This catches a common AI-generated code pattern where agents duplicate constants like `API_TIMEOUT = 30` across files instead of consolidating them.

### Enabling Duplicate Constants Detection

```yaml
dry:
  enabled: true
  detect_duplicate_constants: true  # Enabled by default
  min_constant_occurrences: 2       # Report when constant appears in 2+ files
```

### What Counts as a Constant

**Python Constants:**
- Module-level assignments with `ALL_CAPS` names
- Excludes private constants (leading underscore like `_PRIVATE`)
- Excludes class-level and function-level constants

```python
# Detected as constant
API_TIMEOUT = 30
MAX_RETRIES = 5
DEFAULT_HOST = "localhost"

# NOT detected (lowercase, private, or nested)
api_timeout = 30
_PRIVATE_CONST = 100
class Config:
    MAX_VALUE = 50  # Class-level, not detected
```

**TypeScript Constants:**
- Top-level `const` declarations with `UPPER_SNAKE_CASE` names
- Excludes `let`/`var` declarations
- Excludes camelCase or other naming conventions

```typescript
// Detected as constant
const API_TIMEOUT = 30;
export const MAX_RETRIES = 5;

// NOT detected (not const, or not UPPER_SNAKE_CASE)
let apiTimeout = 30;
const apiTimeout = 30;  // camelCase
var MAX_VALUE = 100;    // var, not const
```

### Fuzzy Matching

The linter uses two fuzzy matching strategies to catch related constants that should be consolidated:

#### Word-Set Matching

Constants with the same words in different order are matched:

```python
# These are matched (same words: api, timeout)
# file1.py
API_TIMEOUT = 30

# file2.py
TIMEOUT_API = 60
```

**Violation message:**
```
Similar constants found: 'API_TIMEOUT' ≈ 'TIMEOUT_API' in 2 files.
Also found in: file2.py:1 (TIMEOUT_API = 60).
These appear to represent the same concept - consider standardizing the name.
```

#### Edit Distance Matching

Constants with typos (Levenshtein distance ≤ 2) are matched:

```python
# These are matched (edit distance = 1)
# file1.py
MAX_RETRIES = 5

# file2.py
MAX_RETRYS = 5  # Typo
```

**Violation message:**
```
Similar constants found: 'MAX_RETRIES' ≈ 'MAX_RETRYS' in 2 files.
Also found in: file2.py:1 (MAX_RETRYS = 5).
These appear to represent the same concept - consider standardizing the name.
```

#### Single-Word Constants

Single-word constants (e.g., `MAX`, `TIMEOUT`) only use exact matching to avoid false positives:

```python
# These are NOT matched (single words, different names)
# file1.py
MAX = 100

# file2.py
MIN = 0
```

### Exact Duplicate Constants

When the same constant name appears in multiple files:

```python
# file1.py
API_TIMEOUT = 30

# file2.py
API_TIMEOUT = 60

# file3.py
API_TIMEOUT = 45
```

**Violation message:**
```
Duplicate constant 'API_TIMEOUT' defined in 3 files.
Also found in: file2.py:1 (API_TIMEOUT = 60), file3.py:1 (API_TIMEOUT = 45).
Consider consolidating to a shared constants module.
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `detect_duplicate_constants` | boolean | `true` | Enable duplicate constant detection |
| `min_constant_occurrences` | integer | `2` | Minimum files to report (2 = pairs) |
| `python_min_constant_occurrences` | integer | `null` | Python-specific override |
| `typescript_min_constant_occurrences` | integer | `null` | TypeScript-specific override |

### Refactoring Pattern: Shared Constants Module

**Before (duplicated):**
```python
# src/api/client.py
API_TIMEOUT = 30

# src/api/server.py
API_TIMEOUT = 30

# src/api/middleware.py
API_TIMEOUT = 30
```

**After (consolidated):**
```python
# src/constants.py
API_TIMEOUT = 30

# src/api/client.py
from src.constants import API_TIMEOUT

# src/api/server.py
from src.constants import API_TIMEOUT

# src/api/middleware.py
from src.constants import API_TIMEOUT
```

### TypeScript Example

**Before (duplicated):**
```typescript
// src/api/client.ts
export const API_TIMEOUT = 30;

// src/api/server.ts
export const API_TIMEOUT = 30;
```

**After (consolidated):**
```typescript
// src/constants.ts
export const API_TIMEOUT = 30;

// src/api/client.ts
import { API_TIMEOUT } from '../constants';

// src/api/server.ts
import { API_TIMEOUT } from '../constants';
```

## Performance

The DRY linter analyzes files fresh every run (no persistence between runs):

| Project Size | Performance | Storage Mode |
|--------------|-------------|--------------|
| 100 files | 0.3-0.5s | Memory |
| 1000 files | 1-3s | Memory |
| 10000 files | 10-30s | Memory or Tempfile |

**Optimizations:**
- SQLite indexed hash lookups (O(log n))
- Token-based hashing (faster than AST comparison)
- In-memory storage (default, fastest)
- Tempfile mode for memory-constrained environments

**Memory Usage:**
- **Memory mode**: 50-200MB for 1000 files, 200-500MB for 10000 files
- **Tempfile mode**: Lower RAM usage, slightly slower due to disk I/O

## Refactoring Patterns

Common patterns to eliminate duplicates:

### Pattern 1: Extract Function

**When to use**: Logic repeated across multiple functions

**Before**:
```python
def save_user(user):
    if not user.email:
        raise ValueError("Email required")
    if not user.name:
        raise ValueError("Name required")
    db.save(user)

def save_admin(admin):
    if not admin.email:
        raise ValueError("Email required")
    if not admin.name:
        raise ValueError("Name required")
    db.save(admin)
```

**After**:
```python
def validate_required_fields(obj):
    if not obj.email:
        raise ValueError("Email required")
    if not obj.name:
        raise ValueError("Name required")

def save_user(user):
    validate_required_fields(user)
    db.save(user)

def save_admin(admin):
    validate_required_fields(admin)
    db.save(admin)
```

### Pattern 2: Extract Base Class

**When to use**: Similar class implementations

**Before**:
```python
class UserRepository:
    def find_by_id(self, id): ...
    def find_all(self): ...
    def save(self, entity): ...
    def delete(self, id): ...

class ProductRepository:
    def find_by_id(self, id): ...
    def find_all(self): ...
    def save(self, entity): ...
    def delete(self, id): ...
```

**After**:
```python
class BaseRepository:
    def find_by_id(self, id): ...
    def find_all(self): ...
    def save(self, entity): ...
    def delete(self, id): ...

class UserRepository(BaseRepository):
    pass  # Inherits all methods

class ProductRepository(BaseRepository):
    pass  # Inherits all methods
```

### Pattern 3: Extract Utility Module

**When to use**: Helper functions repeated across files

**Before**:
```python
# file1.py
def is_valid_email(email):
    return '@' in email and '.' in email

# file2.py
def is_valid_email(email):
    return '@' in email and '.' in email
```

**After**:
```python
# utils/validation.py
def is_valid_email(email):
    return '@' in email and '.' in email

# file1.py
from utils.validation import is_valid_email

# file2.py
from utils.validation import is_valid_email
```

### Pattern 4: Template Method

**When to use**: Similar algorithms with variations

**Before**:
```python
def process_csv_file(path):
    data = read_csv(path)
    validate_data(data)
    transform_data(data)
    save_to_db(data)

def process_json_file(path):
    data = read_json(path)
    validate_data(data)
    transform_data(data)
    save_to_db(data)
```

**After**:
```python
def process_file(path, reader_func):
    data = reader_func(path)
    validate_data(data)
    transform_data(data)
    save_to_db(data)

# Usage
process_file('data.csv', read_csv)
process_file('data.json', read_json)
```

## Language Support

### Python Support

**Fully Supported**

**Detection Features:**
- AST-based tokenization
- Comment stripping
- Whitespace normalization
- Decorator filtering (not included in hash)
- Docstring filtering (not included in hash)

**Configurable:**
```yaml
dry:
  python:
    min_occurrences: 3  # Require 3+ occurrences
```

### TypeScript Support

**Fully Supported**

**Detection Features:**
- Tree-sitter-based parsing
- JSDoc comment filtering
- Interface/type declaration filtering
- Whitespace normalization

**Configurable:**
```yaml
dry:
  typescript:
    min_occurrences: 3  # TypeScript can be verbose
```

### JavaScript Support

**Supported** (via TypeScript parser)

JavaScript files analyzed using TypeScript parser with appropriate settings.

**Configurable:**
```yaml
dry:
  javascript:
    min_occurrences: 3
```

## Ignoring Violations

### Inline Ignore Directives

The DRY linter supports inline ignore directives for duplicate **code blocks** (not constants):

#### Block Ignore

Use `# dry: ignore-block` to ignore the next 10 lines of code:

```python
# dry: ignore-block
def legacy_function1():
    # Duplicates allowed for next 10 lines
    pass

def legacy_function2():
    pass
```

#### Next-Line Ignore

Use `# dry: ignore-next` to ignore just the immediately following line:

```python
# dry: ignore-next
def single_legacy_function():  # Only this line is ignored
    pass
```

**Important limitations:**
- Inline ignores apply to **duplicate code blocks only**, not to similar constants detection
- `ignore-block` ignores the next 10 lines after the directive (not arbitrary start/end markers)
- For constants, use configuration-based ignores or add the constant name to an exclude list

### TypeScript Inline Ignores

```typescript
// dry: ignore-block
function legacyHelper1() {
  // Duplicates allowed
}

// dry: ignore-next
function legacyHelper2() {}
```

### Configuration-Based Ignore

```yaml
dry:
  ignore:
    - "tests/"               # Entire directory
    - "src/legacy/"          # Legacy code
    - "src/migrations/*.py"  # Migration scripts
    - "**/generated/**"      # Generated code
```

## CI/CD Integration

### GitHub Actions

```yaml
name: DRY Check

on: [push, pull_request]

jobs:
  dry-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for duplicate code
        run: thailint dry --format json src/ > dry-report.json

      - name: Upload report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: dry-report
          path: dry-report.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dry-check
        name: Check for duplicate code
        entry: thailint dry --min-lines 4
        language: python
        pass_filenames: false
        always_run: true
```

### Makefile Integration

```makefile
lint-dry:
	@echo "=== Checking for duplicate code ==="
	@thailint dry src/ || exit 1

lint-all: lint-dry
	@echo "All quality checks passed"
```

## Best Practices

### 1. Start with Permissive Thresholds

```yaml
# Initial configuration
dry:
  enabled: true
  min_duplicate_lines: 5  # Start higher
  min_occurrences: 3      # Require more occurrences
```

Gradually reduce thresholds as duplicates are fixed.

### 2. Use Language-Specific Thresholds

```yaml
dry:
  min_occurrences: 2  # Default

  python:
    min_occurrences: 3  # Python: more strict

  typescript:
    min_occurrences: 3  # TypeScript: account for verbosity
```

### 3. Ignore Acceptable Duplication

```yaml
dry:
  ignore:
    - "tests/"          # Tests often have acceptable duplication
    - "migrations/"     # Migration scripts are sequential
    - "*/generated/*"   # Generated code
```

### 4. Use Tempfile Mode for Very Large Projects

```yaml
dry:
  storage_mode: "tempfile"  # For projects > 10000 files or memory-constrained environments
```

### 5. Review Violations Incrementally

```bash
# Fix highest-impact duplicates first
thailint dry src/ | grep "5+ occurrences"

# Then gradually address smaller duplicates
thailint dry src/
```

### 6. Integrate Early in Development

Add to pre-commit hooks or CI/CD to catch new duplicates before merge.

### 7. Document Intentional Duplication

```python
def setup_test_database():  # thailint: ignore dry - Test setup boilerplate
    # Acceptable duplication in test fixtures
    pass
```

### 8. Handle Framework Adapter Patterns

Some code duplication is structural and intentional, particularly in "framework adapter" patterns like CLI command modules. When each command implements the same interface contract:

```python
# CLI commands that implement the same interface contract
@cli.command("nesting")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path())
@format_option
@click.pass_context
def nesting_command(ctx, paths, config_file, format):
    """Execute nesting linter."""
    _execute_lint(paths, config_file, format, "nesting")

@cli.command("srp")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path())
@format_option
@click.pass_context
def srp_command(ctx, paths, config_file, format):
    """Execute SRP linter."""
    _execute_lint(paths, config_file, format, "srp")
```

This duplication is **intentional** because:
- Each command adapts a common framework to a specific linter
- The variation is minimal (command name, rule ID filter)
- Abstracting further would reduce code clarity

**Solution**: Add CLI modules to the ignore list rather than expecting automatic filtering:

```yaml
dry:
  ignore:
    - "src/cli.py"          # CLI command handlers
    - "src/commands/"       # Or wherever CLI modules live
    - "**/cli/**"           # Pattern for CLI directories
```

Framework adapter patterns include:
- CLI command handlers (Click, Typer, argparse)
- API endpoint handlers (FastAPI, Flask, Express)
- Event handlers with common signatures
- Plugin implementations with shared interfaces

## API Reference

### Configuration Schema

```python
@dataclass
class DRYConfig:
    enabled: bool = False
    min_duplicate_lines: int = 3
    min_duplicate_tokens: int = 30
    min_occurrences: int = 2

    # Language-specific overrides for duplicate code
    python_min_occurrences: int | None = None
    typescript_min_occurrences: int | None = None
    javascript_min_occurrences: int | None = None

    # Duplicate constants detection
    detect_duplicate_constants: bool = True
    min_constant_occurrences: int = 2
    python_min_constant_occurrences: int | None = None
    typescript_min_constant_occurrences: int | None = None

    # Storage settings
    storage_mode: str = "memory"  # Options: "memory" or "tempfile"

    # Ignore patterns
    ignore_patterns: list[str] = field(default_factory=lambda: ["tests/", "__init__.py"])

    # Block filters
    filters: dict[str, bool] = field(default_factory=lambda: {
        "keyword_argument_filter": True,
        "import_group_filter": True,
        "logger_call_filter": True,
        "exception_reraise_filter": True,
    })
```

### Rule Class

```python
class DRYRule(BaseLintRule):
    rule_id: str = "dry.duplicate-code"
    rule_name: str = "Duplicate Code"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Analyze file and store blocks (collection phase)."""

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed."""
```

## Troubleshooting

### Issue: High False Positives

**Solution**: Adjust thresholds or enable filters

```yaml
dry:
  min_duplicate_lines: 5  # Increase from 3
  min_occurrences: 3      # Increase from 2
  filters:
    keyword_argument_filter: true  # Enable filter
```

### Issue: Missing Duplicates

**Symptoms**: Known duplicates not reported

**Solutions**:
1. Lower thresholds:
   ```yaml
   dry:
     min_duplicate_lines: 3  # Lower from 5
     min_occurrences: 2      # Lower from 3
   ```

2. Check ignore patterns:
   ```yaml
   dry:
     ignore:
       - "tests/"  # Remove if you want to check tests
   ```

### Issue: Slow Performance or High Memory Usage

**Solutions**:
1. Use tempfile mode for large projects:
   ```yaml
   dry:
     storage_mode: "tempfile"  # Reduces memory usage
   ```

2. Exclude large directories:
   ```yaml
   dry:
     ignore:
       - "vendor/"
       - "node_modules/"
       - "build/"
       - "dist/"
   ```

3. Increase thresholds to reduce processing:
   ```yaml
   dry:
     min_duplicate_lines: 5  # Higher threshold = fewer blocks to hash
   ```

## Resources

- **CLI Reference**: `docs/cli-reference.md` - Complete CLI documentation
- **Configuration Guide**: `docs/configuration.md` - Config file reference
- **API Reference**: `docs/api-reference.md` - Library API documentation
- **Getting Started**: `docs/getting-started.md` - Quick start guide

## Contributing

Report issues or suggest improvements:
- GitHub Issues: https://github.com/be-wise-be-kind/thai-lint/issues
- Feature requests: Tag with `enhancement`
- Bug reports: Tag with `bug`
