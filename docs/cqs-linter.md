# CQS Linter

??? info "AI Agent Context (click to expand)"
    **Purpose**: Complete guide to using the CQS linter for detecting Command-Query Separation violations

    **Scope**: Configuration, usage, refactoring patterns, and best practices for CQS violation detection

    **Overview**: Comprehensive documentation for the CQS (Command-Query Separation) linter that detects
        functions mixing query operations (capturing return values) with command operations (discarding
        return values as side effects). Covers how the linter works using AST and tree-sitter analysis,
        configuration options, CLI and library usage, ignore directives, and common refactoring patterns.
        Helps teams enforce separation of concerns by identifying functions that both read and write state.

    **Dependencies**: ast module (Python parser), tree-sitter-typescript (TypeScript parser)

    **Exports**: Usage documentation, configuration examples, refactoring patterns

    **Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns

    **Implementation**: AST-based detection for Python, tree-sitter for TypeScript/JavaScript

    *This follows the [AI-Optimized Documentation Standard](ai-doc-standard.md).*

---

## Overview

The **CQS (Command-Query Separation)** linter detects functions that violate the Command-Query Separation principle by mixing **queries** (operations that capture return values) with **commands** (operations that perform side effects without capturing return values).

### Why CQS Matters

The Command-Query Separation principle states that every function should either:

- **Query**: Return a value without side effects, OR
- **Command**: Perform a side effect without returning a value

Functions that mix both are harder to reason about, test, and maintain. AI-generated code frequently violates this principle by combining data fetching with data mutation in a single function.

### What It Detects

**INPUT operations (queries)** — function calls whose return values are captured:

```python
# These are INPUT operations
data = fetch_data()
result = validate(data)
self.cache = load_cache()
x, y = get_coordinates()
```

**OUTPUT operations (commands)** — function calls whose return values are discarded:

```python
# These are OUTPUT operations
save_to_db(result)
log_event("processed")
notify_user(user_id)
```

**A violation occurs** when a single function contains both INPUT and OUTPUT operations:

```python
# VIOLATION: mixes queries and commands
def process_and_save(user_id):
    data = fetch_data(user_id)      # INPUT: captures return value
    result = validate(data)          # INPUT: captures return value
    save_to_db(result)               # OUTPUT: discards return value
    notify_user(user_id)             # OUTPUT: discards return value
```

## Rule IDs

| Rule ID | Description |
|---------|-------------|
| `cqs` | Function mixes query (INPUT) and command (OUTPUT) operations |

## Configuration

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
cqs:
  enabled: true

  # Minimum number of each operation type to trigger a violation
  # Both inputs AND outputs must meet this threshold
  # Default: 1
  min_operations: 1

  # Method names to exclude from analysis
  # Default: ["__init__", "__new__"]
  ignore_methods:
    - "__init__"
    - "__new__"

  # Decorators that exclude functions from analysis
  # Default: ["property", "cached_property"]
  ignore_decorators:
    - "property"
    - "cached_property"

  # File patterns to exclude (glob syntax)
  ignore_patterns: []

  # Ignore functions that return self/this (builder/fluent pattern)
  # Default: true
  detect_fluent_interface: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable CQS linter |
| `min_operations` | integer | `1` | Minimum count of each operation type to trigger violation |
| `ignore_methods` | array | `["__init__", "__new__"]` | Method names excluded from analysis |
| `ignore_decorators` | array | `["property", "cached_property"]` | Decorators that exclude functions |
| `ignore_patterns` | array | `[]` | Glob patterns for files to skip |
| `detect_fluent_interface` | boolean | `true` | Exclude functions returning self/this |

## How It Works

### Detection Flow

```
┌────────────────────────────────────────────────────────┐
│ 1. Parse file into AST (Python) or tree-sitter (TS)   │
├────────────────────────────────────────────────────────┤
│ 2. Extract all functions/methods                       │
├────────────────────────────────────────────────────────┤
│ 3. For each function, analyze body statements:         │
│    - Find INPUT operations (assignments from calls)    │
│    - Find OUTPUT operations (standalone call statements)│
├────────────────────────────────────────────────────────┤
│ 4. Filter out:                                         │
│    - Ignored methods (__init__, __new__)                │
│    - Decorated functions (property, cached_property)    │
│    - Fluent interface patterns (return self/this)       │
│    - Functions below min_operations threshold           │
├────────────────────────────────────────────────────────┤
│ 5. Report violations for functions with both INPUTs     │
│    and OUTPUTs meeting the threshold                    │
└────────────────────────────────────────────────────────┘
```

### Python INPUT Patterns

| Pattern | Example |
|---------|---------|
| Simple assignment | `x = func()` |
| Tuple unpacking | `x, y = func()` |
| Async assignment | `x = await func()` |
| Attribute assignment | `self.x = func()` |
| Subscript assignment | `cache[key] = func()` |
| Annotated assignment | `result: int = func()` |
| Walrus operator | `(x := func())` |

### Python OUTPUT Patterns

| Pattern | Example |
|---------|---------|
| Statement call | `func()` |
| Async statement call | `await func()` |
| Method call | `obj.method()` |
| Chained call | `obj.method().method2()` |

### TypeScript INPUT Patterns

| Pattern | Example |
|---------|---------|
| Variable declaration | `const x = func()` |
| Object destructuring | `const { a, b } = func()` |
| Array destructuring | `const [a, b] = func()` |
| Await assignment | `const x = await func()` |
| Class field assignment | `this.x = func()` |

### TypeScript OUTPUT Patterns

| Pattern | Example |
|---------|---------|
| Statement call | `func();` |
| Async statement call | `await func();` |
| Method call | `obj.method();` |
| Chained call | `obj.method().method2();` |

## Violation Examples

### Example 1: Mixed Query and Command

**Code with violation:**
```python
def process_order(order_id):
    order = fetch_order(order_id)       # INPUT
    validated = validate(order)          # INPUT
    save_order(validated)                # OUTPUT
    send_notification(order_id)          # OUTPUT
```

**Violation message:**
```
src/orders.py:1 - Function 'process_order' violates CQS: mixes queries and commands.
  INPUTs: Line 2: order = fetch_order(); Line 3: validated = validate().
  OUTPUTs: Line 4: save_order(); Line 5: send_notification().
  Suggestion: Split into separate query and command functions.
```

**Refactored code:**
```python
def prepare_order(order_id):
    """Query: fetch and validate order."""
    order = fetch_order(order_id)
    return validate(order)

def execute_order(validated_order, order_id):
    """Command: persist and notify."""
    save_order(validated_order)
    send_notification(order_id)
```

### Example 2: TypeScript Violation

**Code with violation:**
```typescript
async function syncUser(userId: string) {
    const user = await fetchUser(userId);     // INPUT
    const profile = await getProfile(userId);  // INPUT
    await updateCache(user);                   // OUTPUT
    notifyListeners(profile);                  // OUTPUT
}
```

**Refactored code:**
```typescript
async function loadUserData(userId: string) {
    const user = await fetchUser(userId);
    const profile = await getProfile(userId);
    return { user, profile };
}

async function persistUserData(user: User, profile: Profile) {
    await updateCache(user);
    notifyListeners(profile);
}
```

### Example 3: Fluent Interface (Not a Violation)

```python
class QueryBuilder:
    def where(self, condition):
        self.conditions.append(condition)
        return self  # Returns self → fluent interface, not flagged
```

## Refactoring Patterns

### Pattern 1: Split into Query + Command

**Before:**
```python
def process_data(source):
    data = load(source)          # INPUT
    transformed = transform(data) # INPUT
    save(transformed)             # OUTPUT
    log_completion(source)        # OUTPUT
```

**After:**
```python
def prepare_data(source):
    """Query: load and transform."""
    data = load(source)
    return transform(data)

def persist_data(data, source):
    """Command: save and log."""
    save(data)
    log_completion(source)
```

### Pattern 2: Return Results for Caller to Act On

**Before:**
```python
def create_user(name, email):
    user = User(name=name, email=email)  # INPUT
    db.save(user)                         # OUTPUT
    send_welcome_email(user.email)        # OUTPUT
    return user
```

**After:**
```python
def build_user(name, email):
    """Query: create user object."""
    return User(name=name, email=email)

def register_user(user):
    """Command: persist and notify."""
    db.save(user)
    send_welcome_email(user.email)
```

## Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for the complete guide.

**Quick examples:**

```python
# File-level ignore
# thailint: ignore-file[cqs]

# Line-level ignore
def mixed_function():  # thailint: ignore[cqs]
    data = fetch()
    save(data)

# Generic ignore
def mixed_function():  # noqa
    ...
```

## Language Support

### Python Support

**Fully Supported**

- Functions and methods in classes
- Async functions (`async def`)
- All assignment patterns (simple, tuple, walrus, annotated)
- Class context tracking for method naming

### TypeScript/JavaScript Support

**Fully Supported**

- Functions, arrow functions, and class methods
- Async functions
- Variable declarations (const, let)
- Destructuring assignments (object and array)
- Class field assignments (`this.x = func()`)

## Related Documentation

- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library usage
