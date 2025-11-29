# Configuration Reference

Complete reference for configuring thailint linters with presets, ignore patterns, and all options.

## Table of Contents

- [Quick Start with init-config](#quick-start-with-init-config)
- [Configuration File Basics](#configuration-file-basics)
- [Ignore Patterns (All Linters)](#ignore-patterns-all-linters)
- [Magic Numbers Configuration](#magic-numbers-configuration)
- [Nesting Depth Configuration](#nesting-depth-configuration)
- [SRP Configuration](#srp-configuration)
- [DRY Configuration](#dry-configuration)
- [File Placement Configuration](#file-placement-configuration)

## Quick Start with init-config

The fastest way to configure thailint is using the `init-config` command:

```bash
# Interactive mode (recommended for first-time setup)
thailint init-config

# Non-interactive with preset (for CI/CD or quick setup)
thailint init-config --preset lenient --non-interactive

# Overwrite existing config
thailint init-config --preset standard --force

# Custom output location
thailint init-config --output config/linting.yaml
```

### Presets Explained

#### `strict` - New Projects

**Best for:** Greenfield projects, strict code quality

```yaml
magic-numbers:
  allowed_numbers: [-1, 0, 1]
  max_small_integer: 2
```

**Characteristics:**
- Only universal values (-1, 0, 1)
- Very low max_small_integer
- Catches almost all numeric literals

#### `standard` - Balanced (Default)

**Best for:** Most projects

```yaml
magic-numbers:
  allowed_numbers: [-1, 0, 1, 2, 3, 4, 5, 10, 100, 1000]
  max_small_integer: 10
```

**Characteristics:**
- Common small numbers (0-5)
- Powers of 10
- Good balance of strictness

#### `lenient` - Existing Codebases

**Best for:** Legacy code, gradual adoption

```yaml
magic-numbers:
  allowed_numbers:
    - -1
    - 0
    - 1
    - 2
    - 3
    - 4
    - 5
    - 10
    - 60      # Time: seconds in minute
    - 100
    - 1000
    - 1024    # Binary: bytes in KB
    - 3600    # Time: seconds in hour
  max_small_integer: 10
```

**Characteristics:**
- Includes time conversions (60s, 3600s)
- Includes binary units (1024)
- Reduces false positives

## Configuration File Basics

### File Locations

thailint searches for configuration in this order:

1. **Command-line flag**: `thailint --config custom.yaml magic-numbers src/`
2. **Current directory**: `.thailint.yaml` or `.thailint.json`
3. **Project root**: Searches up directory tree
4. **Default config**: Built-in defaults if no file found

## Ignore Patterns (All Linters)

All linters support the `ignore` field to exclude files from linting. This section documents the complete glob pattern syntax and matching behavior.

### Pattern Syntax

thailint uses Python's `pathlib.Path.match()` for glob pattern matching with substring fallback:

| Pattern Type | Syntax | Example | Matches |
|--------------|--------|---------|---------|
| **Exact file** | `path/to/file.py` | `backend/app/famous_tracks.py` | Exact file path |
| **Wildcard (*)** | `*.py` | `test_*.py` | Files starting with `test_` |
| **Recursive (**)** | `**/pattern` | `**/test_*.py` | Recursively matches in any directory |
| **Directory** | `dir/**` | `tests/**` | All files in directory tree |
| **Substring** | `substring` | `famous_tracks` | Any path containing substring |

### How Pattern Matching Works

**Important:** Patterns are matched against the **full file path** relative to where you run the command.

```bash
# If you run from project root:
thailint magic-numbers backend/

# File path seen by thailint:
backend/app/famous_tracks.py

# Patterns that match:
- "backend/app/famous_tracks.py"    # Exact match
- "**/famous_tracks.py"              # Recursive match
- "backend/**"                       # Directory match
- "famous_tracks"                    # Substring match
```

### Real-World Examples

#### Example 1: Ignore Specific File

```yaml
magic-numbers:
  ignore:
    - "backend/app/famous_tracks.py"
```

**Matches:**
- `backend/app/famous_tracks.py` ✅

**Does NOT match:**
- `backend/app/other_file.py` ❌
- `frontend/famous_tracks.py` ❌

#### Example 2: Ignore All Test Files

```yaml
magic-numbers:
  ignore:
    - "**/test_*.py"    # test_foo.py in any directory
    - "**/*_test.py"    # foo_test.py in any directory
    - "**/*.test.ts"    # foo.test.ts in any directory
    - "**/*.spec.js"    # foo.spec.js in any directory
```

**Matches:**
- `tests/test_app.py` ✅
- `backend/tests/test_models.py` ✅
- `src/utils_test.py` ✅
- `components/Button.test.ts` ✅
- `services/api.spec.js` ✅

#### Example 3: Ignore Entire Directories

```yaml
dry:
  ignore:
    - "tests/**"           # All files in tests/ tree
    - "**/migrations/**"   # All migration dirs
    - "node_modules/**"    # Dependencies
```

**Matches:**
- `tests/unit/test_foo.py` ✅
- `backend/tests/test_bar.py` ✅
- `backend/db/migrations/001_init.py` ✅
- `node_modules/package/index.js` ✅

#### Example 4: Multiple Patterns (Real Project)

```yaml
magic-numbers:
  ignore:
    # Specific files with legitimate magic numbers
    - "backend/app/famous_tracks.py"
    - "backend/config/constants.py"

    # All test files
    - "**/test_*.py"
    - "**/*_test.py"
    - "**/*.test.ts"
    - "**/*.spec.js"

    # Generated/vendor code
    - "**/migrations/**"
    - "node_modules/**"
    - "**/dist/**"
    - "**/build/**"
```

### Common Patterns Reference

| Use Case | Pattern | Notes |
|----------|---------|-------|
| **Python tests** | `**/test_*.py`, `**/*_test.py` | Covers pytest conventions |
| **JS/TS tests** | `**/*.test.{ts,js}`, `**/*.spec.{ts,js}` | Covers Jest/Vitest conventions |
| **Test directories** | `tests/**`, `**/tests/**` | All files in test dirs |
| **Generated code** | `**/migrations/**`, `**/generated/**` | Database migrations, codegen |
| **Dependencies** | `node_modules/**`, `vendor/**` | Third-party code |
| **Build outputs** | `dist/**`, `build/**`, `out/**` | Compiled artifacts |
| **Config files** | `**/config/*.py`, `**/*_config.py` | Configuration files |
| **Type stubs** | `**/*.pyi`, `**/stubs/**` | Python type hints |

### Debugging Ignore Patterns

If your ignore patterns aren't working:

1. **Check the file path thailint sees:**
   ```bash
   # Run with verbose output to see file paths
   thailint magic-numbers --format json src/ | grep file_path
   ```

2. **Verify pattern matching:**
   ```python
   from pathlib import Path

   file_path = Path("backend/app/famous_tracks.py")
   pattern = "**/famous_tracks.py"

   print(file_path.match(pattern))  # Should be True
   ```

3. **Common mistakes:**
   - ❌ Pattern: `famous_tracks.py` (too specific, no directory context)
   - ✅ Pattern: `**/famous_tracks.py` (matches in any directory)

   - ❌ Pattern: `test/*.py` (only matches immediate children)
   - ✅ Pattern: `test/**/*.py` (matches all descendants)

4. **Escape special characters in filenames:**
   ```yaml
   ignore:
     - "**/file[with]brackets.py"  # Use quotes for special chars
   ```

### Per-Linter Ignore Patterns

Each linter can have its own ignore list:

```yaml
magic-numbers:
  ignore:
    - "backend/config/constants.py"  # Lots of config numbers
    - "**/test_*.py"

nesting:
  ignore:
    - "backend/legacy/**"  # Deep nesting in legacy code
    - "**/migrations/**"

dry:
  ignore:
    - "tests/**"          # Duplicate test setup is OK
    - "**/models.py"      # Similar model definitions

srp:
  ignore:
    - "backend/monolith.py"  # Legacy god object
    - "**/admin.py"          # Admin classes often complex
```

### Version Notes

- **0.4.1+**: Ignore patterns fully functional for magic-numbers linter
- **0.4.0**: Ignore patterns not implemented (known bug, fixed in 0.4.1)
- **Earlier**: Check release notes for ignore support per linter

## File Formats

### YAML Format (Recommended)

**`.thailint.yaml`:**

```yaml
# File placement linter configuration
file-placement:
  # Global patterns apply to all directories
  global_patterns:
    allow:
      - pattern: ".*\\.py$"
        message: "Python files are allowed"
    deny:
      - pattern: "^(?!src/|tests/).*\\.py$"
        message: "Python files must be in src/ or tests/"

  # Directory-specific rules
  directories:
    src:
      allow:
        - ".*\\.py$"
      deny:
        - "test_.*\\.py$"

    tests:
      allow:
        - "test_.*\\.py$"
        - "conftest\\.py$"
        - "__init__\\.py$"

  # Files and directories to ignore
  ignore:
    - "__pycache__/"
    - "*.pyc"
    - ".venv/"
    - ".git/"
    - "node_modules/"

# Future linters can be added as separate top-level sections
# code-quality:
#   max-complexity: 10
#   ...
```

### JSON Format

**`.thailint.json`:**

```json
{
  "file-placement": {
    "global_patterns": {
      "allow": [
        {
          "pattern": ".*\\.py$",
          "message": "Python files are allowed"
        }
      ],
      "deny": [
        {
          "pattern": "^(?!src/|tests/).*\\.py$",
          "message": "Python files must be in src/ or tests/"
        }
      ]
    },
    "directories": {
      "src": {
        "allow": [".*\\.py$"],
        "deny": ["test_.*\\.py$"]
      },
      "tests": {
        "allow": ["test_.*\\.py$", "conftest\\.py$", "__init__\\.py$"]
      }
    },
    "ignore": [
      "__pycache__/",
      "*.pyc",
      ".venv/",
      ".git/",
      "node_modules/"
    ]
  }
}
```

## Output Formats

thailint supports three output formats for linting results:

### Text Format (Default)

Human-readable format for terminal output:

```bash
thailint nesting src/
# or explicitly
thailint nesting --format text src/
```

**Example output:**
```
src/processor.py:42:9 - Nesting depth 5 exceeds maximum 4 in function 'process_data'
src/handler.py:88:13 - Nesting depth 6 exceeds maximum 4 in function 'handle_request'

Found 2 violations
```

### JSON Format

Machine-readable JSON for custom tooling and CI/CD:

```bash
thailint nesting --format json src/
```

**Example output:**
```json
[
  {
    "rule_id": "nesting.excessive-depth",
    "message": "Nesting depth 5 exceeds maximum 4",
    "file_path": "src/processor.py",
    "line": 42,
    "column": 8
  }
]
```

### SARIF Format

SARIF (Static Analysis Results Interchange Format) v2.1.0 for GitHub Code Scanning, Azure DevOps, and VS Code:

```bash
thailint nesting --format sarif src/ > results.sarif
```

**Example output:**
```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "runs": [{
    "tool": {
      "driver": {
        "name": "thai-lint",
        "version": "0.5.0",
        "informationUri": "https://github.com/be-wise-be-kind/thai-lint"
      }
    },
    "results": [...]
  }]
}
```

**Use cases:**
- GitHub Code Scanning integration
- VS Code SARIF Viewer
- Azure DevOps security dashboard
- Enterprise security tooling

See [SARIF Output Guide](sarif-output.md) for comprehensive documentation on SARIF integration.

## Configuration Schema

### Root Level Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `file-placement` | object | No | File placement linter configuration |
| `nesting` | object | No | Nesting depth linter configuration |
| `srp` | object | No | Single Responsibility Principle linter configuration |
| `dry` | object | No | DRY (Don't Repeat Yourself) linter configuration |
| `magic-numbers` | object | No | Magic numbers linter configuration |
| `code-quality` | object | No | Code quality linter configuration (future) |

### File Placement Linter Options

Under the `file-placement` key:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `global_patterns` | object | No | Patterns that apply to all directories |
| `directories` | object | No | Directory-specific rule configurations |
| `ignore` | array | No | Files/directories to skip during linting |

### Nesting Depth Linter Options

Under the `nesting` key:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable nesting depth linter |
| `max_nesting_depth` | integer | `4` | Maximum allowed nesting depth within functions |

**Example:**

```yaml
nesting:
  enabled: true
  max_nesting_depth: 3  # Stricter than default
```

```json
{
  "nesting": {
    "enabled": true,
    "max_nesting_depth": 3
  }
}
```

### Single Responsibility Principle (SRP) Linter Options

Under the `srp` key:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable SRP linter |
| `max_responsibility_score` | integer | `5` | Maximum allowed responsibility score |

**Example:**

```yaml
srp:
  enabled: true
  max_responsibility_score: 4
```

```json
{
  "srp": {
    "enabled": true,
    "max_responsibility_score": 4
  }
}
```

### DRY (Don't Repeat Yourself) Linter Options

Under the `dry` key:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable DRY linter |
| `min_duplicate_lines` | integer | `4` | Minimum lines for duplicate detection |
| `min_duplicate_tokens` | integer | `30` | Minimum tokens for duplicate detection |
| `min_occurrences` | integer | `2` | Report duplicates appearing N+ times |
| `storage_mode` | string | `"memory"` | SQLite storage mode: `"memory"` (RAM) or `"tempfile"` (disk) |
| `ignore` | array | `[]` | Files/directories to exclude from DRY analysis |
| `filters` | object | See below | False positive filtering configuration |
| `python` | object | `{}` | Python-specific threshold overrides |
| `typescript` | object | `{}` | TypeScript-specific threshold overrides |
| `javascript` | object | `{}` | JavaScript-specific threshold overrides |

**Filter Options** (under `dry.filters`):

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `keyword_argument_filter` | boolean | `true` | Filter duplicate keyword argument patterns |
| `import_group_filter` | boolean | `true` | Filter duplicate import statement groups |

**Language-Specific Overrides:**

Each language key (`python`, `typescript`, `javascript`) supports:

| Option | Type | Description |
|--------|------|-------------|
| `min_duplicate_lines` | integer | Override global line threshold |
| `min_duplicate_tokens` | integer | Override global token threshold |
| `min_occurrences` | integer | Override global occurrence threshold |

**Complete YAML Example:**

```yaml
dry:
  enabled: true

  # Detection thresholds
  min_duplicate_lines: 4
  min_duplicate_tokens: 30
  min_occurrences: 2

  # Storage configuration
  storage_mode: "memory"  # Options: "memory" (default, fast) or "tempfile" (for large projects)

  # Language-specific thresholds
  python:
    min_occurrences: 3      # Python: require 3+ duplicates
    min_duplicate_lines: 5  # Python: stricter line threshold

  typescript:
    min_duplicate_tokens: 35  # TypeScript: require more tokens

  javascript:
    min_occurrences: 2  # JavaScript: use global default

  # Ignore patterns
  ignore:
    - "tests/"
    - "__init__.py"
    - "migrations/"
    - "*.generated.py"

  # False positive filtering
  filters:
    keyword_argument_filter: true
    import_group_filter: true
```

**Complete JSON Example:**

```json
{
  "dry": {
    "enabled": true,
    "min_duplicate_lines": 4,
    "min_duplicate_tokens": 30,
    "min_occurrences": 2,
    "storage_mode": "memory",
    "python": {
      "min_occurrences": 3,
      "min_duplicate_lines": 5
    },
    "typescript": {
      "min_duplicate_tokens": 35
    },
    "javascript": {
      "min_occurrences": 2
    },
    "ignore": [
      "tests/",
      "__init__.py",
      "migrations/",
      "*.generated.py"
    ],
    "filters": {
      "keyword_argument_filter": true,
      "import_group_filter": true
    }
  }
}
```

**Configuration Hierarchy:**

Language-specific settings override global settings:

1. **Language-specific** (highest priority): `dry.python.min_occurrences`
2. **Global defaults** (fallback): `dry.min_occurrences`

**Storage Behavior:**

- SQLite storage used for fast duplicate detection during each run
- `storage_mode: "memory"` (default): Stores in RAM for best performance
- `storage_mode: "tempfile"`: Stores in temporary disk file for large projects
- Storage is automatically cleared after each run
- Every run analyzes files fresh (no persistence between runs)

**Filter Behavior:**

Filters reduce false positives:

- **keyword_argument_filter**: Ignores function calls with only keyword arguments (common pattern in configs)
- **import_group_filter**: Ignores import statement groups (naturally similar structure)

### Magic Numbers Linter Options

Under the `magic-numbers` key:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable magic numbers linter |
| `allowed_numbers` | array | `[-1, 0, 1, 2, 10, 100, 1000]` | Numbers that are acceptable without named constants |
| `max_small_integer` | integer | `10` | Maximum value allowed in `range()` or `enumerate()` without being flagged |

**Example:**

```yaml
magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 10, 100, 1000]
  max_small_integer: 10
```

```json
{
  "magic-numbers": {
    "enabled": true,
    "allowed_numbers": [-1, 0, 1, 2, 10, 100, 1000],
    "max_small_integer": 10
  }
}
```

**Configuration Behavior:**

- **allowed_numbers**: Numbers in this list will not be flagged as magic numbers. Common values like `-1`, `0`, `1`, `2` are often self-explanatory and don't need constants.
- **max_small_integer**: Small integers used in `range()` or `enumerate()` below this threshold are considered acceptable (e.g., `range(5)` is clear, but `range(100)` should use a constant).

**Acceptable Contexts** (always allowed regardless of config):

- **Constant definitions**: Numbers assigned to UPPERCASE variable names (e.g., `MAX_SIZE = 100`)
- **Small integers in `range()`**: Integers ≤ `max_small_integer` in `range()` calls
- **Small integers in `enumerate()`**: Integers ≤ `max_small_integer` as start value in `enumerate()`
- **Test files**: Numbers in files matching `test_*.py`, `*_test.py`, `*.test.ts`, `*.spec.ts` patterns
- **String repetition**: Integers used for string multiplication (e.g., `"-" * 40`)

**Complete YAML Example:**

```yaml
magic-numbers:
  enabled: true

  # Numbers that don't need constants (self-explanatory)
  allowed_numbers:
    - -1   # Common error/not-found indicator
    - 0    # Zero/false/empty
    - 1    # One/true/first
    - 2    # Two/second
    - 10   # Decimal base
    - 100  # Percentage base
    - 1000 # Thousand

  # Maximum integer allowed in range() without constant
  max_small_integer: 10
```

**Complete JSON Example:**

```json
{
  "magic-numbers": {
    "enabled": true,
    "allowed_numbers": [-1, 0, 1, 2, 10, 100, 1000],
    "max_small_integer": 10
  }
}
```

**Customization Examples:**

```yaml
# Strict - only very common values allowed
magic-numbers:
  allowed_numbers: [-1, 0, 1]
  max_small_integer: 3

# Standard - recommended (default)
magic-numbers:
  allowed_numbers: [-1, 0, 1, 2, 10, 100, 1000]
  max_small_integer: 10

# Lenient - includes time units
magic-numbers:
  allowed_numbers: [-1, 0, 1, 2, 10, 24, 60, 100, 1000, 3600]
  max_small_integer: 20
```

### Global Patterns

Apply rules across the entire project regardless of directory.

```yaml
file-placement:
  global_patterns:
    allow:
      - pattern: ".*\\.py$"
        message: "Python files are allowed globally"

    deny:
      - pattern: "secret.*"
        message: "Files containing 'secret' are not allowed"
```

**Fields:**
- `pattern` (string, required): Regex pattern to match file paths
- `message` (string, optional): Custom error message when pattern matches

### Directory-Specific Rules

Define rules that apply only within specific directories.

```yaml
file-placement:
  directories:
    # Directory name (relative to project root)
    src:
      # Allowlist: Only these patterns are allowed
      allow:
        - ".*\\.py$"           # Python source files
        - ".*\\.pyi$"          # Type stub files
        - "__init__\\.py$"     # Package init files

      # Denylist: These patterns are forbidden
      deny:
        - "test_.*\\.py$"      # No test files in src/
        - ".*_test\\.py$"      # No test files in src/
```

**Pattern Precedence:**
1. **Deny takes precedence**: If a file matches both allow and deny, it's denied
2. **Most specific wins**: More specific patterns override general ones
3. **Directory rules override global**: Directory-specific rules take precedence over global patterns

### Ignore Patterns

Files and directories to skip during linting.

```yaml
file-placement:
  ignore:
    - "__pycache__/"     # Python cache directories
    - "*.pyc"            # Compiled Python files
    - "*.pyo"            # Optimized Python files
    - ".venv/"           # Virtual environments
    - "venv/"
    - ".git/"            # Version control
    - ".svn/"
    - "node_modules/"    # Node.js dependencies
    - ".DS_Store"        # macOS metadata
    - "*.egg-info/"      # Python package metadata
    - "dist/"            # Build artifacts
    - "build/"
    - ".pytest_cache/"   # Test cache
    - ".mypy_cache/"     # Type checker cache
    - ".ruff_cache/"     # Linter cache
```

**Ignore Pattern Formats:**
- **Exact match**: `.git/` matches `.git/` directory
- **Wildcard**: `*.pyc` matches all `.pyc` files
- **Directory wildcard**: `*/temp/` matches any `temp` subdirectory

## Pattern Syntax

### Regex Patterns

thailint uses Python regex (re module) for pattern matching.

**Common Patterns:**

```yaml
# File extensions
".*\\.py$"           # Python files
".*\\.(ts|tsx)$"     # TypeScript files
".*\\.(js|jsx)$"     # JavaScript files

# Naming conventions
"test_.*\\.py$"      # Test files (prefix)
".*_test\\.py$"      # Test files (suffix)
"^[A-Z].*\\.py$"     # Files starting with uppercase

# Path patterns
"^src/.*\\.py$"      # Python files in src/
"^(?!src/).*\\.py$"  # Python files NOT in src/
"^(src|lib)/.*$"     # Files in src/ OR lib/

# Special files
"__init__\\.py$"     # Package init files
"conftest\\.py$"     # Pytest config files
```

**Regex Special Characters:**

| Character | Meaning | Example |
|-----------|---------|---------|
| `.` | Any character | `a.c` matches "abc", "a1c" |
| `*` | Zero or more of previous | `a*` matches "", "a", "aa" |
| `+` | One or more of previous | `a+` matches "a", "aa" |
| `?` | Zero or one of previous | `a?` matches "", "a" |
| `^` | Start of string | `^src/` matches "src/file.py" |
| `$` | End of string | `\\.py$` matches "file.py" |
| `\|` | OR operator | `(a\|b)` matches "a" or "b" |
| `[]` | Character class | `[abc]` matches "a", "b", or "c" |
| `[^]` | Negated class | `[^abc]` matches anything except a, b, c |
| `()` | Grouping | `(test\|spec)` groups alternatives |
| `\\` | Escape character | `\\.` matches literal "." |

**Important**: Escape special characters in YAML strings:
```yaml
# Wrong - dot matches any character
allow:
  - "file.py"

# Correct - dot is escaped to match literal "."
allow:
  - "file\\.py"
```

### Negative Lookahead

Exclude specific paths using negative lookahead:

```yaml
# Match Python files NOT in src/ or tests/
"^(?!src/|tests/).*\\.py$"

# Match files NOT starting with "test_"
"^(?!test_).*\\.py$"

# Match TypeScript files NOT in node_modules/
"^(?!.*node_modules/).*\\.ts$"
```

## Example Configurations

### Python Project

```yaml
file-placement:
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

  ignore:
    - "__pycache__/"
    - "*.pyc"
    - ".venv/"
    - ".pytest_cache/"
    - "*.egg-info/"
```

### TypeScript/React Project

```yaml
file-placement:
  global_patterns:
    deny:
      - pattern: "^(?!src/|tests/|scripts/).*\\.(ts|tsx)$"
        message: "TypeScript files must be in src/, tests/, or scripts/"

  directories:
    src:
      allow:
        - ".*\\.tsx?$"        # .ts or .tsx files
        - ".*\\.css$"
        - ".*\\.scss$"
      deny:
        - ".*\\.test\\.tsx?$"
        - ".*\\.spec\\.tsx?$"

    tests:
      allow:
        - ".*\\.test\\.tsx?$"
        - ".*\\.spec\\.tsx?$"

  ignore:
    - "node_modules/"
    - "dist/"
    - "build/"
    - "*.d.ts"
    - ".next/"
```

### Monorepo Configuration

```yaml
global_patterns:
  deny:
    - pattern: "^(?!packages/|apps/|libs/).*\\.(py|ts|tsx|js|jsx)$"
      message: "Code files must be in packages/, apps/, or libs/"

directories:
  # Backend package
  packages/backend/src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"

  packages/backend/tests:
    allow:
      - "test_.*\\.py$"
      - "conftest\\.py$"

  # Frontend app
  apps/web/src:
    allow:
      - ".*\\.(tsx?|jsx?|css|scss)$"
    deny:
      - ".*\\.(test|spec)\\.(tsx?|jsx?)$"

  apps/web/tests:
    allow:
      - ".*\\.(test|spec)\\.(tsx?|jsx?)$"

ignore:
  - "**/node_modules/"
  - "**/__pycache__/"
  - "**/dist/"
  - "**/build/"
```

### Microservices Architecture

```yaml
directories:
  # API Service
  services/api/src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*"

  services/api/tests:
    allow:
      - "test_.*\\.py$"

  # Auth Service
  services/auth/src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*"

  services/auth/tests:
    allow:
      - "test_.*\\.py$"

  # Shared libraries
  shared/libs:
    allow:
      - ".*\\.py$"

ignore:
  - "**/__pycache__/"
  - "**/.venv/"
  - "**/dist/"
```

## Advanced Patterns

### Complex Directory Structures

```yaml
directories:
  # Allow only models in models directory
  src/models:
    allow:
      - ".*_model\\.py$"
      - "__init__\\.py$"
    deny:
      - "^(?!.*_model\\.py$|__init__\\.py$).*"

  # Controllers must end with _controller.py
  src/controllers:
    allow:
      - ".*_controller\\.py$"
      - "__init__\\.py$"

  # Services must end with _service.py
  src/services:
    allow:
      - ".*_service\\.py$"
      - "__init__\\.py$"
```

### File Naming Conventions

```yaml
directories:
  src/components:
    # React components: PascalCase.tsx
    allow:
      - "^[A-Z][a-zA-Z0-9]*\\.tsx$"
      - "index\\.tsx?$"
    deny:
      - "^[a-z].*\\.tsx$"  # No lowercase component names

  src/utils:
    # Utilities: snake_case.py or kebab-case.ts
    allow:
      - "^[a-z][a-z0-9_]*\\.py$"
      - "^[a-z][a-z0-9-]*\\.ts$"
    deny:
      - "^[A-Z].*"  # No PascalCase utilities
```

### Environment-Specific Files

```yaml
directories:
  config:
    allow:
      - "^(development|staging|production)\\.yaml$"
      - "^config\\..*\\.(yaml|json)$"
    deny:
      - ".*\\.local\\..*"  # No local override files in repo

  environments:
    allow:
      - "^\\.env\\.(development|staging|production)$"
    deny:
      - "^\\.env$"  # No unqualified .env files
```

## Inline Configuration

Override config file with CLI flags:

```bash
# Inline JSON rules (single quotes for shell, double quotes for JSON)
thai-lint file-placement . --rules '{
  "allow": [".*\\.py$"],
  "deny": ["test_.*\\.py$"]
}'

# Compact format
thai-lint file-placement . --rules '{"allow": [".*\\.py$"], "deny": ["test_.*"]}'
```

## Validation and Testing

### Validate Configuration

```bash
# Test config with verbose output
thai-lint --verbose lint file-placement . --config .thailint.yaml

# Check specific directory
thai-lint file-placement src/ --config .thailint.yaml
```

### Debug Pattern Matching

Use Python regex tester:

```python
import re

pattern = r"^(?!src/|tests/).*\.py$"
test_paths = ["main.py", "src/api.py", "tests/test_api.py"]

for path in test_paths:
    match = re.match(pattern, path)
    print(f"{path}: {'MATCH' if match else 'NO MATCH'}")
```

Output:
```
main.py: MATCH
src/api.py: NO MATCH
tests/test_api.py: NO MATCH
```

## Best Practices

### 1. Start Simple, Expand Gradually

```yaml
# Start with basic rules
directories:
  src:
    allow:
      - ".*\\.py$"

# Expand as needed
directories:
  src:
    allow:
      - ".*\\.py$"
    deny:
      - "test_.*\\.py$"
```

### 2. Use Comments for Complex Patterns

```yaml
directories:
  src:
    deny:
      # No test files in src/ - they belong in tests/
      - "test_.*\\.py$"

      # No temporary or local files
      - ".*\\.local\\.py$"
      - ".*\\.tmp\\.py$"

      # No backup files
      - ".*\\.bak$"
      - ".*~$"
```

### 3. Leverage Global Patterns for Project-Wide Rules

```yaml
# Global deny patterns apply everywhere
global_patterns:
  deny:
    # No secrets anywhere
    - pattern: ".*secret.*"
      message: "Files containing 'secret' are forbidden"

    # No credentials
    - pattern: ".*credentials.*"
      message: "Credential files should not be committed"

    # Python files only in designated directories
    - pattern: "^(?!src/|tests/|scripts/).*\\.py$"
      message: "Python files must be in src/, tests/, or scripts/"
```

### 4. Test Patterns Before Deployment

```bash
# Test on small subset first
thai-lint file-placement src/ --config .thailint.yaml

# Then expand to full project
thai-lint file-placement . --config .thailint.yaml
```

### 5. Document Custom Patterns

```yaml
# Document why patterns exist
directories:
  src/api:
    # API endpoints must use _api.py suffix for clarity
    # This helps distinguish endpoints from business logic
    allow:
      - ".*_api\\.py$"
      - "__init__\\.py$"
```

## Troubleshooting

### Pattern Not Matching

**Problem**: Pattern doesn't match expected files

**Solution**: Check regex escaping
```yaml
# Wrong - matches any character followed by "py"
".*\.py"

# Correct - matches literal ".py" extension
".*\\.py$"
```

### Deny Pattern Not Working

**Problem**: Files still pass despite deny pattern

**Solution**: Remember deny takes precedence, check pattern specificity
```yaml
# This will deny test files even if they match allow
directories:
  src:
    allow:
      - ".*\\.py$"  # Allows all Python files
    deny:
      - "test_.*\\.py$"  # But denies test files (deny wins)
```

### Config File Not Found

**Problem**: "Config file not found" error

**Solutions**:
1. Ensure file is named `.thailint.yaml` or `.thailint.json`
2. Check file is in current directory or project root
3. Use `--config` to specify explicitly:
   ```bash
   thai-lint file-placement . --config /path/to/config.yaml
   ```

### Invalid YAML/JSON

**Problem**: Parse error when loading config

**Solution**: Validate syntax
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.thailint.yaml'))"

# Validate JSON
python -c "import json; json.load(open('.thailint.json'))"
```

## Configuration Templates

### Minimal Configuration

```yaml
directories:
  src:
    allow:
      - ".*\\.py$"
```

### Standard Python Project

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
      - "test_.*"

  tests:
    allow:
      - "test_.*\\.py$"
      - "conftest\\.py$"

ignore:
  - "__pycache__/"
  - ".venv/"
  - "*.pyc"
```

### Multi-Language Project

```yaml
global_patterns:
  deny:
    - pattern: "^(?!src/|tests/).*\\.(py|ts|tsx|js|jsx)$"
      message: "Code files must be in src/ or tests/"

directories:
  src:
    allow:
      - ".*\\.(py|ts|tsx|js|jsx)$"
    deny:
      - ".*(test|spec)\\.(py|ts|tsx|js|jsx)$"

  tests:
    allow:
      - ".*(test|spec)\\.(py|ts|tsx|js|jsx)$"

ignore:
  - "__pycache__/"
  - "node_modules/"
  - "*.pyc"
  - "dist/"
  - "build/"
```

## Next Steps

- **[Getting Started](getting-started.md)** - Basic configuration setup
- **[File Placement Linter](file-placement-linter.md)** - Detailed linter documentation
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Programmatic configuration
