# Performance Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the performance linter for detecting and fixing performance anti-patterns in loops

    **Scope**: Configuration, usage, refactoring patterns, and best practices for performance analysis

    **Overview**: Comprehensive documentation for the performance linter that detects O(n^2) anti-patterns in Python and TypeScript code. Covers two key rules: string-concat-loop (detecting += string concatenation in loops) and regex-in-loop (detecting uncompiled regex calls in loops). Includes AST-based analysis, configuration options, CLI and library usage, common refactoring patterns, and CI/CD integration.

    **Dependencies**: tree-sitter (Python parser), tree-sitter-typescript (TypeScript parser)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format

    **Implementation**: AST-based pattern detection with helpful violation messages and refactoring suggestions

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thai-lint
thailint perf src/
```

**Example output:**
```
src/utils.py:42:8
  [ERROR] performance.string-concat-loop: String concatenation in for loop: 'result +=' creates O(n^2) complexity

src/parser.py:78:11
  [ERROR] performance.regex-in-loop: Regex compilation in for loop: 're.match()' recompiles pattern on each iteration
```

**Fix it:** Use `"".join()` for string building, and `re.compile()` for regex patterns.

---

## Overview

The performance linter detects common performance anti-patterns in loops that cause O(n^2) time complexity. These patterns are particularly common in AI-generated code and can cause significant slowdowns in production.

### Rules

| Rule | Description | Languages |
|------|-------------|-----------|
| `string-concat-loop` | Detects `+=` string concatenation in loops | Python, TypeScript |
| `regex-in-loop` | Detects uncompiled regex calls in loops | Python |

### Why Performance Patterns Matter

**String Concatenation in Loops:**
- Each `+=` creates a new string object (strings are immutable)
- Copying all previous characters each time = O(n^2) total operations
- With 1000 iterations: ~500,000 character copies instead of ~1000

**Regex in Loops:**
- `re.match(pattern, text)` compiles the regex pattern each call
- Regex compilation is expensive (parsing, NFA construction)
- Pre-compiling with `re.compile()` avoids repeated work

### Real-World Impact

These patterns were found in production codebases:
- **FastAPI** `exceptions.py:197` - String concatenation in loop
- **FastAPI** `scripts/deploy_docs_status.py:83` - Regex in loop

### Benefits

- **Faster execution**: O(n) instead of O(n^2) for string operations
- **Lower memory**: Avoid creating intermediate string objects
- **Reduced CPU**: Compile regex once, not thousands of times
- **Scalability**: Performance issues become critical at scale

## How It Works

### AST-Based Analysis

The linter uses Abstract Syntax Tree (AST) parsing to analyze code structure:

1. **Parse source code** into AST using language-specific parsers:
   - Python: Built-in `ast` module
   - TypeScript: `tree-sitter-typescript` library

2. **Find all loops** in the file (for, while, async for)

3. **Detect patterns** within loops:
   - String concatenation: `+=` assignment with string operand
   - Regex calls: `re.match()`, `re.search()`, etc.

4. **Report violations** with line numbers and fix suggestions

### Pattern Detection

**String Concatenation Detection:**
```python
def build_message(items):
    result = ""           # String variable initialized
    for item in items:
        result += str(item)  # += detected in loop ← VIOLATION
    return result
```

**Regex Detection:**
```python
def find_matches(items, pattern):
    for item in items:
        if re.match(pattern, item):  # re.match() in loop ← VIOLATION
            yield item
```

### Smart Filtering

The linter avoids false positives by:

- **Ignoring numeric +=**: `count += 1` is fine (integer addition)
- **Ignoring list/dict +=**: `items += more` is fine (list extend)
- **Ignoring compiled patterns**: `pattern.match()` is fine (already compiled)
- **Tracking variable types**: Uses heuristics to identify string variables

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
performance:
  enabled: true

  string-concat-loop:
    enabled: true
    report_each_concat: false  # One violation per loop

  regex-in-loop:
    enabled: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable performance linter |
| `string-concat-loop.enabled` | boolean | `true` | Enable string concat detection |
| `string-concat-loop.report_each_concat` | boolean | `false` | Report each += separately |
| `regex-in-loop.enabled` | boolean | `true` | Enable regex detection |

### Ignore Patterns

```yaml
performance:
  enabled: true
  ignore:
    - "tests/**"
    - "scripts/**"
```

## Usage

### CLI Mode

#### Combined Command (All Rules)

```bash
# Check current directory
thailint perf

# Check specific directory
thailint perf src/

# Check specific file
thailint perf src/main.py
```

#### Individual Rules

```bash
# String concatenation only
thailint perf --rule string-concat src/

# Regex in loop only
thailint perf --rule regex-loop src/

# Or use individual commands
thailint string-concat-loop src/
thailint regex-in-loop src/
```

#### With Config File

```bash
# Use config file
thailint perf --config .thailint.yaml src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint perf src/

# JSON output for CI/CD
thailint perf --format json src/

# SARIF output for GitHub Code Scanning
thailint perf --format sarif src/
```

### Library Mode

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with performance rules
violations = linter.lint('src/', rules=['performance'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line} - {v.message}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint perf /workspace/src/

# With specific rule
docker run --rm -v $(pwd):/workspace \
  washad/thailint perf --rule string-concat /workspace/src/
```

## Violation Examples

### Example 1: String Concatenation in Loop (Python)

**Code with violation:**
```python
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item.name}</li>"  # ← VIOLATION
    return f"<ul>{html}</ul>"
```

**Violation message:**
```
src/example.py:4:8
  [ERROR] performance.string-concat-loop: String concatenation in for loop: 'html +=' creates O(n^2) complexity
```

### Example 2: Regex in Loop (Python)

**Code with violation:**
```python
import re

def extract_emails(lines):
    emails = []
    for line in lines:
        match = re.search(r'[\w.]+@[\w.]+', line)  # ← VIOLATION
        if match:
            emails.append(match.group())
    return emails
```

**Violation message:**
```
src/parser.py:7:16
  [ERROR] performance.regex-in-loop: Regex compilation in for loop: 're.search()' recompiles pattern on each iteration
```

### Example 3: TypeScript String Concatenation

**Code with violation:**
```typescript
function buildMessage(items: string[]): string {
  let result = "";
  for (const item of items) {
    result += item;  // ← VIOLATION
  }
  return result;
}
```

## Refactoring Patterns

### Pattern 1: String Concatenation → join()

**Before (O(n^2)):**
```python
def build_message(items):
    result = ""
    for item in items:
        result += str(item)
    return result
```

**After (O(n)):**
```python
def build_message(items):
    return "".join(str(item) for item in items)
```

**Benefits**: Single string allocation, linear time complexity

### Pattern 2: String Concatenation → List Append + Join

**Before (O(n^2)):**
```python
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item.name}</li>\n"
    return f"<ul>\n{html}</ul>"
```

**After (O(n)):**
```python
def build_html(items):
    parts = [f"<li>{item.name}</li>" for item in items]
    return f"<ul>\n{chr(10).join(parts)}\n</ul>"
```

**Benefits**: Lists are mutable, no intermediate string copies

### Pattern 3: Regex → Pre-compile

**Before (slow):**
```python
def find_matches(lines, pattern):
    matches = []
    for line in lines:
        if re.match(pattern, line):
            matches.append(line)
    return matches
```

**After (fast):**
```python
def find_matches(lines, pattern):
    compiled = re.compile(pattern)
    matches = []
    for line in lines:
        if compiled.match(line):
            matches.append(line)
    return matches
```

**Benefits**: Compile once, use many times

### Pattern 4: Regex + Comprehension

**Before:**
```python
def extract_numbers(lines):
    numbers = []
    for line in lines:
        match = re.search(r'\d+', line)
        if match:
            numbers.append(int(match.group()))
    return numbers
```

**After:**
```python
def extract_numbers(lines):
    pattern = re.compile(r'\d+')
    return [int(m.group()) for line in lines if (m := pattern.search(line))]
```

**Benefits**: Concise, efficient, Pythonic

### Pattern 5: TypeScript Array.join()

**Before (O(n^2)):**
```typescript
function buildCSV(rows: string[][]): string {
  let csv = "";
  for (const row of rows) {
    csv += row.join(",") + "\n";
  }
  return csv;
}
```

**After (O(n)):**
```typescript
function buildCSV(rows: string[][]): string {
  return rows.map(row => row.join(",")).join("\n");
}
```

## Ignoring Violations

### Line-Level Ignore

```python
def legacy_builder(items):
    result = ""
    for item in items:
        result += item  # thailint: ignore performance.string-concat-loop
    return result
```

### File-Level Ignore

```python
# thailint: ignore-file performance

def function1():
    # All performance violations ignored in this file
    pass
```

### Config-Level Ignore

```yaml
performance:
  ignore:
    - "tests/**"
    - "scripts/**"
    - "**/legacy/**"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Performance Check

on: [push, pull_request]

jobs:
  performance-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thai-lint
        run: pip install thai-lint

      - name: Check performance patterns
        run: thailint perf src/

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: performance-report.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: performance-check
        name: Check performance patterns
        entry: thailint perf
        language: python
        types: [python]
        pass_filenames: false
```

### Makefile Integration

```makefile
lint-performance:
	@echo "=== Checking performance patterns ==="
	@thailint perf src/ || exit 1

lint-all: lint-performance
	@echo "All checks passed"
```

## Language Support

### Python Support

**Fully Supported**

**String concat detection:**
- `+=` with string literals
- `+=` with f-strings
- `+=` with `str()` calls
- Variables named: result, output, html, text, msg, message, content

**Regex detection:**
- `re.match()`
- `re.search()`
- `re.sub()`
- `re.findall()`
- `re.split()`
- `re.fullmatch()`

**Import variants:**
- `import re`
- `from re import match, search, ...`
- `import re as regex`

### TypeScript Support

**String Concat: Fully Supported**

- `+=` string concatenation in for/while loops
- Template literal concatenation
- Type inference for string variables

**Regex: Not Supported**

TypeScript regex (`/pattern/.test()`) follows different patterns and is not detected.

## Performance

The performance linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse | ~10-30ms | <100ms |
| Single file analysis | ~5-15ms | <50ms |
| 100 files | ~500ms | <2s |
| 1000 files | ~2-3s | <10s |

## Troubleshooting

### Common Issues

**Issue: No violations shown but code has patterns**

```bash
# Check config is loaded
thailint perf --verbose src/

# Verify rules are enabled
cat .thailint.yaml | grep -A5 performance
```

**Issue: False positive on list +=**

The linter uses heuristics to identify string variables. If you get false positives:

```python
# Use explicit ignore
items += more_items  # thailint: ignore performance.string-concat-loop
```

**Issue: Compiled regex flagged**

The linter tracks `re.compile()` assignments. Ensure the pattern variable is used:

```python
# Good - pattern.match() not flagged
pattern = re.compile(r'\d+')
for line in lines:
    pattern.match(line)

# Bad - different variable name
p = re.compile(r'\d+')
for line in lines:
    pattern.match(line)  # Might be flagged if 'pattern' not tracked
```

## Best Practices

### 1. Always Use join() for String Building

```python
# Always prefer
"".join(items)

# Over
result = ""
for item in items:
    result += item
```

### 2. Pre-compile Regex Patterns

```python
# Module-level compilation
EMAIL_PATTERN = re.compile(r'[\w.]+@[\w.]+')

def find_emails(text):
    return EMAIL_PATTERN.findall(text)
```

### 3. Consider List Comprehensions

```python
# Combine filter and transform
[process(x) for x in items if condition(x)]
```

### 4. Benchmark Critical Paths

```python
import timeit

# Measure actual impact
timeit.timeit(lambda: build_string_v1(data), number=1000)
timeit.timeit(lambda: build_string_v2(data), number=1000)
```

### 5. Enforce in CI/CD

Make performance checks mandatory:

```yaml
- name: Performance check
  run: thailint perf --format sarif src/ > perf.sarif
```

## API Reference

### Configuration Schema

```python
@dataclass
class PerformanceConfig:
    enabled: bool = True
    string_concat_enabled: bool = True
    regex_in_loop_enabled: bool = True
    report_each_concat: bool = False
```

### Rule IDs

| Rule ID | Description |
|---------|-------------|
| `performance.string-concat-loop` | String += in loop |
| `performance.regex-in-loop` | re.method() in loop |

### CLI Commands

```bash
# Combined command
thailint perf [--rule RULE] [--format FORMAT] [PATHS...]

# Individual commands
thailint string-concat-loop [--format FORMAT] [PATHS...]
thailint regex-in-loop [--format FORMAT] [PATHS...]
```

## Resources

- **CLI Reference**: `docs/cli-reference.md` - Complete CLI documentation
- **Configuration Guide**: `docs/configuration.md` - Config file reference
- **SARIF Output**: `docs/sarif-output.md` - SARIF integration guide

## Contributing

Report issues or suggest improvements:
- GitHub Issues: https://github.com/be-wise-be-kind/thai-lint/issues
- Feature requests: Tag with `enhancement`
- Bug reports: Tag with `bug`

## Version History

- **v0.13.0**: Performance linter release
  - String concatenation in loop detection (Python + TypeScript)
  - Regex in loop detection (Python)
  - Combined `perf` command with `--rule` filtering
  - 80 tests passing (100%)
  - SARIF output support
