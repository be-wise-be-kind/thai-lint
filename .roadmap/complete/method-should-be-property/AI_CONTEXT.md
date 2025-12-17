# Method Should Be Property Linter - AI Context

**Purpose**: AI agent context document for implementing Method Should Be Property Linter

**Scope**: Detection of Python methods that should be converted to @property decorators, following Pythonic conventions

**Overview**: Comprehensive context document for AI agents working on the Method Should Be Property Linter feature.
    This linter identifies methods that violate Pythonic conventions by using explicit getter methods instead of
    the @property decorator. Uses AST analysis to detect simple accessor methods, get_* prefixed methods,
    and simple computed values that would be better expressed as properties.

**Dependencies**: Python AST module, MultiLanguageLintRule base class, pytest for testing

**Exports**: Feature architecture, detection patterns, exclusion rules, integration guidance

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: AST-based pattern detection with comprehensive exclusion rules to minimize false positives

---

## Overview

The Method Should Be Property Linter detects Python methods that should be converted to `@property` decorators. This fills a gap in the linting ecosystem - no major linter (Pylint, Ruff, SonarQube) implements this check despite it being a well-known Python best practice.

## Project Background

### The Problem
Python developers coming from Java or other languages often write explicit getter/setter methods:

```python
# Java-style (anti-pattern in Python)
class User:
    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value
```

This violates PEP 8 and Pythonic conventions. Python provides the `@property` decorator for this purpose:

```python
# Pythonic approach
class User:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
```

### Research Findings

| Source | Key Guidance |
|--------|-------------|
| [PEP 8](https://peps.python.org/pep-0008/) | "For simple public data attributes, it is best to expose just the attribute name. Use properties to hide functional implementation behind simple data attribute access syntax." |
| [Pylint #7172](https://github.com/pylint-dev/pylint/issues/7172) | Feature request exists but is marked "Needs PR" - not implemented |
| [python-course.eu](https://python-course.eu/oop/properties-vs-getters-and-setters.php) | "The Pythonic way to introduce attributes is to make them public. Properties use the @property decorator." |

## Feature Vision

1. **Detect Java-style getters**: Flag `get_*()` methods that should be properties
2. **Detect simple accessors**: Flag methods that only return `self._attribute`
3. **Detect simple computed values**: Flag methods with simple arithmetic/string operations
4. **Minimize false positives**: Comprehensive exclusion rules for legitimate methods
5. **Provide actionable suggestions**: Tell users exactly how to convert

## Detection Patterns

### Pattern 1: Simple Attribute Return
Methods that return only a single attribute.

```python
# DETECT - should be @property
def name(self):
    return self._name

def value(self):
    return self.value

def config(self):
    return self._settings.config
```

### Pattern 2: get_* Prefix (Java-Style)
Methods with `get_` prefix - explicit Java-style getters.

```python
# DETECT - Java-style anti-pattern
def get_name(self):
    return self._name

def get_total(self):
    return self._count * self._price
```

### Pattern 3: Simple Computation
Methods with simple arithmetic or string operations on self attributes.

```python
# DETECT - simple computed properties
def area(self):
    return self._width * self._height

def full_name(self):
    return f"{self._first} {self._last}"

def is_valid(self):
    return self._value > 0 and self._value < 100

def display_name(self):
    return self._name.upper()
```

### Pattern 4: Chained Attribute Access
Methods returning nested attribute access.

```python
# DETECT - delegation pattern
def database(self):
    return self._connection.database

def settings(self):
    return self._config.settings.general
```

## Exclusion Rules

### Rule 1: Methods with Parameters
Properties cannot accept arguments. Any method with parameters beyond `self` is excluded.

```python
# EXCLUDE - has parameters
def get_item(self, index):
    return self._items[index]

def value_with_default(self, default=None):
    return self._value or default
```

### Rule 2: Methods with Assignments (Side Effects)
Methods that modify state should not be properties.

```python
# EXCLUDE - modifies state
def cached_value(self):
    self._cached = True  # Assignment!
    return self._value

def increment_and_get(self):
    self._count += 1  # Augmented assignment!
    return self._count
```

### Rule 3: Methods with Loops
Loops indicate iteration, which is typically not property-like.

```python
# EXCLUDE - contains loop
def items(self):
    for item in self._data:
        yield item

def filtered_values(self):
    result = []
    for v in self._values:
        if v > 0:
            result.append(v)
    return result
```

### Rule 4: Methods with try/except
Error handling indicates complexity beyond property access.

```python
# EXCLUDE - error handling
def safe_value(self):
    try:
        return self._value
    except AttributeError:
        return None
```

### Rule 5: Methods with External Function Calls
Calling external functions may have side effects.

```python
# EXCLUDE - external function call
def formatted_date(self):
    return format_date(self._date)  # External function!

def validated_value(self):
    validate(self._value)  # External function!
    return self._value
```

**Exception**: Calls to `self.*` methods are allowed if they are also simple accessors.

### Rule 6: Decorated Methods
Certain decorators indicate the method has special behavior.

```python
# EXCLUDE - decorated
@staticmethod
def create_default():
    return MyClass()

@classmethod
def from_dict(cls, data):
    return cls(**data)

@abstractmethod
def compute(self):
    pass

@property  # Already a property!
def name(self):
    return self._name

@functools.cached_property
def expensive_value(self):
    return compute_expensive()
```

### Rule 7: Complex Method Bodies
Methods with more than 3 statements are too complex for properties.

```python
# EXCLUDE - too many statements
def processed_value(self):
    value = self._raw_value
    value = value.strip()
    value = value.lower()
    value = value.replace("-", "_")
    return value
```

### Rule 8: Dunder Methods
Special methods like `__str__`, `__repr__` should not be flagged.

```python
# EXCLUDE - dunder method
def __str__(self):
    return self._name

def __repr__(self):
    return f"MyClass({self._value})"
```

### Rule 9: Test Files
Methods in test files are not production code.

```python
# EXCLUDE - in test_*.py or *_test.py files
def get_mock_value(self):
    return self._mock_data
```

### Rule 10: Methods Returning None
Methods with no return or returning None are not accessors.

```python
# EXCLUDE - no return value
def initialize(self):
    pass

def log_value(self):
    print(self._value)
    return None
```

### Rule 11: Async Methods
Methods with `await` perform I/O and should not be properties.

```python
# EXCLUDE - async/await
async def data(self):
    return await self._fetch_data()
```

## AST Analysis Strategy

### Method Detection Flow

```
1. Parse Python file into AST
2. Walk AST to find all class definitions
3. For each class, iterate over methods (FunctionDef nodes)
4. For each method, check:
   a. Takes only 'self' parameter? (check args)
   b. Has simple body? (1-3 statements, ends with Return)
   c. Returns a value? (not None, not missing)
   d. No side effects? (no Assign, AugAssign, For, While, Try, Await)
   e. No excluded decorators? (staticmethod, classmethod, abstractmethod, property)
   f. Not a dunder method? (not __*__)
5. If all checks pass, flag as violation
```

### AST Node Types to Check

| Node Type | Check For |
|-----------|-----------|
| `ast.FunctionDef` | Method definitions |
| `ast.arguments` | Parameter count (should be 1 - self only) |
| `ast.Return` | Return statement (body should end with this) |
| `ast.Assign` | State modification (exclude) |
| `ast.AugAssign` | Augmented assignment (exclude) |
| `ast.For` | Loop (exclude) |
| `ast.While` | Loop (exclude) |
| `ast.Try` | Error handling (exclude) |
| `ast.Call` | Function calls (check if external) |
| `ast.Await` | Async operation (exclude) |
| `ast.Attribute` | self.* access (allowed) |

### Violation Classification

Based on detection pattern, generate appropriate message:

| Pattern | Message Template |
|---------|-----------------|
| `get_*` prefix | "Method 'get_name()' should be a @property 'name' - Java-style getter detected" |
| Simple return | "Method 'value()' should be a @property - returns only 'self._value'" |
| Computed value | "Method 'area()' should be a @property - simple stateless computation" |

## Integration Points

### With Existing Code

| Component | Integration |
|-----------|-------------|
| `src/core/base.py` | Inherit from `MultiLanguageLintRule` |
| `src/core/types.py` | Use `Violation` dataclass |
| `src/cli.py` | Register `method-property` command |
| `src/orchestrator/` | Auto-discovered via RuleRegistry |

### Pattern Reference

Follow the structure of `src/linters/print_statements/`:

```
print_statements/
├── __init__.py          → Package exports
├── config.py            → Configuration dataclass
├── linter.py            → Main rule class
├── python_analyzer.py   → AST analysis
├── typescript_analyzer.py (not needed for this linter)
└── violation_builder.py → Violation message creation
```

## Technical Constraints

1. **Python Only**: This linter targets Python code. TypeScript has different conventions.
2. **AST Limitation**: Can only analyze syntactically valid Python files.
3. **No Runtime Analysis**: Cannot detect runtime side effects (only static analysis).
4. **Performance**: Keep analysis fast - avoid expensive operations.

## AI Agent Guidance

### When Implementing Detection

1. Start with the most common pattern (get_* prefix)
2. Build exclusion rules incrementally with tests
3. Prefer false negatives over false positives
4. Each exclusion rule should have tests

### When Writing Tests

1. Write tests FIRST (TDD red phase)
2. Each detection pattern needs positive and negative tests
3. Each exclusion rule needs tests proving it works
4. Include edge cases (empty files, syntax errors, Unicode)

### Common Patterns

**Creating a Violation**:
```python
violation = Violation(
    rule_id="method-property.should-be-property",
    file_path=str(context.file_path),
    line=method.lineno,
    column=method.col_offset,
    message=f"Method '{method.name}()' should be a @property",
    suggestion="Convert to @property decorator for Pythonic attribute access"
)
```

**Checking for Side Effects**:
```python
def _has_side_effects(self, method: ast.FunctionDef) -> bool:
    """Check for assignments, loops, try/except, external calls, await."""
    for node in ast.walk(method):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            return True
        if isinstance(node, (ast.For, ast.While)):
            return True
        if isinstance(node, ast.Try):
            return True
        if isinstance(node, ast.Await):
            return True
        if isinstance(node, ast.Call) and not self._is_self_call(node):
            return True
    return False
```

## Risk Mitigation

### False Positive Risks

| Risk | Mitigation |
|------|------------|
| Methods with legitimate reasons to not be properties | Comprehensive exclusion rules |
| Performance-critical code | Exclude methods calling external functions |
| Framework integration | Test with real-world codebases (dogfooding) |

### Implementation Risks

| Risk | Mitigation |
|------|------------|
| Complex AST analysis | Follow existing linter patterns |
| Missing edge cases | Comprehensive test suite (40+ tests) |
| Performance issues | Keep analysis simple, avoid recursion |

## Future Enhancements

1. **set_* Detection**: Detect `set_*` methods that should use `@property.setter`
2. **TypeScript Support**: Extend to TypeScript getter/setter patterns
3. **Auto-fix**: Provide automatic code transformation
4. **IDE Integration**: VS Code extension for real-time feedback

## Rule Configuration

### Default Configuration
```yaml
method-property:
  enabled: true
  max_body_statements: 3
  ignore:
    - "tests/*"
    - "**/test_*.py"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | true | Enable/disable the linter |
| `max_body_statements` | int | 3 | Maximum statements in method body |
| `ignore` | list[str] | [] | Glob patterns for files to skip |
