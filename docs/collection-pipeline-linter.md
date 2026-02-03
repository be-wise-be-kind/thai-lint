# Collection Pipeline Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the collection-pipeline linter for detecting for loops with embedded filtering that should use collection pipelines

    **Scope**: Configuration, usage, language support, and best practices for detecting imperative loop patterns with embedded filtering

    **Overview**: Comprehensive documentation for the collection-pipeline linter that detects for loops containing if/continue patterns that could be refactored to use generator expressions, filter(), or comprehensions. Based on Martin Fowler's "Replace Loop with Pipeline" refactoring pattern. Covers how the linter works using AST analysis, configuration options including min_continues threshold, CLI and library usage, ignore patterns, and integration with CI/CD pipelines. Helps teams maintain clean, readable code by separating filtering logic from processing logic.

    **Dependencies**: Python AST module for parsing and pattern detection

    **Exports**: Usage documentation, configuration examples, violation messages, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: AST-based analysis for Python for loops with embedded if/continue filtering patterns

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint pipeline src/
```

**Example output:**
```
src/processor.py:28 - For loop over 'items' has embedded filtering
  Consider: for item in (x for x in items if x.is_valid()):
```

**Fix it:** Extract filter conditions into a generator expression.

---

## Overview

The collection-pipeline linter detects `for` loops with embedded filtering (if/continue patterns) that could be refactored to use collection pipelines such as generator expressions, `filter()`, or list comprehensions.

### Why Detect Embedded Filtering?

Loops with embedded filtering are problematic for several reasons:

- **Mixed concerns**: Filtering logic is interleaved with processing logic
- **Reduced readability**: Intent is obscured by conditional flow control
- **Harder to test**: Filtering can't be tested independently from processing
- **Cognitive load**: Readers must mentally track which items pass through
- **Missed optimization**: Python's built-in itertools are often more efficient

### The Anti-Pattern

```python
# Anti-pattern: Embedded filtering in loop body
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    if ignore_parser.is_ignored(file_path):
        continue
    violations.extend(self.lint_path(file_path))
```

### The Solution

```python
# Collection pipeline: Filtering separated from processing
valid_files = (
    f for f in dir_path.glob(pattern)
    if f.is_file() and not ignore_parser.is_ignored(f)
)
for file_path in valid_files:
    violations.extend(self.lint_path(file_path))
```

### Based on Martin Fowler's Refactoring

This linter implements Martin Fowler's ["Replace Loop with Pipeline"](https://martinfowler.com/articles/refactoring-pipelines.html) refactoring pattern, which advocates for:

- Separating filtering operations from transformation operations
- Using functional-style pipelines for clearer data flow
- Making the sequence of operations explicit and readable

### Fills a Gap in Python Linting

No existing Python linter catches this pattern:

- **Ruff PERF401**: Only catches `if` with append, NOT `continue` pattern
- **Pylint**: No equivalent rule
- **Flake8**: No equivalent rule
- **Sourcery**: Similar patterns but not comprehensive

### AI-Generated Code Pattern

AI coding assistants frequently generate this anti-pattern:

```python
# Common AI pattern - embedded filtering
def process_files(paths):
    results = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            continue
        if is_ignored(path):
            continue
        results.append(analyze(path))
    return results
```

This linter catches these patterns before they accumulate in your codebase.

## How It Works

### Python Analysis

The linter uses Python's `ast` module to detect for loops with if/continue patterns:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Parse Python file into Abstract Syntax Tree (AST)        │
├─────────────────────────────────────────────────────────────┤
│ 2. Walk AST looking for For nodes                           │
├─────────────────────────────────────────────────────────────┤
│ 3. Check if loop body starts with If statements             │
├─────────────────────────────────────────────────────────────┤
│ 4. Verify If body contains only Continue statement          │
├─────────────────────────────────────────────────────────────┤
│ 5. Check for side effects in conditions (walrus operator)   │
├─────────────────────────────────────────────────────────────┤
│ 6. Check ignore directives (line, file, pattern)            │
├─────────────────────────────────────────────────────────────┤
│ 7. Generate refactoring suggestion with generator syntax    │
├─────────────────────────────────────────────────────────────┤
│ 8. Report violations with line numbers and suggestions      │
└─────────────────────────────────────────────────────────────┘
```

### What Gets Detected

**Single if/continue:**
```python
for item in items:
    if not item.is_valid():
        continue
    process(item)
```

**Multiple if/continue:**
```python
for path in paths:
    if not path.is_file():
        continue
    if is_ignored(path):
        continue
    lint(path)
```

### What Gets Ignored (Not Flagged)

**If with else branch:**
```python
for item in items:
    if not item.is_valid():
        continue
    else:
        special_process(item)  # Has else, not a simple filter
    process(item)
```

**Walrus operator (side effects):**
```python
for item in items:
    if not (result := validate(item)):  # Side effect - creates variable
        continue
    process(item, result)
```

**Already using pipeline:**
```python
for item in (x for x in items if x.is_valid()):  # Already a pipeline
    process(item)
```

**Using filter():**
```python
for item in filter(lambda x: x.is_valid(), items):  # Already filtered
    process(item)
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
collection-pipeline:
  enabled: true

  # Minimum if/continue patterns to flag
  # Default: 1
  min_continues: 1

  # Suggest filter() instead of generator expression
  # Default: false
  suggest_filter: false

  # Suggest list comprehension for .append patterns
  # Default: false
  suggest_comprehension: false

  # File patterns to ignore (glob syntax)
  ignore:
    - "tests/**"           # Test files may have intentional patterns
    - "**/legacy/**"       # Legacy code
    - "**/migrations/**"   # Database migrations
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable collection-pipeline linter |
| `min_continues` | integer | `1` | Minimum if/continue patterns to flag |
| `suggest_filter` | boolean | `false` | Suggest filter() instead of generator |
| `suggest_comprehension` | boolean | `false` | Suggest list comp for .append patterns |
| `ignore` | array | `[]` | Glob patterns for files to skip |

### Strictness Presets

```yaml
# Strict - flag even single if/continue
collection-pipeline:
  min_continues: 1

# Standard - flag two or more (default)
collection-pipeline:
  min_continues: 1

# Lenient - only flag complex patterns
collection-pipeline:
  min_continues: 2
```

### JSON Configuration

```json
{
  "collection-pipeline": {
    "enabled": true,
    "min_continues": 1,
    "suggest_filter": false,
    "suggest_comprehension": false,
    "ignore": [
      "tests/**",
      "**/legacy/**"
    ]
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete guide.

**Quick examples:**

```python
# File-level ignore (entire file exempt)
# thailint: ignore-file[collection-pipeline]

# Line-level ignore
for item in items:  # thailint: ignore[collection-pipeline]
    if not item.valid:
        continue
    process(item)

# Generic ignore (works for all rules)
for item in items:  # noqa
    if not item.valid:
        continue
    process(item)
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory (recursive by default)
thailint pipeline .

# Check specific directory
thailint pipeline src/

# Check specific file
thailint pipeline src/main.py

# Check multiple paths
thailint pipeline src/ lib/ utils/
```

#### With Configuration

```bash
# Use config file
thailint pipeline --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint pipeline src/
```

#### With Custom Threshold

```bash
# Only flag patterns with 2+ if/continue statements
thailint pipeline --min-continues 2 src/

# Flag all patterns (default)
thailint pipeline --min-continues 1 src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint pipeline src/

# JSON output for CI/CD
thailint pipeline --format json src/

# SARIF output for GitHub Code Scanning
thailint pipeline --format sarif src/ > results.sarif
```

#### CLI Options

```bash
Options:
  -c, --config PATH               Path to config file
  --min-continues INTEGER         Minimum if/continue patterns to flag
  -f, --format [text|json|sarif]  Output format
  --recursive / --no-recursive    Scan directories recursively
  --project-root PATH             Explicit project root directory
  --help                          Show this message and exit
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with collection-pipeline rule
violations = linter.lint('src/', rules=['collection-pipeline'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/data \
  washad/thailint:latest pipeline /data/src/

# With custom config file
docker run --rm \
  -v $(pwd):/data \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest pipeline \
  --config /config/.thailint.yaml /data/src/

# With threshold
docker run --rm -v $(pwd):/data \
  washad/thailint:latest pipeline --min-continues 2 /data/src/
```

## Violation Examples

### Example 1: Single if/continue Pattern

**Code with violation:**
```python
def process_files(paths):
    for path in paths:
        if not path.is_file():
            continue
        analyze(path)
```

**Violation message:**
```
src/processor.py:3 - For loop over 'paths' has embedded filtering.
  Consider using a generator expression:
  for path in (path for path in paths if path.is_file()):
```

**Refactored code:**
```python
def process_files(paths):
    valid_paths = (p for p in paths if p.is_file())
    for path in valid_paths:
        analyze(path)
```

### Example 2: Multiple if/continue Patterns

**Code with violation:**
```python
def lint_directory(dir_path, pattern, ignore_parser):
    for file_path in dir_path.glob(pattern):
        if not file_path.is_file():
            continue
        if ignore_parser.is_ignored(file_path):
            continue
        violations.extend(lint_file(file_path))
```

**Violation message:**
```
src/linter.py:2 - For loop over 'dir_path.glob(pattern)' has 2 filter conditions.
  Consider combining into a collection pipeline:
  for file_path in (file_path for file_path in dir_path.glob(pattern)
                    if file_path.is_file() and not ignore_parser.is_ignored(file_path)):
```

**Refactored code:**
```python
def lint_directory(dir_path, pattern, ignore_parser):
    valid_files = (
        f for f in dir_path.glob(pattern)
        if f.is_file() and not ignore_parser.is_ignored(f)
    )
    for file_path in valid_files:
        violations.extend(lint_file(file_path))
```

### Example 3: Not Flagged - Walrus Operator

**Code (no violation):**
```python
for item in items:
    if not (result := validate(item)):
        continue
    process(item, result)  # Uses result from walrus
```

This is not flagged because the walrus operator (`:=`) has a side effect (creates a variable used later).

## Refactoring Patterns

### Pattern 1: Simple Filter to Generator

**Before:**
```python
for user in users:
    if not user.is_active:
        continue
    send_email(user)
```

**After:**
```python
active_users = (u for u in users if u.is_active)
for user in active_users:
    send_email(user)
```

### Pattern 2: Multiple Conditions Combined

**Before:**
```python
for path in paths:
    if not path.exists():
        continue
    if path.is_dir():
        continue
    if is_hidden(path):
        continue
    process(path)
```

**After:**
```python
valid_paths = (
    p for p in paths
    if p.exists() and not p.is_dir() and not is_hidden(p)
)
for path in valid_paths:
    process(path)
```

### Pattern 3: Named Pipeline for Clarity

**Before:**
```python
for file in files:
    if not file.endswith('.py'):
        continue
    if file.startswith('test_'):
        continue
    lint(file)
```

**After:**
```python
# Descriptive name explains intent
non_test_python_files = (
    f for f in files
    if f.endswith('.py') and not f.startswith('test_')
)
for file in non_test_python_files:
    lint(file)
```

## Language Support

### Python Support

**Fully Supported**

**Detection:** `for` loops with if/continue patterns using AST analysis

**Parser:** Python `ast` module for reliable detection

**Features:**
- Detects single and multiple if/continue patterns
- Inverts conditions for generator syntax suggestion
- Detects walrus operator side effects
- Proper handling of nested conditions

**Supported constructs:**
```python
# Single if/continue
for x in items:
    if not condition:
        continue
    action(x)

# Multiple if/continue
for x in items:
    if not cond1:
        continue
    if not cond2:
        continue
    action(x)

# Negated conditions
for x in items:
    if bad_condition:
        continue
    action(x)
```

### TypeScript Support

**Not Yet Supported**

TypeScript support is planned for a future release.

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  collection-pipeline-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check for embedded filtering patterns
        run: |
          thailint pipeline src/

      - name: Check (SARIF for Code Scanning)
        run: |
          thailint pipeline --format sarif src/ > results.sarif

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
      - id: collection-pipeline-check
        name: Check for embedded filtering patterns
        entry: thailint pipeline
        language: python
        types: [python]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-pipeline:
	@echo "=== Checking for embedded filtering patterns ==="
	@poetry run thailint pipeline src/ || exit 1

lint-all: lint-pipeline
	@echo "All checks passed"
```

### Justfile Integration

```just
# Lint collection pipeline patterns
lint-pipeline *ARGS:
    poetry run python -m src.cli pipeline {{ARGS}}
```

## Performance

The collection-pipeline linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single Python file | ~5-15ms | <50ms |
| 100 files | ~200-500ms | <1s |
| 500 files | ~1-2s | <3s |
| 1000 files | ~2-4s | <5s |

**Optimizations:**
- Language detection via file extension (O(1))
- AST parsing only for Python files
- Early exit on ignore pattern matches
- Minimal memory footprint per file

## Troubleshooting

### Common Issues

**Issue: False positive in test file**

```bash
# Problem
tests/test_processor.py:15 - For loop has embedded filtering
```

**Solution:** Add to ignore patterns:
```yaml
collection-pipeline:
  ignore:
    - "tests/**"
    - "**/test_*.py"
```

**Issue: Want to keep simple patterns**

```bash
# Problem: Flagging simple one-condition filters
```

**Solution:** Increase threshold:
```yaml
collection-pipeline:
  min_continues: 2  # Only flag 2+ conditions
```

**Issue: Walrus operator needed**

```python
# This is NOT flagged - walrus creates needed variable
for item in items:
    if not (result := validate(item)):
        continue
    process(item, result)
```

The linter correctly ignores patterns where the condition has side effects (like the walrus operator creating a variable used later).

**Issue: Legitimate embedded filtering**

```python
# Use inline ignore for intentional patterns
for item in items:  # thailint: ignore[collection-pipeline]
    if not item.ready:
        continue
    process(item)
```

## Best Practices

### 1. Name Your Pipelines

```python
# Bad - anonymous generator
for x in (x for x in items if x.valid and not x.processed):
    handle(x)

# Good - descriptive name
unprocessed_valid_items = (
    x for x in items
    if x.valid and not x.processed
)
for item in unprocessed_valid_items:
    handle(item)
```

### 2. Extract Complex Predicates

```python
# Bad - complex inline condition
valid_files = (f for f in files if f.is_file() and not f.name.startswith('.') and f.suffix == '.py')

# Good - extracted predicate
def is_python_source(f):
    return f.is_file() and not f.name.startswith('.') and f.suffix == '.py'

python_sources = (f for f in files if is_python_source(f))
```

### 3. Consider filter() for Simple Cases

```python
# Generator expression
active = (u for u in users if u.is_active)

# filter() - sometimes cleaner for simple predicates
active = filter(lambda u: u.is_active, users)

# filter() with method reference
strings = filter(str.strip, lines)
```

### 4. Preserve Generator Laziness

```python
# Good - stays lazy
valid = (x for x in items if x.valid)
for item in valid:
    process(item)

# Avoid - converts to list unnecessarily
valid = [x for x in items if x.valid]  # Stores all in memory
for item in valid:
    process(item)
```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation
- **[Martin Fowler: Refactoring with Loops and Collection Pipelines](https://martinfowler.com/articles/refactoring-pipelines.html)** - Original pattern

## Rule Details

| Property | Value |
|----------|-------|
| Rule ID | `collection-pipeline.embedded-filter` |
| Severity | Warning |
| Fixable | Manual |
| Languages | Python |

## Version History

- **v0.10.0**: Collection-pipeline linter release
  - Python for loop detection with AST analysis
  - Single and multiple if/continue pattern detection
  - Configurable `min_continues` threshold
  - Generator expression suggestions
  - 5-level ignore support
  - SARIF output for CI/CD integration
