# Method Property Linter

**Purpose**: Complete guide to using the method-property linter for detecting methods that should be @property decorators

**Scope**: Configuration, usage, refactoring patterns, and best practices for Pythonic property usage

**Overview**: Comprehensive documentation for the method-property linter that detects Python methods that should be converted to @property decorators. Covers detection patterns, exclusion rules, configuration options, CLI usage, and refactoring guidance. Follows PEP 8 conventions that prefer properties over getter/setter methods for simple attribute access.

**Dependencies**: ast module (Python parser)

**Exports**: Usage documentation, configuration examples, refactoring patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

**Implementation**: AST-based detection with comprehensive exclusion rules to minimize false positives

---

## Try It Now

```bash
pip install thai-lint
thailint method-property src/
```

**Example output:**
```
src/models.py:45 - Method 'get_full_name' should be a @property
  Suggestion: Replace 'def get_full_name(self):' with '@property def full_name(self):'
```

**Fix it:** Convert getter methods to `@property` decorators for cleaner attribute access.

---

## Overview

The method-property linter detects Python methods that should be converted to `@property` decorators. It follows the Pythonic principle that simple attribute access should use properties rather than getter methods.

### What Are Property Candidates?

Methods that should be properties typically:
- Take only `self` as a parameter
- Return an attribute or simple computed value
- Have no side effects
- Have a short body (1-3 statements)

```python
# Bad - Java-style getter methods
class User:
    def __init__(self, name):
        self._name = name

    def get_name(self):  # Should be a property
        return self._name

    def full_name(self):  # Should be a property
        return f"{self._first} {self._last}"

# Good - Pythonic properties
class User:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def full_name(self):
        return f"{self._first} {self._last}"
```

### Why Use Properties?

Properties are preferred over getter methods because:
- **More Pythonic**: Following PEP 8 conventions
- **Cleaner API**: `user.name` vs `user.get_name()`
- **Encapsulation**: Implementation can change without API changes
- **Consistency**: Uniform attribute access style
- **IDE support**: Better autocomplete and type inference

### Best Practices (PEP 8)

According to PEP 8:
> Use properties when you need functional behavior around simple attribute access

Properties are ideal for:
- Simple attribute returns
- Computed values without side effects
- Lazy initialization patterns
- Validation on access

## How It Works

### AST-Based Detection

The linter uses Python's Abstract Syntax Tree (AST) to analyze methods:

1. **Parse source code** into AST
2. **Find class methods** without decorators
3. **Check method signature**: Takes only `self`
4. **Analyze body**: Simple, returns a value, no side effects
5. **Report candidates** for conversion

### Detection Patterns

The linter flags methods that:

| Pattern | Example | Suggestion |
|---------|---------|------------|
| Simple attribute return | `def name(self): return self._name` | `@property name` |
| get_* prefix | `def get_name(self): return self._name` | `@property name` |
| Computed value | `def area(self): return self._w * self._h` | `@property area` |
| Boolean expression | `def is_valid(self): return self._x > 0` | `@property is_valid` |
| String formatting | `def full_name(self): return f"{self._first} {self._last}"` | `@property full_name` |

### Exclusion Rules

The linter **does not** flag methods that:

| Exclusion | Example | Why Excluded |
|-----------|---------|--------------|
| Have parameters | `def get_item(self, i)` | Properties can't have parameters |
| Have side effects | `def value(self): self._cached = True; return self._x` | Properties should be pure |
| Have decorators | `@staticmethod`, `@classmethod`, `@abstractmethod` | Already decorated |
| Have control flow | `if/for/while/try` | Too complex for property |
| Call external functions | `def value(self): return fetch(self._id)` | May have side effects |
| Are dunder methods | `def __str__(self)` | Protocol methods |
| Are action verbs | `def to_dict(self)`, `def finalize(self)` | Transformation/lifecycle methods |
| Are in test files | `test_*.py`, `*_test.py` | Test flexibility |

## Configuration

### Basic Configuration

Create `.thailint.yaml`:

```yaml
method-property:
  enabled: true
  max_body_statements: 3  # Max statements in method body
  ignore:                  # File patterns to ignore
    - "tests/"
    - "*_test.py"
  ignore_methods:          # Method names to ignore
    - "_get_css_styles"
    - "_get_default_standards"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable linter |
| `max_body_statements` | integer | `3` | Maximum statements in method body |
| `ignore` | array | `[]` | File patterns to exclude |
| `ignore_methods` | array | `[]` | Method names to exclude |
| `exclude_prefixes` | array | `[]` | Additional action verb prefixes to exclude (extends defaults) |
| `exclude_names` | array | `[]` | Additional action verb names to exclude (extends defaults) |
| `exclude_prefixes_override` | array | - | Replace default prefixes entirely |
| `exclude_names_override` | array | - | Replace default names entirely |

### Default Exclusions

The linter ships with sensible defaults for action verb exclusions:

**Default Prefixes** (methods starting with these are excluded):
- `to_*`, `dump_*`, `generate_*`, `create_*`, `build_*`, `make_*`, `render_*`, `compute_*`, `calculate_*`

**Default Names** (exact method names excluded):
- `finalize`, `serialize`, `dump`, `validate`, `show`, `display`, `print`, `refresh`, `reset`, `clear`, `close`, `open`, `save`, `load`, `execute`, `run`

### Extending Exclusions

Add your own exclusions while keeping defaults:

```yaml
method-property:
  exclude_prefixes:
    - "fetch_"
    - "format_"
  exclude_names:
    - "export"
    - "import"
```

### Overriding Exclusions

Replace defaults entirely (use with caution):

```yaml
method-property:
  exclude_prefixes_override:
    - "to_"
    - "generate_"
  exclude_names_override:
    - "finalize"
```

### JSON Configuration

```json
{
  "method-property": {
    "enabled": true,
    "max_body_statements": 3,
    "ignore": ["tests/", "*_test.py"],
    "ignore_methods": ["_get_css_styles", "_get_default_standards"]
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete guide.

**Quick examples:**

```python
# Line-level ignore
def get_config(self):  # thailint: ignore[method-property] - API compatibility
    return self._config

# Method-level ignore (on def line)
def serialize(self):  # thailint: ignore[method-property] - Action method
    return self._data

# File-level ignore
# thailint: ignore-file[method-property]
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory
thailint method-property .

# Check specific directory
thailint method-property src/

# Check specific file
thailint method-property src/models.py
```

#### With Configuration

```bash
# Use config file
thailint method-property --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint method-property src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint method-property src/

# JSON output for CI/CD
thailint method-property --format json src/

# SARIF output for GitHub Actions
thailint method-property --format sarif src/ > report.sarif
```

### Library Mode

```python
from src.linters.method_property import lint

# Lint specific path
violations = lint('src/models.py', open('src/models.py').read())

# With custom configuration
violations = lint(
    'src/models.py',
    content,
    config={'max_body_statements': 5}
)

# Process results
for violation in violations:
    print(f"Line {violation.line}: {violation.message}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest method-property /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest method-property \
  --config /config/.thailint.yaml /workspace/src/
```

## Violation Examples

### Example 1: get_* Methods

**Code with violations:**
```python
class User:
    def __init__(self, name, email):
        self._name = name
        self._email = email

    def get_name(self):  # Violation
        return self._name

    def get_email(self):  # Violation
        return self._email
```

**Violation messages:**
```
src/models.py:7 - Method 'get_name' in class 'User' should be a @property named 'name'
src/models.py:10 - Method 'get_email' in class 'User' should be a @property named 'email'
```

**Refactored code:**
```python
class User:
    def __init__(self, name, email):
        self._name = name
        self._email = email

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email
```

### Example 2: Computed Values

**Code with violations:**
```python
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def area(self):  # Violation
        return self._width * self._height

    def perimeter(self):  # Violation
        return 2 * (self._width + self._height)
```

**Refactored code:**
```python
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def area(self):
        return self._width * self._height

    @property
    def perimeter(self):
        return 2 * (self._width + self._height)
```

### Example 3: Acceptable Methods (No Violations)

```python
class DataProcessor:
    # Method with parameters - OK
    def get_item(self, index):
        return self._items[index]

    # Method with side effects - OK
    def fetch_data(self):
        self._last_fetch = time.time()
        return self._data

    # Decorated method - OK
    @staticmethod
    def get_default():
        return 42

    # Action verb method - OK
    def to_dict(self):
        return {"name": self._name}

    # Complex control flow - OK
    def safe_value(self):
        try:
            return self._value
        except KeyError:
            return None
```

## Refactoring Patterns

### Pattern 1: Simple Attribute Return

**Before:**
```python
def name(self):
    return self._name
```

**After:**
```python
@property
def name(self):
    return self._name
```

### Pattern 2: get_* to Property

**Before:**
```python
def get_status(self):
    return self._status
```

**After:**
```python
@property
def status(self):  # Drop the get_ prefix
    return self._status
```

### Pattern 3: Computed Value

**Before:**
```python
def full_name(self):
    return f"{self._first_name} {self._last_name}"
```

**After:**
```python
@property
def full_name(self):
    return f"{self._first_name} {self._last_name}"
```

### Pattern 4: Boolean Property

**Before:**
```python
def is_valid(self):
    return self._value is not None and self._value > 0
```

**After:**
```python
@property
def is_valid(self):
    return self._value is not None and self._value > 0
```

### Pattern 5: With Setter

When you need write access, add a setter:

**Before:**
```python
def get_name(self):
    return self._name

def set_name(self, value):
    self._name = value
```

**After:**
```python
@property
def name(self):
    return self._name

@name.setter
def name(self, value):
    self._name = value
```

## Language Support

### Python Support

**Fully Supported**

The linter analyzes Python files using the built-in `ast` module.

**Detection patterns:**
- Simple attribute returns: `return self._name`
- Computed values: `return self._a + self._b`
- Method chains: `return self._config.get_value()`
- get_* prefixed methods

**Exclusions:**
- Methods with parameters beyond `self`
- Methods with side effects
- Decorated methods
- Dunder methods (`__str__`, `__repr__`)
- Action verb methods (`to_*`, `finalize`, `serialize`, `validate`)
- Test files

### TypeScript Support

**Not Supported**

TypeScript uses different conventions (getter syntax) and is not analyzed by this linter.

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  method-property-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check method properties
        run: |
          thailint method-property src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: method-property-check
        name: Check method properties
        entry: thailint method-property
        language: python
        types: [python]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-method-property:
	@echo "=== Checking method properties ==="
	@poetry run thailint method-property src/ || exit 1

lint-all: lint-method-property
	@echo "All checks passed"
```

## Troubleshooting

### Common Issues

**Issue: Method with parameter flagged**

This shouldn't happen - the linter excludes methods with parameters. If you see this, please report a bug.

**Issue: Method with side effects flagged**

```python
# Problem - side effect not detected
def cached_value(self):
    self._cached = True  # Side effect
    return self._value
```

The linter should detect assignments to `self.*` as side effects. If not detected, check that the assignment is direct (not through a method call).

**Issue: Test file flagged**

```bash
# Problem - file doesn't match test pattern
utils/helpers.py  # Not recognized as test file

# Solution 1: Rename to match pattern
tests/test_helpers.py  # Recognized

# Solution 2: Add to ignore patterns
# .thailint.yaml
method-property:
  ignore:
    - "utils/helpers.py"
```

## Best Practices

### 1. Use Properties for Simple Access

```python
# Good - property for simple access
@property
def name(self):
    return self._name

# Good - property for computed value
@property
def full_name(self):
    return f"{self._first} {self._last}"
```

### 2. Keep Properties Simple

```python
# Bad - too complex for property
@property
def data(self):
    if self._cache:
        return self._cache
    data = fetch_from_api(self._id)
    self._cache = data  # Side effect!
    return data

# Good - use method for complex logic
def get_data(self):
    """Fetch data from API with caching."""
    if self._cache:
        return self._cache
    data = fetch_from_api(self._id)
    self._cache = data
    return data
```

### 3. Don't Raise Exceptions in Properties

```python
# Bad - exceptions in property
@property
def value(self):
    if self._value is None:
        raise ValueError("Value not set")
    return self._value

# Good - return sensible default or use method
@property
def value(self):
    return self._value  # Returns None if not set

def get_value_or_raise(self):
    """Get value, raising if not set."""
    if self._value is None:
        raise ValueError("Value not set")
    return self._value
```

### 4. Use Descriptive Names

```python
# Good - clear property names
@property
def is_active(self):  # Boolean property
    return self._status == "active"

@property
def total_cost(self):  # Computed value
    return self._price * self._quantity
```

## When to Keep Methods

Keep methods (don't convert to properties) when:

1. **Method takes parameters**
   ```python
   def get_item(self, index):  # Keep as method
       return self._items[index]
   ```

2. **Method has side effects**
   ```python
   def next_value(self):  # Keep as method
       self._index += 1
       return self._values[self._index]
   ```

3. **Method is expensive**
   ```python
   def calculate_total(self):  # Keep as method - expensive
       return sum(item.price for item in self._items)
   ```

4. **Method is an action**
   ```python
   def to_dict(self):  # Keep as method - transformation
       return {"name": self._name, "value": self._value}
   ```

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation

## Version History

- **v0.7.0**: Method-property linter release
  - Python support with AST-based detection
  - Comprehensive exclusion rules
  - Action verb method detection (`to_*`, `finalize`, etc.)
  - 111 tests passing
  - Self-dogfooded on thai-lint codebase (0 violations after fixes)
