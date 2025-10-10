# How to Ignore Linter Violations

**Purpose**: Comprehensive guide to ignoring linter violations at all levels for all linters in thai-lint

**Scope**: All linters (file-placement, nesting, SRP, DRY, magic-numbers) and all ignore mechanisms

**Overview**: Complete reference for ignoring linter violations in thai-lint using the 5-level ignore system. Covers line-level, method-level, class-level, file-level, and repository-level ignores with specific examples for every linter. Designed to be AI-agent-friendly with clear patterns and comprehensive examples. Includes best practices, when to use each ignore level, and how to document ignored violations properly.

**Dependencies**: Linter configuration system, inline comment parsing, config file loader

**Exports**: Ignore patterns, syntax examples, and best practices for all linters and all ignore levels

**Related**: configuration.md for config file format, each linter's documentation for linter-specific rules

**Implementation**: 5-level ignore system with inline comments and configuration file patterns

---

## Overview

thai-lint provides a **5-level ignore system** that allows you to suppress violations at different scopes:

1. **Line-level ignores** - Ignore specific violations on specific lines
2. **Method/Function-level ignores** - Ignore violations for entire methods
3. **Class-level ignores** - Ignore violations for entire classes
4. **File-level ignores** - Ignore violations for entire files
5. **Repository-level ignores** - Ignore patterns in configuration file

This guide provides **complete examples for EVERY linter and EVERY ignore level**.

## 5-Level Ignore System Overview

| Level | Scope | Syntax | Use When |
|-------|-------|--------|----------|
| Line | Single line | `# thailint: ignore[rule-name]` | One-off acceptable violation |
| Method | Function/method | `def foo(): # thailint: ignore[rule-name]` | Method has justified complexity |
| Class | Entire class | `class Foo: # thailint: ignore[rule-name]` | Class has justified violations |
| File | Entire file | `# thailint: ignore-file[rule-name]` (first line) | Legacy file or special case |
| Repository | File patterns | `.thailint.yaml` config | Standard project exceptions |

## Line-Level Ignores

Suppress violations on **specific lines only**.

### Syntax

**Python:**
```python
code_here  # thailint: ignore[rule-name]
```

**TypeScript:**
```typescript
code_here  // thailint: ignore[rule-name]
```

### Examples for Each Linter

#### Magic Numbers Linter

**Python:**
```python
# Single violation
timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard timeout

# Multiple violations on same line
dimensions = (1920, 1080)  # thailint: ignore[magic-numbers] - Standard HD resolution

# Inside function
def calculate():
    return 2.54  # thailint: ignore[magic-numbers] - Inches to cm conversion factor
```

**TypeScript:**
```typescript
// Single violation
const timeout = 3600;  // thailint: ignore[magic-numbers] - Industry standard

// Arrow function
const convert = () => 2.54;  // thailint: ignore[magic-numbers] - Conversion factor

// In object
const config = {
  port: 8080  // thailint: ignore[magic-numbers] - Standard HTTP alternate port
};
```

#### Nesting Linter

**Python:**
```python
def legacy_parser():  # thailint: ignore[nesting] - Complex legacy code, scheduled for rewrite
    if data:
        if data.valid:
            for item in data:
                if item.process():  # Deeply nested but justified
                    return True
```

**TypeScript:**
```typescript
// thailint: ignore[nesting] - Complex state machine, refactor in v2.0
function processStateMachine() {
  if (state) {
    if (state.valid) {
      for (const event of events) {
        if (event.handle()) {
          return true;
        }
      }
    }
  }
}
```

#### SRP Linter

**Python:**
```python
class LegacyController:  # thailint: ignore[srp] - Framework adapter, refactoring planned
    def method1(self): pass
    def method2(self): pass
    # ... 10+ methods
```

**TypeScript:**
```typescript
// thailint: ignore[srp] - React component with complex state, breaking up affects UX
class Dashboard extends React.Component {
  // Many methods for different UI sections
}
```

#### DRY Linter

**Python:**
```python
# thailint: ignore[dry] - Similar validation logic but different domains
def validate_user(data):
    if not data:
        return False
    if not data.get('email'):
        return False
    return True
```

**TypeScript:**
```typescript
// thailint: ignore[dry] - Intentional duplication for test readability
test('validates email', () => {
  // Repeated setup code that's clearer when explicit
});
```

#### File Placement Linter

**Python:**
```python
# src/utils/temp_script.py
# thailint: ignore[file-placement] - Temporary utility script, will be moved

def helper():
    pass
```

## Method/Function-Level Ignores

Suppress violations for **entire functions or methods**.

### Syntax

Place ignore comment on the same line as the function definition:

**Python:**
```python
def function_name():  # thailint: ignore[rule-name]
    # entire function body ignored
    pass
```

**TypeScript:**
```typescript
function functionName() {  // thailint: ignore[rule-name]
  // entire function body ignored
}
```

### Examples for Each Linter

#### Magic Numbers Linter

**Python:**
```python
def get_http_codes():  # thailint: ignore[magic-numbers] - HTTP status codes are self-documenting
    return {
        200: "OK",
        404: "Not Found",
        500: "Internal Server Error"
    }
```

**TypeScript:**
```typescript
// thailint: ignore[magic-numbers] - Standard port configurations
function getDefaultPorts() {
  return {
    http: 80,
    https: 443,
    ssh: 22
  };
}
```

#### Nesting Linter

**Python:**
```python
def complex_algorithm():  # thailint: ignore[nesting] - Algorithm requires deep nesting
    for i in range(n):
        for j in range(m):
            for k in range(p):
                if matrix[i][j][k]:
                    # Justified complexity
                    process()
```

**TypeScript:**
```typescript
// thailint: ignore[nesting] - Parser requires nested state checks
function parseExpression() {
  if (token) {
    if (token.valid) {
      while (hasMore) {
        if (match()) {
          return result;
        }
      }
    }
  }
}
```

## Class-Level Ignores

Suppress violations for **entire classes**.

### Syntax

**Python:**
```python
class ClassName:  # thailint: ignore[rule-name]
    # entire class ignored
    pass
```

**TypeScript:**
```typescript
// thailint: ignore[rule-name]
class ClassName {
  // entire class ignored
}
```

### Examples for Each Linter

#### SRP Linter

**Python:**
```python
class FilePlacementRule:  # thailint: ignore[srp] - Framework adapter with multiple config sources
    def validate_config(self): pass
    def check_patterns(self): pass
    def load_rules(self): pass
    def format_violations(self): pass
    # 15 methods - justified for framework integration
```

**TypeScript:**
```typescript
// thailint: ignore[srp] - Redux store manager requires many methods
class StoreManager {
  initStore() {}
  subscribe() {}
  dispatch() {}
  getState() {}
  // Many methods for store management
}
```

#### Magic Numbers Linter

**Python:**
```python
class Constants:  # thailint: ignore[magic-numbers] - Constants definition class
    HTTP_OK = 200
    HTTP_CREATED = 201
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
```

**TypeScript:**
```typescript
// thailint: ignore[magic-numbers] - Configuration constants
class AppConfig {
  static readonly PORT = 8080;
  static readonly MAX_CONNECTIONS = 100;
  static readonly TIMEOUT_MS = 5000;
}
```

## File-Level Ignores

Suppress violations for **entire files**.

### Syntax

Place directive as the **first line** (or after shebang/encoding):

**Python:**
```python
# thailint: ignore-file[rule-name]

# Rest of file content
```

**TypeScript:**
```typescript
// thailint: ignore-file[rule-name]

// Rest of file content
```

### Examples for Each Linter

#### Magic Numbers Linter

**Python:**
```python
# thailint: ignore-file[magic-numbers]
"""Configuration constants file - numbers are self-documenting."""

HTTP_CODES = {
    200: "OK",
    404: "Not Found",
    500: "Server Error"
}

TIMEOUTS = {
    'short': 5,
    'medium': 30,
    'long': 300
}
```

**TypeScript:**
```typescript
// thailint: ignore-file[magic-numbers]
/**
 * System configuration with standard values
 */

export const CONFIG = {
  ports: { http: 80, https: 443 },
  limits: { maxUsers: 1000, maxRequests: 10000 }
};
```

#### Nesting Linter

**Python:**
```python
# thailint: ignore-file[nesting]
"""Legacy module - scheduled for refactoring in Q2."""

def old_parser():
    # Deep nesting acceptable in legacy code
    pass
```

**TypeScript:**
```typescript
// thailint: ignore-file[nesting]
/**
 * Legacy state machine - refactoring in progress
 */

function complexStateMachine() {
  // Deep nesting allowed
}
```

#### SRP Linter

**Python:**
```python
# thailint: ignore-file[srp]
"""
Monolithic controller - framework requires single entry point.
Splitting would break framework integration.
"""

class MainController:
    # Many methods required by framework
    pass
```

#### DRY Linter

**Python:**
```python
# thailint: ignore-file[dry]
"""Test fixtures with intentional duplication for clarity."""

def test_case_1():
    # Repeated setup for test readability
    setup_database()
    create_user()
    # Test logic
```

#### File Placement Linter

**Python:**
```python
# thailint: ignore-file[file-placement]
"""Temporary migration script - will be removed after deployment."""

def migrate_data():
    pass
```

## Repository-Level Ignores (Configuration File)

Suppress violations for **file patterns** across the entire repository.

### Syntax

Add to `.thailint.yaml` or `.thailint.json`:

**YAML:**
```yaml
linter-name:
  ignore:
    - "pattern/to/ignore"
    - "another/pattern/**"
```

**JSON:**
```json
{
  "linter-name": {
    "ignore": [
      "pattern/to/ignore",
      "another/pattern/**"
    ]
  }
}
```

### Examples for Each Linter

#### Magic Numbers Linter

**YAML:**
```yaml
magic-numbers:
  enabled: true
  ignore:
    - "tests/**"              # Test files can have magic numbers
    - "**/*_constants.py"     # Constants files
    - "config/*.py"           # Configuration files
    - "migrations/*.py"       # Database migrations
```

**JSON:**
```json
{
  "magic-numbers": {
    "enabled": true,
    "ignore": [
      "tests/**",
      "**/*_constants.py",
      "config/*.py",
      "migrations/*.py"
    ]
  }
}
```

#### Nesting Linter

**YAML:**
```yaml
nesting:
  enabled: true
  max_nesting_depth: 3
  ignore:
    - "legacy/**"             # Legacy code module
    - "vendor/**"             # Third-party code
    - "generated/**"          # Auto-generated code
```

**JSON:**
```json
{
  "nesting": {
    "enabled": true,
    "max_nesting_depth": 3,
    "ignore": [
      "legacy/**",
      "vendor/**",
      "generated/**"
    ]
  }
}
```

#### SRP Linter

**YAML:**
```yaml
srp:
  enabled: true
  max_methods: 8
  ignore:
    - "**/*Controller.py"     # Controllers are complex by nature
    - "**/*Manager.py"        # Manager pattern requires many methods
    - "adapters/**"           # Framework adapters
```

**JSON:**
```json
{
  "srp": {
    "enabled": true,
    "max_methods": 8,
    "ignore": [
      "**/*Controller.py",
      "**/*Manager.py",
      "adapters/**"
    ]
  }
}
```

#### DRY Linter

**YAML:**
```yaml
dry:
  enabled: true
  min_duplicate_lines: 4
  ignore:
    - "tests/**"              # Test code can be repetitive
    - "examples/**"           # Examples intentionally show patterns
    - "migrations/**"         # Migrations often have similar structure
    - "fixtures/**"           # Test fixtures
```

**JSON:**
```json
{
  "dry": {
    "enabled": true,
    "min_duplicate_lines": 4,
    "ignore": [
      "tests/**",
      "examples/**",
      "migrations/**",
      "fixtures/**"
    ]
  }
}
```

#### File Placement Linter

**YAML:**
```yaml
file-placement:
  ignore:
    - "__pycache__/"
    - "*.pyc"
    - ".venv/"
    - "node_modules/"
    - "dist/"
    - "build/"
    - ".git/"
```

**JSON:**
```json
{
  "file-placement": {
    "ignore": [
      "__pycache__/",
      "*.pyc",
      ".venv/",
      "node_modules/",
      "dist/",
      "build/",
      ".git/"
    ]
  }
}
```

## Multiple Rules on Same Line

You can ignore multiple rules on the same line:

**Python:**
```python
def complex_function():  # thailint: ignore[nesting,srp]
    # Ignore both nesting and SRP violations
    pass

value = 3600  # thailint: ignore[magic-numbers,dry]
```

**TypeScript:**
```typescript
// thailint: ignore[nesting,magic-numbers]
function legacyCode() {
  if (depth > 5) {  // Deep nesting + magic number
    return 42;
  }
}
```

## Generic Ignore (All Rules)

Ignore **all rules** on a line (use sparingly):

**Python:**
```python
legacy_code()  # thailint: ignore
```

**TypeScript:**
```typescript
legacyFunction();  // thailint: ignore
```

**File-level:**
```python
# thailint: ignore-file

# All linters ignore this entire file
```

## Best Practices

### When to Use Each Level

| Level | Use When | Example |
|-------|----------|---------|
| **Line** | One-off acceptable violation | Industry standard constant |
| **Method** | Function has justified complexity | Algorithm requires deep nesting |
| **Class** | Class design justifies violations | Framework adapter |
| **File** | Legacy code or special file | Migration script, constants file |
| **Repository** | Project-wide patterns | All test files, generated code |

### Documentation Requirements

**Always document WHY you're ignoring:**

**Good:**
```python
timeout = 3600  # thailint: ignore[magic-numbers] - Industry standard HTTP timeout
```

**Bad:**
```python
timeout = 3600  # thailint: ignore[magic-numbers]
```

**Very Good:**
```python
class DatabaseAdapter:  # thailint: ignore[srp] - ORM framework requires single adapter class
    # Detailed explanation in class docstring
    """
    Framework adapter for SQLAlchemy ORM.

    Must handle connection, session, query building, and migrations
    in single class per framework requirements. Splitting would break
    ORM transaction management.
    """
```

### Avoid Over-Ignoring

**Prefer fixing over ignoring:**

1. **First**: Try to refactor to fix the violation
2. **Second**: If refactoring is not feasible, document why
3. **Third**: Choose the narrowest ignore scope possible

**Example - Prefer narrow scope:**

```python
# Bad - ignores entire file unnecessarily
# thailint: ignore-file[magic-numbers]

def function1():
    return 42  # Only this needs ignoring

def function2():
    return "hello"  # No magic numbers here

# Good - ignore only where needed
def function1():
    return 42  # thailint: ignore[magic-numbers] - Ultimate answer

def function2():
    return "hello"
```

### Review Ignores Regularly

Add comments with dates when planning to fix:

```python
# thailint: ignore[nesting] - TODO: Refactor by 2025-Q2
def legacy_function():
    pass
```

## Ignore Patterns (Repository-Level)

### Glob Pattern Syntax

Repository-level ignores support glob patterns:

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | Any characters in filename | `*.py` matches all Python files |
| `**` | Any directories | `tests/**` matches all files under tests/ |
| `?` | Single character | `test?.py` matches `test1.py`, `testA.py` |
| `[abc]` | Character set | `file[123].py` matches `file1.py`, `file2.py` |

### Common Patterns

```yaml
ignore:
  # All files in directory
  - "legacy/"
  - "vendor/"

  # Files by extension
  - "*.generated.py"
  - "*.min.js"

  # Recursive patterns
  - "**/__pycache__/"
  - "**/node_modules/"

  # Specific file patterns
  - "**/*_constants.py"
  - "**/*Controller.py"

  # Single files
  - "src/legacy_module.py"
  - "config/old_settings.json"
```

## Troubleshooting

### Ignore Not Working

**Problem**: Violation still reported despite ignore directive

**Solutions**:

1. **Check syntax** - Ensure correct rule name:
   ```python
   # Wrong
   x = 42  # thailint: ignore magic-numbers

   # Correct
   x = 42  # thailint: ignore[magic-numbers]
   ```

2. **Check spelling** - Rule names are case-sensitive:
   ```python
   # Wrong
   x = 42  # thailint: ignore[Magic-Numbers]

   # Correct
   x = 42  # thailint: ignore[magic-numbers]
   ```

3. **Check placement** - Comment must be on same line:
   ```python
   # Wrong
   # thailint: ignore[magic-numbers]
   x = 42

   # Correct
   x = 42  # thailint: ignore[magic-numbers]
   ```

4. **Check file-level placement** - Must be first line (after shebang):
   ```python
   # Wrong
   """Module docstring."""
   # thailint: ignore-file[magic-numbers]

   # Correct
   # thailint: ignore-file[magic-numbers]
   """Module docstring."""
   ```

5. **Check config file syntax** - YAML indentation matters:
   ```yaml
   # Wrong
   magic-numbers:
   ignore:
     - "tests/**"

   # Correct
   magic-numbers:
     ignore:
       - "tests/**"
   ```

### Finding the Right Rule Name

Run the linter to see the rule ID in violation messages:

```bash
$ thailint magic-numbers src/

src/example.py:10 - Magic number 3600 should be a named constant
  Rule: magic-numbers  ← Use this in ignore directive
```

All rule names:
- `magic-numbers` - Magic Numbers Linter
- `nesting` - Nesting Depth Linter
- `srp` - Single Responsibility Principle Linter
- `dry` - Don't Repeat Yourself Linter
- `file-placement` - File Placement Linter

## Complete Examples

### Python Module with Mixed Ignores

```python
# thailint: ignore-file[dry]
"""
Test fixtures module with intentional duplication.

Test fixtures repeat similar patterns for clarity and test isolation.
DRY violations are acceptable here.
"""

# Repository config ignores tests/** for magic-numbers

class TestConstants:  # thailint: ignore[srp] - Test data aggregator
    HTTP_OK = 200  # Magic numbers OK in constants class
    HTTP_CREATED = 201
    HTTP_ERROR = 500

    def setup_database(self):  # thailint: ignore[nesting] - Complex test setup
        if self.db:
            if self.db.connected:
                for table in tables:
                    if table.exists():
                        table.clear()

    timeout = 3600  # thailint: ignore[magic-numbers] - Standard test timeout
```

### TypeScript Component with Ignores

```typescript
// thailint: ignore-file[magic-numbers]
/**
 * Configuration component with standard port values.
 *
 * Port numbers are industry standard and self-documenting,
 * so magic number warnings are disabled for this file.
 */

// thailint: ignore[srp] - Config UI requires many form handlers
class ConfigPanel extends React.Component {
  // Many methods for different config sections

  validatePort() {  // thailint: ignore[nesting] - Port validation is complex
    if (port) {
      if (port > 0) {
        if (port < 65535) {
          if (!this.isReserved(port)) {
            return true;
          }
        }
      }
    }
    return false;
  }
}
```

## Related Documentation

- **[Configuration Reference](configuration.md)** - Config file format and options
- **[Magic Numbers Linter](magic-numbers-linter.md)** - Magic numbers documentation
- **[Nesting Linter](nesting-linter.md)** - Nesting depth documentation
- **[SRP Linter](srp-linter.md)** - Single Responsibility documentation
- **[DRY Linter](dry-linter.md)** - Duplicate code documentation
- **[File Placement Linter](file-placement-linter.md)** - File placement documentation

## Summary

thai-lint provides **5 levels of ignore** for maximum flexibility:

1. **Line-level** - `# thailint: ignore[rule-name]` - Most specific
2. **Method-level** - On function definition line
3. **Class-level** - On class definition line
4. **File-level** - `# thailint: ignore-file[rule-name]` - First line
5. **Repository-level** - `.thailint.yaml` ignore patterns - Most general

**Always prefer**:
1. Fixing the violation through refactoring
2. Narrowest possible ignore scope
3. Clear documentation of WHY you're ignoring

This ensures code quality while allowing justified exceptions.
