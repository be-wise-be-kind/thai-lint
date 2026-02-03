# Nesting Depth Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the nesting depth linter for detecting and fixing excessive code nesting

    **Scope**: Configuration, usage, refactoring patterns, and best practices for nesting depth analysis

    **Overview**: Comprehensive documentation for the nesting depth linter that detects excessive nesting in Python, TypeScript, and Rust code. Covers how the linter works using AST analysis, configuration options, CLI and library usage, common refactoring patterns, and integration with CI/CD pipelines. Helps teams maintain readable, maintainable code by enforcing configurable nesting depth limits.

    **Dependencies**: tree-sitter (Python parser), tree-sitter-typescript (TypeScript parser), tree-sitter-rust (Rust parser, optional)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format

    **Implementation**: AST-based depth analysis with configurable limits and helpful violation messages

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint nesting src/
```

**Example output:**
```
src/processor.py:42 - Excessive nesting (depth 5, max 4) in function 'process_data'
  Suggestion: Use guard clauses or extract nested logic to separate functions
```

**Fix it:** Add early returns or extract deeply nested code into helper functions.

---

## Overview

The nesting depth linter detects deeply nested code structures (if/for/while/try statements) that reduce readability and maintainability. It analyzes Python, TypeScript, and Rust code using Abstract Syntax Tree (AST) parsing to accurately calculate nesting depth within functions.

### Why Nesting Depth Matters

Deeply nested code is:
- **Harder to read**: Requires tracking multiple context levels
- **Harder to test**: More branches and edge cases
- **Harder to maintain**: Changes are riskier and more complex
- **More error-prone**: Easy to miss edge cases in deeply nested logic

### Benefits

- **Improved readability**: Flatter code is easier to understand
- **Better testability**: Simpler functions are easier to test
- **Easier maintenance**: Refactored code is more modular
- **Reduced complexity**: Lower cognitive load for developers
- **Team consistency**: Enforces shared code quality standards

## How It Works

### AST-Based Analysis

The linter uses Abstract Syntax Tree (AST) parsing to analyze code structure:

1. **Parse source code** into AST using language-specific parsers:
   - Python: Built-in `ast` module
   - TypeScript: `tree-sitter-typescript` library
   - Rust: `tree-sitter-rust` library (optional dependency)

2. **Find all functions** in the file (functions, methods, lambdas, arrow functions)

3. **Calculate nesting depth** for each function:
   - Start at depth 1 for function body
   - Increment depth for nesting statements (if, for, while, try, etc.)
   - Track maximum depth reached

4. **Report violations** when max depth exceeds configured limit

### Depth Calculation

**Nesting depth starts at 1** for the function body. Each nested block increments the depth:

```python
def example():           # Depth 0 (function definition)
    x = 1               # Depth 1 (function body)
    if condition:       # Depth 2 (first nesting)
        for item in lst: # Depth 3 (second nesting)
            while x:    # Depth 4 (third nesting) ← Violation if max=3
                pass
```

### Statements That Increase Depth

**Python:**
- `if` / `elif` / `else`
- `for` / `while`
- `with` / `async with`
- `try` / `except` / `finally`
- `match` / `case` (Python 3.10+)

**TypeScript:**
- `if` / `else`
- `for` / `for...in` / `for...of`
- `while` / `do...while`
- `try` / `catch` / `finally`
- `switch` / `case`

**Rust:**
- `if` / `else`
- `match` arms
- `for` / `while` / `loop`
- Closure expressions (`|args| { ... }`)
- `async` blocks

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
nesting:
  enabled: true
  max_nesting_depth: 3  # Default: 4
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable nesting linter |
| `max_nesting_depth` | integer | `4` | Maximum allowed nesting depth |

### Recommended Values

| Max Depth | Description | Use Case |
|-----------|-------------|----------|
| `2` | Very strict | New projects, strict coding standards |
| `3` | Strict | **Recommended** - Good balance |
| `4` | Moderate | Default - Reasonable for most code |
| `5` | Lenient | Legacy code, complex domains |

**thai-lint uses max_nesting_depth=3** as its project standard.

### JSON Configuration

```json
{
  "nesting": {
    "enabled": true,
    "max_nesting_depth": 3
  }
}
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thai-lint nesting

# Check specific directory
thai-lint nesting src/

# Check specific file
thai-lint nesting src/main.py
```

#### With Custom Max Depth

```bash
# Use max depth of 3
thai-lint nesting --max-depth 3 src/

# Very strict (max depth 2)
thai-lint nesting --max-depth 2 src/
```

#### With Config File

```bash
# Use config file
thai-lint nesting --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thai-lint nesting src/
```

#### Output Formats

```bash
# Human-readable text (default)
thai-lint nesting src/

# JSON output for CI/CD
thai-lint nesting --format json src/

# JSON with exit code check
thai-lint nesting --format json src/ > report.json
echo "Exit code: $?"
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with nesting rule
violations = linter.lint('src/', rules=['nesting'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_number} - {v.message}")
```

#### Direct Nesting Linter API

```python
from src import nesting_lint

# Lint specific path
violations = nesting_lint(
    'src/main.py',
    max_nesting_depth=3
)

# Process results
for violation in violations:
    print(f"Function: {violation.message}")
    print(f"Depth: (extracted from message)")
```

#### Advanced: Direct Rule Usage

```python
from src.linters.nesting import NestingDepthRule
from src.orchestrator.core import Orchestrator

# Create rule instance
rule = NestingDepthRule()

# Use orchestrator for file processing
orchestrator = Orchestrator(config={'nesting': {'max_nesting_depth': 3}})
violations = orchestrator.lint_file('src/example.py', rules=[rule])
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint nesting /workspace/src/

# With custom max depth
docker run --rm -v $(pwd):/workspace \
  washad/thailint nesting --max-depth 3 /workspace/src/

# With config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint nesting --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: Excessive Nesting (Python)

**Code with violation:**
```python
def process_data(items):
    for item in items:              # Depth 2
        if item.is_valid():         # Depth 3
            try:                    # Depth 4 ← VIOLATION (max=3)
                if item.process():
                    return True
            except Exception:
                pass
    return False
```

**Violation message:**
```
src/example.py:3 - Function 'process_data' has nesting depth 4 (max: 3)
Consider refactoring: early returns, guard clauses, or extract method
```

### Example 2: TypeScript Violation

**Code with violation:**
```typescript
function validateUser(user: User): boolean {
  if (user) {                    // Depth 2
    if (user.isActive) {         // Depth 3
      for (const role of user.roles) {  // Depth 4 ← VIOLATION
        if (role.hasPermission('admin')) {
          return true;
        }
      }
    }
  }
  return false;
}
```

## Refactoring Patterns

Proven patterns for reducing nesting depth:

### Pattern 1: Guard Clauses (Early Returns)

**Before (depth 4):**
```python
def process(data):
    if data:
        if data.is_valid():
            if data.can_process():
                try:
                    return data.process()
                except Exception:
                    return None
    return None
```

**After (depth 2):**
```python
def process(data):
    if not data:
        return None
    if not data.is_valid():
        return None
    if not data.can_process():
        return None

    try:
        return data.process()
    except Exception:
        return None
```

**Benefits**: Reduces nesting, improves readability, exit fast

### Pattern 2: Extract Method

**Before (depth 4):**
```python
def handle_request(request):
    if request.is_valid():
        if request.has_auth():
            for item in request.items:
                if item.needs_processing():
                    # Complex logic here
                    pass
```

**After (depth 2):**
```python
def handle_request(request):
    if not request.is_valid():
        return
    if not request.has_auth():
        return

    process_request_items(request.items)

def process_request_items(items):
    for item in items:
        if item.needs_processing():
            # Complex logic here
            pass
```

**Benefits**: Separation of concerns, reusable code, testability

### Pattern 3: Dispatch Pattern (Replace if-elif-else chains)

**Before (depth 3):**
```python
def handle_event(event_type, data):
    if event_type == 'create':
        if data.is_valid():
            return create_handler(data)
    elif event_type == 'update':
        if data.is_valid():
            return update_handler(data)
    elif event_type == 'delete':
        return delete_handler(data)
```

**After (depth 2):**
```python
HANDLERS = {
    'create': create_handler,
    'update': update_handler,
    'delete': delete_handler,
}

def handle_event(event_type, data):
    handler = HANDLERS.get(event_type)
    if not handler:
        return None
    if event_type in ['create', 'update'] and not data.is_valid():
        return None
    return handler(data)
```

**Benefits**: Extensible, cleaner logic, easier testing

### Pattern 4: Flatten Error Handling

**Before (depth 4):**
```python
def load_config(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return None
        except IOError:
            return None
    return None
```

**After (depth 2):**
```python
def load_config(path):
    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None
```

**Benefits**: Combines exceptions, reduces nesting, clearer flow

### Pattern 5: Invert Conditions

**Before (depth 4):**
```python
def validate(data):
    if data:
        if len(data) > 0:
            if data[0].is_valid():
                return True
    return False
```

**After (depth 1):**
```python
def validate(data):
    return (
        data is not None
        and len(data) > 0
        and data[0].is_valid()
    )
```

**Benefits**: Single expression, no nesting, very clear

## Ignoring Violations

### Line-Level Ignore

```python
def complex_logic():  # thailint: ignore nesting
    if condition1:
        if condition2:
            if condition3:
                if condition4:  # Ignored
                    pass
```

### File-Level Ignore

```python
# thailint: ignore-file nesting

def function1():
    # Deep nesting allowed
    pass
```

### Block Ignore

```python
# thailint: ignore-start nesting
def legacy_function():
    # Deep nesting allowed in this block
    pass

def another_legacy():
    pass
# thailint: ignore-end nesting
```

### TypeScript Ignores

```typescript
// thailint: ignore nesting
function complexLogic() {
  // Deep nesting allowed
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  nesting-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check nesting depth
        run: |
          thai-lint nesting --max-depth 3 src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: nesting-check
        name: Check nesting depth
        entry: thai-lint nesting --max-depth 3
        language: python
        types: [python]
        pass_filenames: false
```

### Makefile Integration

```makefile
lint-nesting:
	@echo "=== Checking nesting depth ==="
	@poetry run python -m src.cli nesting src/ || exit 1

lint-all: lint-nesting
	@echo "All checks passed"
```

## Language Support

### Python Support

**Fully Supported**

**Nesting constructs detected:**
- `if` / `elif` / `else`
- `for` / `while` loops
- `with` / `async with` context managers
- `try` / `except` / `finally` exception handling
- `match` / `case` pattern matching (3.10+)

**Function types detected:**
- Regular functions (`def`)
- Methods (class functions)
- Lambda expressions
- Async functions (`async def`)

### TypeScript Support

**Fully Supported**

**Nesting constructs detected:**
- `if` / `else` conditionals
- `for` / `for...in` / `for...of` loops
- `while` / `do...while` loops
- `try` / `catch` / `finally` exception handling
- `switch` / `case` statements

**Function types detected:**
- Function declarations
- Arrow functions
- Method definitions
- Async functions

### JavaScript Support

**Supported** (via TypeScript parser)

JavaScript files are analyzed using the TypeScript parser, which handles JavaScript syntax.

### Rust Support

**Fully Supported** - Analyzes Rust functions using `tree-sitter-rust`.

**Nesting constructs detected:**

- `if` / `else` conditionals
- `match` arms
- `for` / `while` / `loop` loops
- Closure expressions (`|args| { ... }`)
- `async` blocks

**Function types detected:**

- Free functions (`fn`)
- Methods in `impl` blocks
- Async functions (`async fn`)

**Example:**
```rust
fn process_items(items: &[Item]) {       // Depth 0
    for item in items {                  // Depth 2
        if item.is_valid() {             // Depth 3
            match item.category {        // Depth 4 ← Violation if max=3
                Category::A => { ... }
                Category::B => { ... }
            }
        }
    }
}
```

**Configuration:**
```yaml
nesting:
  rust:
    max_nesting_depth: 3
```

**Requires**: `tree-sitter-rust` (optional dependency). Install with `pip install thailint[rust]` or `pip install thailint[all]`.

## Performance

The nesting linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse | ~10-30ms | <100ms |
| Single file analysis | ~5-15ms | <50ms |
| 100 files | ~500ms | <2s |
| 1000 files | ~2-3s | <10s |

**Optimizations:**
- AST parsing is cached during file processing
- Only functions are analyzed (not module-level code)
- Violations are reported immediately (fail-fast)
- Parallel processing for multiple files (via orchestrator)

## Troubleshooting

### Common Issues

**Issue: No violations shown but code is nested**

```bash
# Solution: Check config file is loaded
thai-lint nesting --verbose src/

# Verify max depth setting
grep max_nesting_depth .thailint.yaml
```

**Issue: Syntax errors reported as violations**

The linter gracefully handles syntax errors by reporting them:

```
src/broken.py:1 - Syntax error: invalid syntax
```

Fix the syntax error and re-run the linter.

**Issue: False positives on valid code**

Some deeply nested code is legitimate. Use ignore directives:

```python
def complex_algorithm():  # thailint: ignore nesting
    # Justified complexity
    pass
```

**Issue: TypeScript files not analyzed**

Ensure `.ts` or `.tsx` extension:

```bash
# Check file extension
ls -la *.ts

# Verify TypeScript support
thai-lint nesting --verbose example.ts
```

## Best Practices

### 1. Start Conservative

Begin with `max_nesting_depth: 4` (default) and gradually reduce to 3 as code is refactored.

### 2. Refactor Incrementally

Fix violations file-by-file, not all at once:

```bash
# Focus on one directory
thai-lint nesting src/core/

# Fix violations, then move to next
thai-lint nesting src/utils/
```

### 3. Use Ignore Directives Sparingly

Only ignore violations when refactoring is truly not feasible:

```python
def legacy_parser():  # thailint: ignore nesting - Complex legacy code, scheduled for rewrite
    pass
```

### 4. Document Refactoring Patterns

Keep a team guide of common refactoring patterns (guard clauses, extract method, etc.).

### 5. Enforce in CI/CD

Make nesting checks mandatory in CI pipeline:

```yaml
- name: Nesting depth check
  run: thai-lint nesting --max-depth 3 src/
```

### 6. Review Violations in PRs

Include nesting depth checks in code review process.

## API Reference

### Configuration Schema

```python
@dataclass
class NestingConfig:
    max_nesting_depth: int = 4  # Maximum allowed depth
```

### Rule Class

```python
class NestingDepthRule(BaseLintRule):
    rule_id: str = "nesting.excessive-depth"
    rule_name: str = "Excessive Nesting Depth"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file for nesting violations."""
```

### Convenience Function

```python
def lint(
    path: str | Path,
    max_nesting_depth: int = 4,
    config: dict[str, Any] | None = None
) -> list[Violation]:
    """Lint path for nesting violations."""
```

## Resources

- **CLI Reference**: `docs/cli-reference.md` - Complete CLI documentation
- **Configuration Guide**: `docs/configuration.md` - Config file reference
- **API Reference**: `docs/api-reference.md` - Library API documentation
- **Violations Report**: `.roadmap/in-progress/nesting-linter/VIOLATIONS.md` - Real refactoring examples

## Contributing

Report issues or suggest improvements:
- GitHub Issues: https://github.com/be-wise-be-kind/thai-lint/issues
- Feature requests: Tag with `enhancement`
- Bug reports: Tag with `bug`

## Version History

- **v0.2.0**: Nesting depth linter release
  - Python and TypeScript support
  - AST-based analysis with tree-sitter
  - Configurable max_nesting_depth
  - CLI and library API
  - 76/76 tests passing (100%)
  - Validated on thai-lint codebase (zero violations)
