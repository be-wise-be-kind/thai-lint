# How to: Fix Linting Errors

**Purpose**: Step-by-step guide for fixing basic linting violations (code style, security, types)

**Scope**: Ruff, Flake8, Pylint, MyPy, Bandit, pip-audit - mechanical fixes before architectural refactoring

**Overview**: This guide covers systematic fixing of objective linting violations - code style, formatting,
    security issues, and type checking. These are prerequisite fixes that should be completed before
    architectural refactoring (complexity and SRP). Follows an iterative fix-test cycle until all basic
    linting passes with exit code 0 and Pylint reaches exactly 10.00/10. Does not cover complexity or
    SRP violations - see how-to-refactor-for-quality.md for architectural refactoring.

**Dependencies**: make lint-full, poetry, ruff, flake8, pylint, mypy, bandit, pip-audit

**Exports**: Clean code passing all basic linting checks, ready for architectural refactoring if needed

**Related**: how-to-refactor-for-quality.md, AGENTS.md (Quality Gates section)

**Implementation**: Sequential priority-based fixing with validation after each phase

---

## Overview

Basic linting fixes are **objective and mechanical** - they have clear right/wrong answers and don't require architectural decisions. Fix these first before tackling complexity or SRP violations.

**The Process**:
1. Run `make lint-full` to see all violations
2. Fix violations in priority order (style → security → types → pylint)
3. Run `make lint-full` again to verify
4. Run `make test` to ensure nothing broke
5. Repeat until clean

**Success Criteria**:
- `make lint-full` exits with code 0
- Pylint score is exactly 10.00/10
- All tests pass (`make test` exits with code 0)

---

## The Iterative Cycle

### Step 1: Assess Current State

```bash
# Run full linting to see all violations
make lint-full

# Check exit code
echo $?
# Must be 0 for success

# Look for Pylint score
# Must show: "Your code has been rated at 10.00/10"
```

### Step 2: Fix Violations by Priority

Follow the priority order below. Don't skip ahead - each phase builds on the previous.

### Step 3: Validate After Each Priority

```bash
# After fixing each priority level, validate
make lint-full
make test

# Both must exit with code 0
```

### Step 4: Repeat Until Clean

Continue the cycle until:
- `make lint-full` shows no violations
- Exit code is 0
- Pylint shows 10.00/10
- Tests all pass

---

## Priority 1: Code Style & Formatting

**Tools**: Ruff (formatter + linter), Flake8

**Why First**: Style issues are easiest to fix and auto-fixable. Get them out of the way.

### Auto-Fix with Ruff

```bash
# Auto-fix most style issues
make format

# This runs:
# - ruff format (fixes formatting)
# - ruff check --fix (fixes auto-fixable linting issues)
```

### Common Ruff Violations

#### Line Too Long (E501)

**Error**:
```
src/example.py:10:101: E501 Line too long (120 > 100 characters)
```

**Fix**: Break into multiple lines
```python
# Before
some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10, arg11, arg12, arg13, arg14)

# After
some_function(
    arg1, arg2, arg3, arg4, arg5,
    arg6, arg7, arg8, arg9, arg10,
    arg11, arg12, arg13, arg14
)
```

#### Unused Imports (F401)

**Error**:
```
src/example.py:5:1: F401 'pathlib.Path' imported but unused
```

**Fix**: Remove the import
```python
# Before
from pathlib import Path
import sys

# After
import sys
```

#### Import Order (I001)

**Error**:
```
src/example.py:3:1: I001 Import block is un-sorted or un-formatted
```

**Fix**: Let Ruff auto-fix it, or follow this order:
```python
# 1. Standard library
import sys
from pathlib import Path

# 2. Third-party
import click
import yaml

# 3. Local
from src.utils import helper
```

#### Undefined Name (F821)

**Error**:
```
src/example.py:15:5: F821 Undefined name 'result'
```

**Fix**: Define the variable or fix the typo
```python
# Before
def process():
    print(result)  # result is not defined

# After
def process():
    result = calculate()
    print(result)
```

### Common Flake8 Violations

#### Multiple Statements on One Line (E701)

**Error**:
```
src/example.py:10:1: E701 Multiple statements on one line (colon)
```

**Fix**: Split into multiple lines
```python
# Before
if condition: do_something()

# After
if condition:
    do_something()
```

#### Comparison to True/False (E712)

**Error**:
```
src/example.py:12:5: E712 Comparison to True should be 'if cond is True:' or 'if cond:'
```

**Fix**: Use implicit boolean check
```python
# Before
if is_valid == True:
    pass

# After
if is_valid:
    pass
```

### Validation

```bash
# Check style is clean
poetry run ruff check src/ tests/
poetry run ruff format --check src/ tests/
poetry run flake8 src/ tests/

# All should exit with code 0
```

---

## Priority 2: Security Issues

**Tools**: Bandit, pip-audit

**Why Second**: Security vulnerabilities must be fixed before moving forward.

### Running Security Checks

```bash
# Run security linting
make lint-security

# This runs:
# - Bandit (code security issues)
# - pip-audit (dependency vulnerabilities)
```

### Common Bandit Violations

#### B601: Parameterless Shell Execution

**Error**:
```
src/example.py:10:5: B601 Parameterless shell execution
```

**Fix**: Use subprocess with list arguments
```python
# Before
import os
os.system("ls -la")

# After
import subprocess
subprocess.run(["ls", "-la"], check=True)
```

#### B608: SQL Injection

**Error**:
```
src/example.py:15:5: B608 Possible SQL injection vector
```

**Fix**: Use parameterized queries
```python
# Before
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# After
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

#### B303: Insecure Hash Function

**Error**:
```
src/example.py:20:5: B303 Use of insecure MD5 hash function
```

**Fix**: Use secure hash function
```python
# Before
import hashlib
hash = hashlib.md5(data).hexdigest()

# After
import hashlib
hash = hashlib.sha256(data).hexdigest()
```

#### B105: Hardcoded Password

**Error**:
```
src/example.py:8:5: B105 Possible hardcoded password
```

**Fix**: Use environment variables or config
```python
# Before
password = "secret123"

# After
import os
password = os.environ.get("DB_PASSWORD")
```

### Suppressing False Positives

When Bandit flags a false positive:

```python
# Use nosec comment with justification
password_field = "password"  # nosec B105 - This is a field name, not a password
```

### Dependency Vulnerabilities

**Error**:
```
Found vulnerability in requests (1.0.0): CVE-2023-XXXXX
```

**Fix**: Update the dependency
```bash
# Update specific package
poetry update requests

# Or update pyproject.toml version constraint
# Then run:
poetry lock
poetry install
```

### Validation

```bash
# Check security is clean
poetry run bandit -r src/
poetry run pip-audit

# Both should show no issues
```

---

## Priority 3: Type Checking

**Tools**: MyPy

**Why Third**: Type checking catches potential runtime errors and improves code clarity.

### Running Type Checks

```bash
# Run type checking on src/ (not tests/)
poetry run mypy src/
```

### Common MyPy Violations

#### Missing Type Annotations

**Error**:
```
src/example.py:10: error: Function is missing a type annotation
```

**Fix**: Add type hints
```python
# Before
def calculate(x, y):
    return x + y

# After
def calculate(x: int, y: int) -> int:
    return x + y
```

#### Incompatible Return Type

**Error**:
```
src/example.py:15: error: Incompatible return value type (got "str", expected "int")
```

**Fix**: Return correct type or fix annotation
```python
# Before
def get_count() -> int:
    return "5"  # Wrong type

# After
def get_count() -> int:
    return 5
```

#### Argument Type Mismatch

**Error**:
```
src/example.py:20: error: Argument 1 has incompatible type "str"; expected "int"
```

**Fix**: Pass correct type or convert
```python
# Before
def process(value: int) -> None:
    pass

process("123")  # Wrong type

# After
def process(value: int) -> None:
    pass

process(int("123"))  # Convert to int
```

#### Missing Return Statement

**Error**:
```
src/example.py:25: error: Missing return statement
```

**Fix**: Add return statement or use None type
```python
# Before
def get_value() -> str:
    if condition:
        return "value"
    # Missing return for else case

# After
def get_value() -> str:
    if condition:
        return "value"
    return ""  # Add return
```

#### Optional Type Handling

**Error**:
```
src/example.py:30: error: Item "None" of "Optional[str]" has no attribute "upper"
```

**Fix**: Check for None before using
```python
# Before
def process(value: str | None) -> str:
    return value.upper()  # value might be None

# After
def process(value: str | None) -> str:
    if value is None:
        return ""
    return value.upper()
```

### Type Hints Quick Reference

```python
from pathlib import Path
from typing import Any

# Basic types
def func(x: int, y: str, z: bool) -> float:
    pass

# Collections
def func(items: list[str]) -> dict[str, int]:
    pass

# Optional (can be None)
def func(value: str | None) -> int | None:
    pass

# Path objects
def func(path: Path) -> None:
    pass

# Any (use sparingly)
def func(data: Any) -> Any:
    pass

# No return value
def func() -> None:
    pass
```

### Validation

```bash
# Check types are clean
poetry run mypy src/

# Should show: "Success: no issues found"
```

---

## Priority 4: Pylint Violations

**Tools**: Pylint

**Why Last**: Pylint is strictest and requires all previous fixes to be done first.

**Goal**: Reach exactly 10.00/10

### Running Pylint

```bash
# Run Pylint on src/ (not tests/)
poetry run pylint src/

# Look for the score at the end:
# "Your code has been rated at 10.00/10"
```

### Common Pylint Violations

#### Missing Docstring (C0111/C0116)

**Error**:
```
src/example.py:10:0: C0116: Missing function or method docstring
```

**Fix**: Add Google-style docstring
```python
# Before
def calculate(x: int, y: int) -> int:
    return x + y

# After
def calculate(x: int, y: int) -> int:
    """Calculate the sum of two integers.

    Args:
        x: First integer
        y: Second integer

    Returns:
        Sum of x and y
    """
    return x + y
```

#### Invalid Name (C0103)

**Error**:
```
src/example.py:5:0: C0103: Variable name "X" doesn't conform to snake_case naming style
```

**Fix**: Use snake_case
```python
# Before
X = 10
MyVariable = "test"

# After
x = 10
my_variable = "test"
```

#### Too Many Arguments (R0913)

**Error**:
```
src/example.py:15:0: R0913: Too many arguments (7/5)
```

**Fix**: Use a dataclass or dict
```python
# Before
def process(a, b, c, d, e, f, g):
    pass

# After
from dataclasses import dataclass

@dataclass
class ProcessConfig:
    """Configuration for process function."""
    a: int
    b: str
    c: float
    d: bool
    e: list
    f: dict
    g: str

def process(config: ProcessConfig) -> None:
    """Process with configuration."""
    pass
```

#### Unused Variable (W0612)

**Error**:
```
src/example.py:20:5: W0612: Unused variable 'result'
```

**Fix**: Remove or use the variable
```python
# Before
def calculate():
    result = expensive_operation()
    return 42

# After (use it)
def calculate():
    result = expensive_operation()
    return result

# Or (remove it)
def calculate():
    return 42
```

#### Redefined Outer Name (W0621)

**Error**:
```
src/example.py:25:5: W0621: Redefining name 'data' from outer scope
```

**Fix**: Rename the inner variable
```python
# Before
data = load_data()

def process():
    data = transform()  # Shadows outer 'data'
    return data

# After
data = load_data()

def process():
    processed_data = transform()
    return processed_data
```

#### Consider Using f-string (C0209)

**Error**:
```
src/example.py:30:5: C0209: Formatting a regular string which could be a f-string
```

**Fix**: Use f-string
```python
# Before
message = "Hello, {}".format(name)
message = "Count: %d" % count

# After
message = f"Hello, {name}"
message = f"Count: {count}"
```

### Disabling Pylint Checks

Only disable when truly necessary. Always add justification.

```python
# Disable for one line
result = some_function()  # pylint: disable=line-too-long  # Long URL cannot be broken

# Disable for a block
# pylint: disable=too-many-locals
def complex_function():
    # Complex logic requiring many variables
    pass
# pylint: enable=too-many-locals

# Disable for entire file (use very sparingly)
# pylint: disable=invalid-name
# This file uses non-standard naming for compatibility with external API
```

### Validation

```bash
# Check Pylint is at 10.00/10
poetry run pylint src/

# Must show: "Your code has been rated at 10.00/10"
# NOT 9.98/10, NOT 9.95/10 - exactly 10.00/10
```

---

## Quick Reference: Common Errors

| Error | Tool | Fix |
|-------|------|-----|
| Line too long | Ruff E501 | Break into multiple lines |
| Unused import | Ruff F401 | Remove import |
| Missing import | Ruff F821 | Add import |
| Import order | Ruff I001 | Run `make format` |
| Hardcoded password | Bandit B105 | Use environment variables |
| SQL injection | Bandit B608 | Use parameterized queries |
| Shell injection | Bandit B601 | Use subprocess with list args |
| Missing type hint | MyPy | Add type annotations |
| Type mismatch | MyPy | Fix types or convert |
| Optional not checked | MyPy | Check for None before use |
| Missing docstring | Pylint C0116 | Add Google-style docstring |
| Invalid name | Pylint C0103 | Use snake_case |
| Too many arguments | Pylint R0913 | Use dataclass or config object |
| Unused variable | Pylint W0612 | Remove or use variable |

---

## The Complete Workflow

### Initial Assessment

```bash
# See all violations
make lint-full > lint-output.txt 2>&1

# Check output and note:
# - How many Ruff/Flake8 violations?
# - How many Bandit security issues?
# - How many MyPy type errors?
# - What's the Pylint score?
```

### Fix in Order

```bash
# Phase 1: Style
make format
poetry run ruff check src/ tests/
poetry run flake8 src/ tests/
make test  # Ensure nothing broke

# Phase 2: Security
poetry run bandit -r src/
# Fix violations
make test  # Ensure nothing broke

# Phase 3: Types
poetry run mypy src/
# Fix violations
make test  # Ensure nothing broke

# Phase 4: Pylint
poetry run pylint src/
# Fix violations until 10.00/10
make test  # Ensure nothing broke
```

### Final Validation

```bash
# Run everything
make lint-full
echo "Exit code: $?"  # Must be 0

# Run tests
make test
echo "Exit code: $?"  # Must be 0

# Check Pylint score
# Must show: "Your code has been rated at 10.00/10"
```

### Commit

Only commit when:
- `make lint-full` exits with code 0
- Pylint shows exactly 10.00/10
- `make test` exits with code 0

```bash
git add .
git commit -m "fix: Resolve all linting violations"
```

---

## What This Guide Does NOT Cover

This guide covers **objective, mechanical linting fixes**. It does NOT cover:

- **Complexity violations** (Radon, Xenon) - See `how-to-refactor-for-quality.md`
- **SRP violations** - See `how-to-refactor-for-quality.md`
- **DRY violations** (duplicate code) - See `how-to-refactor-for-quality.md`
- **Architectural refactoring** - See `how-to-refactor-for-quality.md`

If `make lint-complexity`, `make lint-solid`, or `make lint-dry` show violations, complete this guide first, then proceed to architectural refactoring.

---

## Critical Insights: The Refactoring Trap

**IMPORTANT**: When fixing DRY violations, you can inadvertently create MORE violations than you fix. This section explains why and how to avoid it.

### The "10 Fixed, 3 Created" Problem

**Symptom**: You fix 10 DRY violations but the linter now reports 3 new ones you just created.

**Root Cause**: Extraction without sufficient abstraction leads to new duplication patterns.

**Example of the Problem**:
```python
# Before: 4 files have duplicate validation logic
def validate_order(order):
    if not order.get("customer_id"):
        raise ValueError("Missing customer_id")
    if not order.get("items"):
        raise ValueError("Missing items")

# Bad fix: Extract to shared function
def validate_order_fields(order):
    if not order.get("customer_id"):
        raise ValueError("Missing customer_id")
    if not order.get("items"):
        raise ValueError("Missing items")

# Now you also need validate_user_fields, validate_product_fields, etc.
# Each with the same pattern! You've created NEW duplication.
```

**Better fix**: Extract at the right level of abstraction
```python
# Good: Extract the PATTERN, not just the code
def validate_required_fields(data: dict, required_fields: list[str], entity_name: str) -> None:
    """Validate required fields exist in data dictionary.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        entity_name: Name of entity for error messages

    Raises:
        ValueError: If any required field is missing
    """
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing {field} in {entity_name}")

# Usage - no more duplication!
validate_required_fields(order, ["customer_id", "items"], "order")
validate_required_fields(user, ["email", "password"], "user")
validate_required_fields(product, ["name", "price"], "product")
```

### Key Principles to Avoid Creating New Violations

#### 1. The "Rule of Three" - Wait for Patterns

**Don't refactor duplication the first or second time you see it. Wait for the THIRD occurrence.**

- **First occurrence**: Write the code
- **Second occurrence**: Duplicate it (yes, duplicate!)
- **Third occurrence**: NOW extract it

**Why**: The first two instances might be coincidental. The third confirms a real pattern worth abstracting.

**Example**:
```python
# First time: Write user validation
def validate_user(user):
    if "@" not in user.get("email", ""):
        raise ValueError("Invalid email")

# Second time: Duplicate in admin validation
def validate_admin(admin):
    if "@" not in admin.get("email", ""):  # DUPLICATE but OK
        raise ValueError("Invalid email")

# Third time: NOW extract
class EmailValidator:
    def validate(self, email: str) -> None:
        if "@" not in email:
            raise ValueError("Invalid email")
```

#### 2. Distinguish True Duplication from Coincidental Similarity

**Not all similar code is true duplication!**

**True Duplication** (should be extracted):
- Same purpose and behavior
- Will evolve together
- Changes in one should affect all instances

**Coincidental Similarity** (leave separate):
- Looks similar but serves different purposes
- Likely to diverge in the future
- Different contexts and semantics

**Example**:
```python
# These LOOK similar but are NOT true duplicates:

# User password validation - business rule
def validate_user_password(password: str):
    if len(password) < 8:
        raise ValueError("Password too short")

# Database password validation - technical constraint
def validate_db_password(password: str):
    if len(password) < 8:
        raise ValueError("Password too short")

# Don't extract! These are likely to diverge:
# - User passwords might require special characters
# - DB passwords might have different requirements
# They're only coincidentally similar NOW
```

#### 3. Extract at the Right Level of Abstraction

**Common mistake**: Extracting code that's too specific leads to many similar extracted functions.

**Signs you extracted at wrong level**:
- You create multiple functions with same structure
- Function names differ only by entity name
- You end up with `validate_user_fields()`, `validate_order_fields()`, `validate_product_fields()`

**Fix**: Extract the PATTERN, not the INSTANCE

**Bad** (too specific):
```python
def format_user_error(user_id: str, error: str) -> str:
    return f"User {user_id}: {error}"

def format_order_error(order_id: str, error: str) -> str:
    return f"Order {order_id}: {error}"

def format_product_error(product_id: str, error: str) -> str:
    return f"Product {product_id}: {error}"

# Created 3 similar functions - new duplication!
```

**Good** (right abstraction):
```python
def format_entity_error(entity_type: str, entity_id: str, error: str) -> str:
    """Format error message for any entity.

    Args:
        entity_type: Type of entity (user, order, product, etc.)
        entity_id: Entity identifier
        error: Error message

    Returns:
        Formatted error message
    """
    return f"{entity_type.title()} {entity_id}: {error}"

# Usage - one function handles all cases
format_entity_error("user", user_id, "Invalid email")
format_entity_error("order", order_id, "Missing items")
format_entity_error("product", product_id, "Out of stock")
```

#### 4. Use Parameterization and Dataclasses

**Problem**: Creating many builder/factory functions with same structure

**Solution**: Use dataclasses to capture variations

**Bad** (creates new duplication):
```python
def build_user_violation(user_id, message):
    return {"type": "user", "id": user_id, "message": message, "severity": "ERROR"}

def build_order_violation(order_id, message):
    return {"type": "order", "id": order_id, "message": message, "severity": "ERROR"}

def build_product_violation(product_id, message):
    return {"type": "product", "id": product_id, "message": message, "severity": "ERROR"}
```

**Good** (single parameterized function):
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ViolationInfo:
    """Information for building violations."""
    entity_type: str
    entity_id: str
    message: str
    severity: Literal["ERROR", "WARNING", "INFO"] = "ERROR"

def build_violation(info: ViolationInfo) -> dict:
    """Build violation dictionary from info.

    Args:
        info: Violation information

    Returns:
        Violation dictionary
    """
    return {
        "type": info.entity_type,
        "id": info.entity_id,
        "message": info.message,
        "severity": info.severity,
    }

# Usage - one function, many uses
build_violation(ViolationInfo("user", user_id, "Invalid email"))
build_violation(ViolationInfo("order", order_id, "Missing items"))
build_violation(ViolationInfo("product", product_id, "Out of stock"))
```

#### 5. Template Method Pattern for Similar Workflows

**Problem**: Multiple classes with same workflow but different steps

**Solution**: Base class with template method

**Bad** (creates duplication):
```python
class UserProcessor:
    def process(self, user):
        self.validate_user(user)
        result = self.transform_user(user)
        self.save_user(result)
        return result

class OrderProcessor:
    def process(self, order):  # DUPLICATE workflow
        self.validate_order(order)  # Different validation
        result = self.transform_order(order)  # Different transform
        self.save_order(result)  # Different save
        return result

# Same workflow structure duplicated!
```

**Good** (template method):
```python
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """Base processor with common workflow."""

    def process(self, data: dict) -> dict:
        """Process data using template method pattern.

        Args:
            data: Data to process

        Returns:
            Processed data
        """
        self.validate(data)
        result = self.transform(data)
        self.save(result)
        return result

    @abstractmethod
    def validate(self, data: dict) -> None:
        """Validate data - subclasses implement."""

    @abstractmethod
    def transform(self, data: dict) -> dict:
        """Transform data - subclasses implement."""

    @abstractmethod
    def save(self, data: dict) -> None:
        """Save data - subclasses implement."""

class UserProcessor(BaseProcessor):
    def validate(self, data: dict) -> None:
        # User-specific validation
        pass

    def transform(self, data: dict) -> dict:
        # User-specific transformation
        pass

    def save(self, data: dict) -> None:
        # User-specific save
        pass

# Workflow defined ONCE, variations implemented cleanly
```

### Anti-Patterns That Create More Violations

#### Anti-Pattern 1: Half-Way Extraction

**Problem**: Extract some duplicates but leave others

```python
# You fix duplication in UserService and OrderService
# But leave same pattern in ProductService and CustomerService
# Now you have PARTIAL extraction - still have violations!
```

**Fix**: When extracting, find ALL instances and refactor ALL of them

```bash
# Before extracting, search for all similar patterns
grep -r "similar_pattern" src/
# Make sure you refactor ALL occurrences
```

#### Anti-Pattern 2: Creating Parallel Hierarchies

**Problem**: Creating matched sets of classes/functions

```python
# Bad - parallel structures
class UserValidator:
    def validate(self, user): pass

class UserTransformer:
    def transform(self, user): pass

class UserPersister:
    def persist(self, user): pass

class OrderValidator:  # Parallel to UserValidator
    def validate(self, order): pass

class OrderTransformer:  # Parallel to UserTransformer
    def transform(self, order): pass

class OrderPersister:  # Parallel to UserPersister
    def persist(self, order): pass

# You've created a PATTERN of duplication!
```

**Fix**: Use generic/template classes

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Validator(Generic[T], ABC):
    @abstractmethod
    def validate(self, item: T) -> None:
        pass

class Transformer(Generic[T], ABC):
    @abstractmethod
    def transform(self, item: T) -> T:
        pass

class Persister(Generic[T], ABC):
    @abstractmethod
    def persist(self, item: T) -> None:
        pass

# One set of abstractions for ALL entities
```

#### Anti-Pattern 3: Copy-Paste Refactoring

**Problem**: Copying your extracted utility to create variations

```python
# You extract validation logic
def validate_email_field(data, field_name):
    if "@" not in data.get(field_name, ""):
        raise ValueError(f"Invalid email in {field_name}")

# Then copy-paste to create similar functions
def validate_url_field(data, field_name):  # COPY-PASTE
    if "http" not in data.get(field_name, ""):  # Changed check
        raise ValueError(f"Invalid URL in {field_name}")

def validate_phone_field(data, field_name):  # COPY-PASTE
    if len(data.get(field_name, "")) < 10:  # Changed check
        raise ValueError(f"Invalid phone in {field_name}")

# You just created MORE duplication!
```

**Fix**: Parameterize the validation

```python
from typing import Callable

def validate_field(
    data: dict,
    field_name: str,
    validator_func: Callable[[str], bool],
    error_type: str
) -> None:
    """Generic field validation.

    Args:
        data: Data dictionary
        field_name: Field to validate
        validator_func: Function that returns True if valid
        error_type: Type description for error message

    Raises:
        ValueError: If validation fails
    """
    value = data.get(field_name, "")
    if not validator_func(value):
        raise ValueError(f"Invalid {error_type} in {field_name}")

# Usage - one function, many validators
validate_field(data, "email", lambda v: "@" in v, "email")
validate_field(data, "url", lambda v: "http" in v, "URL")
validate_field(data, "phone", lambda v: len(v) >= 10, "phone")
```

### Validation Checklist Before Committing

Before committing refactored code, verify:

- [ ] Did I wait for the third occurrence before extracting?
- [ ] Is this TRUE duplication or coincidental similarity?
- [ ] Did I extract at the right level of abstraction?
- [ ] Did I refactor ALL instances, not just some?
- [ ] Did I create any new parallel structures?
- [ ] Can my extracted code be parameterized further?
- [ ] Run `make lint-dry` - did violations decrease or increase?
- [ ] Review the NEW code for potential duplication patterns

### Success Metrics

**Good refactoring**:
- Violations decrease significantly (>50% reduction)
- No new duplication patterns created
- Code is more flexible and reusable
- Tests still pass

**Bad refactoring** (revert and rethink):
- Violations decrease slightly (<20% reduction)
- New duplication patterns appear
- Created parallel hierarchies
- Abstraction is more complex than original duplication

---

## When Linting Seems Impossible

### "I can't reach 10.00/10!"

Common causes:
1. Missing docstrings (add Google-style docs)
2. Invalid names (use snake_case)
3. Unused variables (remove them)
4. Hidden violations in files you didn't check

```bash
# Find all violations
poetry run pylint src/ | grep -E "^src/"

# Fix each file one by one
poetry run pylint src/specific_file.py
```

### "Tests break after linting fixes!"

This means your tests were relying on buggy behavior.

1. Check what broke: `pytest -v`
2. Fix the test to match the corrected code
3. If the linting fix was wrong, revert and find a better approach

### "Auto-fix made things worse!"

Sometimes `make format` introduces issues:

1. Review changes: `git diff`
2. If bad, revert: `git checkout -- src/file.py`
3. Fix manually instead of using auto-fix

---

## Success Checklist

Before moving to architectural refactoring:

- [ ] `make lint-full` exits with code 0
- [ ] Pylint score is exactly 10.00/10
- [ ] `make test` exits with code 0
- [ ] No Ruff violations
- [ ] No Flake8 violations
- [ ] No Bandit security issues
- [ ] No MyPy type errors
- [ ] All imports sorted and unused imports removed
- [ ] All functions have type hints
- [ ] All public functions have docstrings

---

## Next Steps

After completing basic linting:

1. **If `make lint-complexity` passes**, **`make lint-solid` passes**, and **`make lint-dry` passes**:
   - You're done! Commit your changes.

2. **If complexity, SRP, or DRY violations remain**:
   - Proceed to `.ai/howtos/how-to-refactor-for-quality.md`
   - Follow the architectural refactoring guide

3. **Before committing**:
   - Run `make lint-full && make test`
   - Both must exit with code 0
   - See `AGENTS.md` Quality Gates section

---

## See Also

- **Architectural refactoring**: `.ai/howtos/how-to-refactor-for-quality.md`
- **Quality standards**: `AGENTS.md` (Quality Gates section)
- **Pre-commit hooks**: `.ai/howtos/how-to-debug-failing-hooks.md`
- **Testing**: `.ai/howtos/how-to-write-tests.md`
- **Makefile targets**: `Makefile` (linting commands)
