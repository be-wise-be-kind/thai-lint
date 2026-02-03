# LBYL Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the LBYL linter for detecting "Look Before You Leap" anti-patterns

    **Scope**: Configuration, usage, refactoring patterns, and best practices for LBYL detection in Python code

    **Overview**: Comprehensive documentation for the LBYL linter that detects "Look Before You Leap" anti-patterns in Python code. LBYL patterns involve checking a condition before performing an operation that could raise an exception. The Pythonic alternative is EAFP (Easier to Ask Forgiveness than Permission) - using try/except blocks. Covers the 8 detected patterns, configuration options, CLI usage, false positive filtering, and refactoring guidance.

    **Dependencies**: ast module (Python parser)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: AST-based detection with pattern-specific detectors for each LBYL anti-pattern

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint lbyl src/
```

**Example output:**
```
src/utils.py:15 - LBYL anti-pattern: checking 'key in config' before accessing config[key]
  Suggestion: Use try/except KeyError instead: try: value = config[key] except KeyError: ...
```

**Fix it:** Replace LBYL checks with EAFP try/except patterns.

---

## Overview

The LBYL linter detects "Look Before You Leap" anti-patterns in Python code - patterns where you check if an operation will succeed before performing it, rather than just trying the operation and handling any exceptions.

### What is LBYL vs EAFP?

**LBYL (Look Before You Leap)** - Check before acting:
```python
# Anti-pattern - LBYL
if key in config:
    value = config[key]
else:
    value = default
```

**EAFP (Easier to Ask Forgiveness than Permission)** - Try and handle exceptions:
```python
# Pythonic - EAFP
try:
    value = config[key]
except KeyError:
    value = default

# Or even simpler:
value = config.get(key, default)
```

### Why EAFP is Preferred in Python

1. **Race conditions**: LBYL checks can become stale between check and use
2. **Performance**: Exception handling is optimized in Python; checking twice is slower
3. **Readability**: EAFP focuses on the happy path, with exceptions handling edge cases
4. **Duck typing**: EAFP works with any object that supports the operation
5. **Atomicity**: try/except is atomic; LBYL requires two separate operations

### Detected Patterns

The LBYL linter detects 8 anti-patterns:

| Pattern | Default | What It Detects |
|---------|---------|-----------------|
| `dict_key` | Enabled | `if key in d: d[key]` |
| `hasattr` | Enabled | `if hasattr(obj, 'attr'): obj.attr` |
| `isinstance` | **Disabled** | `if isinstance(obj, Type): obj.method()` |
| `file_exists` | Enabled | `if os.path.exists(f): open(f)` |
| `len_check` | Enabled | `if len(items) > 0: items[0]` |
| `none_check` | **Disabled** | `if obj is not None: obj.method()` |
| `string_validation` | Enabled | `if s.isdigit(): int(s)` |
| `division_check` | Enabled | `if divisor != 0: x / divisor` |

**Note**: `isinstance` and `none_check` are disabled by default because they have many valid use cases.

---

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
lbyl:
  enabled: true
  detect_dict_key: true
  detect_hasattr: true
  detect_isinstance: false      # Disabled - many valid uses
  detect_file_exists: true
  detect_len_check: true
  detect_none_check: false      # Disabled - many valid uses
  detect_string_validation: true
  detect_division_check: true
  ignore: []                    # File patterns to ignore
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable LBYL linter |
| `detect_dict_key` | boolean | `true` | Detect `if key in dict: dict[key]` patterns |
| `detect_hasattr` | boolean | `true` | Detect `if hasattr(...): obj.attr` patterns |
| `detect_isinstance` | boolean | `false` | Detect `if isinstance(...): ...` patterns |
| `detect_file_exists` | boolean | `true` | Detect `if exists(f): open(f)` patterns |
| `detect_len_check` | boolean | `true` | Detect `if len(x) > 0: x[0]` patterns |
| `detect_none_check` | boolean | `false` | Detect `if x is not None: ...` patterns |
| `detect_string_validation` | boolean | `true` | Detect `if s.isdigit(): int(s)` patterns |
| `detect_division_check` | boolean | `true` | Detect `if x != 0: y / x` patterns |
| `ignore` | array | `[]` | File patterns to ignore (glob syntax) |

### Recommended Configurations

**For strict enforcement (all patterns):**
```yaml
lbyl:
  detect_dict_key: true
  detect_hasattr: true
  detect_isinstance: true
  detect_file_exists: true
  detect_len_check: true
  detect_none_check: true
  detect_string_validation: true
  detect_division_check: true
```

**For lenient enforcement (defaults):**
```yaml
lbyl:
  detect_isinstance: false
  detect_none_check: false
```

### Ignoring Files

```yaml
lbyl:
  ignore:
    - "tests/**"              # Ignore test files
    - "**/migrations/**"      # Ignore migrations
    - "scripts/**"            # Ignore scripts
```

---

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint lbyl .

# Check specific directory
thailint lbyl src/

# Check specific file
thailint lbyl src/utils.py
```

#### With Configuration

```bash
# Use config file
thailint lbyl --config .thailint.yaml src/

# Auto-discover config
thailint lbyl src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint lbyl src/

# JSON output for CI/CD
thailint lbyl --format json src/

# SARIF output for IDE integration
thailint lbyl --format sarif src/ > report.sarif
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest lbyl /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest lbyl \
  --config /config/.thailint.yaml /workspace/src/
```

---

## Pattern Details

### Pattern 1: Dict Key Check (`detect_dict_key`)

**Detects:**
```python
# Anti-pattern
if key in config:
    value = config[key]
```

**EAFP alternative:**
```python
# Option 1: try/except
try:
    value = config[key]
except KeyError:
    value = default

# Option 2: dict.get() (preferred for simple cases)
value = config.get(key, default)
```

**False positives avoided:**
- Different dict/key combinations: `if k in d1: d2[k]`
- Walrus operator patterns: `if (val := d.get(k)) is not None:`
- dict.get() usage (not flagged)

---

### Pattern 2: hasattr Check (`detect_hasattr`)

**Detects:**
```python
# Anti-pattern
if hasattr(obj, 'process'):
    obj.process()
```

**EAFP alternative:**
```python
# Option 1: try/except AttributeError
try:
    obj.process()
except AttributeError:
    handle_missing_method()

# Option 2: getattr with default
processor = getattr(obj, 'process', None)
if processor:
    processor()
```

---

### Pattern 3: isinstance Check (`detect_isinstance`)

**Default: Disabled** - Many valid uses for type narrowing in type-safe code.

**Detects:**
```python
# Anti-pattern
if isinstance(obj, MyClass):
    obj.my_method()
```

**EAFP alternative:**
```python
# Duck typing - just try it
try:
    obj.my_method()
except AttributeError:
    handle_incompatible_type()
```

**When to enable:** Enable this pattern only if you want to enforce strict duck typing.

---

### Pattern 4: File Exists Check (`detect_file_exists`)

**Detects:**
```python
# Anti-pattern - os.path.exists
if os.path.exists(filepath):
    with open(filepath) as f:
        data = f.read()

# Anti-pattern - pathlib
if path.exists():
    content = path.read_text()
```

**EAFP alternative:**
```python
# Option 1: try/except
try:
    with open(filepath) as f:
        data = f.read()
except FileNotFoundError:
    data = default_data

# Option 2: pathlib with try/except
try:
    content = path.read_text()
except FileNotFoundError:
    content = ""
```

**Why EAFP is better here:**
- Race condition: file could be deleted between check and open
- Atomic: single operation instead of two
- Handles permission errors naturally

**False positives avoided:**
- Inverted checks: `if not exists(f): create_file(f)` (not flagged)
- Different paths between check and use

---

### Pattern 5: Length Check (`detect_len_check`)

**Detects:**
```python
# Anti-pattern
if len(items) > 0:
    first = items[0]

# Also detects
if len(items) >= 1:
    first = items[0]
```

**EAFP alternative:**
```python
# Option 1: try/except
try:
    first = items[0]
except IndexError:
    first = default

# Option 2: truthiness test (for non-empty check)
if items:  # Pythonic empty check
    first = items[0]
```

**False positives avoided:**
- Legitimate bounds checking: `if len(items) > 5:` (not flagged unless accessing index 5)
- Range checks: `if len(items) < 10:` (typically not flagged)

---

### Pattern 6: None Check (`detect_none_check`)

**Default: Disabled** - Many valid uses for explicit None handling.

**Detects:**
```python
# Anti-pattern
if obj is not None:
    result = obj.process()
```

**EAFP alternative:**
```python
# Option 1: try/except
try:
    result = obj.process()
except AttributeError:
    result = default

# Option 2: Optional with default
result = obj.process() if obj else default
```

**When to enable:** Enable only in codebases that prefer exception handling over explicit None checks.

---

### Pattern 7: String Validation (`detect_string_validation`)

**Detects:**
```python
# Anti-patterns
if s.isdigit():
    num = int(s)

if s.isnumeric():
    num = float(s)

if s.isalpha():
    process_letters(s)
```

**EAFP alternative:**
```python
# For int conversion
try:
    num = int(s)
except ValueError:
    num = 0

# For float conversion
try:
    num = float(s)
except ValueError:
    num = 0.0
```

---

### Pattern 8: Division Check (`detect_division_check`)

**Detects:**
```python
# Anti-pattern
if divisor != 0:
    result = numerator / divisor
else:
    result = 0
```

**EAFP alternative:**
```python
try:
    result = numerator / divisor
except ZeroDivisionError:
    result = 0
```

---

## False Positive Filtering

The LBYL linter includes extensive false positive filtering:

### Excluded Patterns

| Pattern | Why Excluded |
|---------|--------------|
| Walrus operator | `if (val := d.get(k)) is not None:` is EAFP |
| dict.get() | Already EAFP pattern |
| Inverted checks | `if not exists(f):` typically creates files |
| Different variables | Check uses `x`, body uses `y` |

### Excluded Contexts

| Context | Example | Why Excluded |
|---------|---------|--------------|
| Guard clauses | Early returns with isinstance | Valid pattern for type narrowing |
| Protocol checks | hasattr for protocol detection | Valid duck typing check |

---

## Ignore Directives

### Line-Level Ignore

Suppress a single line:

```python
if key in config:  # thailint: ignore[lbyl]
    value = config[key]
```

### Next-Line Ignore

Suppress the next line:

```python
# thailint: ignore-next-line[lbyl]
if key in config:
    value = config[key]
```

### Block-Level Ignore

Suppress a region:

```python
# thailint: ignore-start lbyl
if key in config:
    value = config[key]
if hasattr(obj, 'method'):
    obj.method()
# thailint: ignore-end
```

### File-Level Ignore

Suppress entire file:

```python
# thailint: ignore-file[lbyl]
# At top of file, within first 10 lines
```

### Pattern-Specific Ignore

```python
# Ignore only dict key pattern
if key in config:  # thailint: ignore[lbyl.dict_key]
    value = config[key]
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lbyl-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for LBYL patterns
        run: thailint lbyl src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lbyl-check
        name: Check for LBYL anti-patterns
        entry: thailint lbyl
        language: python
        types: [python]
        pass_filenames: false
        args: ["src/"]
```

### SARIF Integration

```bash
# Generate SARIF report for GitHub Code Scanning
thailint lbyl --format sarif src/ > lbyl-results.sarif
```

```yaml
# GitHub Actions with SARIF upload
- name: Run LBYL linter
  run: thailint lbyl --format sarif src/ > lbyl-results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: lbyl-results.sarif
```

---

## Best Practices

### 1. Start with Defaults

The default configuration (isinstance and none_check disabled) catches the most clear-cut LBYL patterns while avoiding common false positives.

### 2. Use dict.get() for Simple Cases

```python
# Instead of LBYL
if key in config:
    value = config[key]
else:
    value = default

# Use dict.get()
value = config.get(key, default)
```

### 3. Prefer try/except for File Operations

```python
# File operations should always use try/except
try:
    with open(filepath) as f:
        data = f.read()
except FileNotFoundError:
    data = create_default_data()
except PermissionError:
    raise ConfigError(f"Cannot read {filepath}")
```

### 4. Be Specific with Exception Types

```python
# Good - specific exception
try:
    value = config[key]
except KeyError:
    value = default

# Bad - too broad
try:
    value = config[key]
except Exception:  # Don't do this
    value = default
```

### 5. Consider contextlib.suppress for No-Op Handling

```python
from contextlib import suppress

# When you want to silently ignore an exception
with suppress(FileNotFoundError):
    os.remove(temp_file)
```

---

## When to Suppress Violations

### Legitimate Uses of LBYL

1. **Performance-critical code** where exception overhead matters:
   ```python
   # Performance-critical inner loop
   if key in cache:  # thailint: ignore[lbyl] - Performance optimization
       return cache[key]
   ```

2. **External API contracts** that require checking:
   ```python
   # API requires exists check before operation
   if client.resource_exists(id):  # thailint: ignore[lbyl] - API contract
       client.update_resource(id, data)
   ```

3. **Type narrowing for static analysis**:
   ```python
   # MyPy requires isinstance for type narrowing
   if isinstance(obj, SpecificType):  # thailint: ignore[lbyl] - Type narrowing
       obj.specific_method()
   ```

---

## Troubleshooting

### Too Many Violations Initially

```yaml
# Start with fewer patterns enabled
lbyl:
  detect_dict_key: true
  detect_hasattr: false
  detect_isinstance: false
  detect_file_exists: true
  detect_len_check: false
  detect_none_check: false
  detect_string_validation: false
  detect_division_check: false
```

### False Positives in Tests

```yaml
# Exclude test files
lbyl:
  ignore:
    - "tests/**"
    - "**/*_test.py"
    - "**/test_*.py"
```

### Pattern Not Detected

Check that:
1. The pattern is enabled in configuration
2. The check and operation use the same variable/expression
3. The file matches the language (Python only)

---

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[SARIF Output](sarif-output.md)** - CI/CD integration with SARIF
