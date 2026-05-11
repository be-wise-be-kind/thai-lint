# Law of Demeter Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the law-of-demeter linter for detecting excessive attribute/method chaining

    **Scope**: Configuration, usage, language support, and best practices for detecting Law of Demeter violations

    **Overview**: Comprehensive documentation for the law-of-demeter linter that detects chains of attribute access and method calls that reach through intermediary objects. Uses AST-based analysis for Python and tree-sitter for TypeScript/JavaScript. Features a 9-filter classification pipeline that distinguishes genuine violations from legitimate patterns such as fluent APIs, string method chaining, module-qualified access, and AST traversal. Validated against 20 real-world open-source repos with under 3% false positive rate.

    **Dependencies**: Python AST module for Python analysis, tree-sitter for TypeScript/JavaScript

    **Exports**: Usage documentation, configuration examples, violation messages, filter pipeline reference

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: 9-filter classification pipeline with AST-based chain extraction for Python and tree-sitter for TypeScript/JavaScript

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Try It Now

```bash
pip install thailint
thailint law-of-demeter src/
```

**Example output:**
```
src/service.py:42:8 - Law of Demeter violation: chain depth 3 in 'order.customer.address.city'
```

**Fix it:** Access only your immediate collaborators. Instead of reaching through objects, ask the object you have to do the work for you.

---

## Overview

The Law of Demeter (LoD) linter detects chains of attribute access and method calls where code reaches through intermediary objects to access deeply nested state. This principle, also known as the "principle of least knowledge," states that an object should only talk to its immediate friends.

### Why the Law of Demeter Matters

Violating the Law of Demeter creates problems:

- **Tight coupling**: Code depends on the internal structure of objects it doesn't own
- **Fragile chains**: If any intermediate object changes, all callers break
- **Hard to test**: Deep chains require complex mock setups
- **Hidden dependencies**: The real dependency is buried several layers deep
- **Shotgun surgery**: Structural changes ripple across many files

### The Anti-Pattern

```python
# Violation: reaching through order → customer → address
city = order.customer.address.city
```

### The Solution

```python
# Ask the object you have to do the work
city = order.shipping_city()
```

---

## How It Works

### Chain Extraction

The linter parses source code into an AST and extracts chains of attribute access and method calls. A chain like `order.customer.address.city` is extracted as the parts `["order", "customer", "address", "city"]` with depth 4.

### 9-Filter Classification Pipeline

Each extracted chain is run through a pipeline of 8 filter functions (the 9th filter, test file exclusion, is applied at the linter level). If any filter matches, the chain is classified as a legitimate pattern and not reported. If no filter matches, it is reported as a genuine LoD violation.

| # | Filter | What It Allows | Example |
|---|--------|----------------|---------|
| 1 | Safe prefix | `self.`, `cls.`, `this.`, `os.path.`, `settings.` | `self.db.query()` |
| 2 | Module access | Dotted module imports | `json.dumps()`, `os.path.join()` |
| 3 | String methods | Same-type method chaining | `name.strip().lower()` |
| 4 | Fluent chain | Builder / collection pipeline / ORM | `queryset.filter().order_by().first()` |
| 5 | AST traversal | Data structure navigation (AST, DOM, CST) | `node.body[0].value.attr` |
| 6 | Dunder access | Python protocol attributes | `obj.__class__.__name__` |
| 7 | Subscript access | Dict/list access contributing to depth | `data["key"]["nested"]` |
| 8 | Safe terminal | Common endpoint methods | `obj.attr.get()`, `path.parent.exists()` |
| 9 | Test file | Skip test files (linter level) | `tests/test_foo.py` |

### Language Support

| Language | Parser | Optional Chaining |
|----------|--------|-------------------|
| Python | `ast` (stdlib) | N/A |
| TypeScript | tree-sitter | Excluded (`?.` chains are not violations) |
| JavaScript | tree-sitter | Excluded (`?.` chains are not violations) |

TypeScript's optional chaining (`obj?.prop?.method()`) indicates the developer is already handling the possibility that intermediaries may not exist, so these chains are excluded.

---

## Configuration

### Basic Configuration

```yaml
# .thailint.yaml
law-of-demeter:
  min_chain_depth: 3        # Minimum chain depth to flag (default: 3)
  check_test_files: false   # Skip test files by default
  enabled: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `min_chain_depth` | int | `3` | Minimum chain depth to report as a violation |
| `check_test_files` | bool | `false` | Whether to analyze test files |
| `enabled` | bool | `true` | Enable or disable the linter |
| `safe_prefixes` | list | (built-in set) | Additional safe chain prefixes (merged with defaults) |
| `fluent_methods` | list | (built-in set) | Additional fluent/builder method names (merged with defaults) |
| `exempt_modules` | list | `[]` | Additional module names to treat as module-qualified access |

### Extending Filters

User-provided lists are **merged** with built-in defaults, so you extend coverage rather than replacing it:

```yaml
law-of-demeter:
  min_chain_depth: 3
  safe_prefixes:
    - "ctx."           # Your app's context object
    - "app.services."  # Your service locator
  fluent_methods:
    - "with_retry"     # Your custom builder method
    - "with_timeout"
  exempt_modules:
    - "mycompany"      # Your internal module namespace
```

### JSON Configuration

```json
{
  "law-of-demeter": {
    "min_chain_depth": 3,
    "check_test_files": false,
    "safe_prefixes": ["ctx."],
    "fluent_methods": ["with_retry"]
  }
}
```

---

## Usage

### CLI

```bash
# Check a directory
thailint law-of-demeter src/

# Check with parallel processing
thailint law-of-demeter --parallel src/

# Include test files in analysis
thailint law-of-demeter --check-test-files src/

# Set a higher minimum depth
thailint law-of-demeter --min-depth 4 src/

# JSON output
thailint law-of-demeter --format json src/

# SARIF output (for CI/CD integration)
thailint law-of-demeter --format sarif src/

# Use a specific config file
thailint law-of-demeter --config .thailint.yaml src/
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--format TEXT` | Output format: `text`, `json`, or `sarif` (default: `text`) |
| `--parallel` | Enable multi-core parallel processing |
| `--min-depth N` | Minimum chain depth to flag (overrides config) |
| `--check-test-files` | Include test files in analysis |
| `--config PATH` | Path to configuration file |

### Docker

```bash
docker run -v $(pwd):/workspace thailint law-of-demeter /workspace/src/
```

---

## Violation Examples

### Example 1: Reaching Through Objects

```python
# Violation: depth 3 — reaching through customer to get address
def send_invoice(order):
    city = order.customer.address.city
    send_to(city)
```

**Refactored:**
```python
# Ask order for the shipping city directly
def send_invoice(order):
    city = order.shipping_city()
    send_to(city)
```

### Example 2: Deep Config Access

```python
# Violation: depth 4 — reaching through nested config objects
timeout = app.config.database.connection.timeout
```

**Refactored:**
```python
# Access config at the appropriate level
timeout = app.db_timeout()
```

### Example 3: TypeScript Chain

```typescript
// Violation: depth 3 — reaching through user to get role
const permissions = user.department.manager.permissions;
```

**Refactored:**
```typescript
// Ask user for the relevant permissions
const permissions = user.effectivePermissions();
```

---

## What Is NOT a Violation

The linter's filter pipeline recognizes many legitimate chaining patterns:

### Fluent APIs / Builder Pattern

```python
# Allowed: ORM query builder (fluent chain)
users = User.query.filter(active=True).order_by("name").limit(10)
```

### String Method Chaining

```python
# Allowed: same-type chaining (str → str → str)
clean_name = raw_input.strip().lower().replace("-", "_")
```

### Module-Qualified Access

```python
# Allowed: dotted module path, not object navigation
result = os.path.join(base_dir, filename)
config = logging.getLogger(__name__)
```

### Self/Cls Access

```python
# Allowed: accessing own state is fine
class Service:
    def process(self):
        return self.db.query("SELECT 1")
```

### Optional Chaining (TypeScript)

```typescript
// Allowed: optional chaining shows awareness of nullable intermediaries
const name = user?.profile?.displayName;
```

---

## Ignoring Violations

### Line-Level Ignore

```python
city = order.customer.address.city  # thailint: ignore law-of-demeter
```

### Block Ignore

```python
# thailint: ignore-start law-of-demeter
city = order.customer.address.city
state = order.customer.address.state
# thailint: ignore-end law-of-demeter
```

### File-Level Ignore

```python
# thailint: ignore-file law-of-demeter
```

### Configuration-Based Ignore

```yaml
law-of-demeter:
  ignore:
    - "src/generated/**"
    - "src/legacy/**"
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Check Law of Demeter
  run: thailint law-of-demeter --format sarif --parallel src/ > results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

### Pre-commit Hook

```yaml
- repo: local
  hooks:
    - id: law-of-demeter
      name: Law of Demeter
      entry: thailint law-of-demeter
      language: python
      types: [python]
```

---

## Best Practices

1. **Start with the default depth of 3** — this catches the most impactful violations without being noisy
2. **Don't suppress ORM chains** — the linter already recognizes Django/SQLAlchemy query builders as fluent APIs
3. **Use `safe_prefixes` for your domain** — if your codebase has a `ctx` or `services` namespace, add it to safe prefixes
4. **Fix violations by adding methods**, not by splitting chains into multiple lines — the fix is delegation, not cosmetics
5. **Enable `--parallel` for large codebases** — the linter supports multi-core processing
6. **Use `--check-test-files` sparingly** — test code legitimately reaches into objects for assertions

---

## Resources

- [Law of Demeter (Wikipedia)](https://en.wikipedia.org/wiki/Law_of_Demeter)
- [Tell, Don't Ask (Martin Fowler)](https://martinfowler.com/bliki/TellDontAsk.html)
- [CLI Reference](cli-reference.md)
- [Configuration Guide](configuration.md)
- [How to Ignore Violations](how-to-ignore-violations.md)
