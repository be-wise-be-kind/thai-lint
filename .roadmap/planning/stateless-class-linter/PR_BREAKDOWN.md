# Stateless Class Linter - PR Breakdown (TDD Approach)

**Purpose**: Detailed Test-Driven Development breakdown of Stateless Class Linter into manageable pull requests

**Scope**: Complete linter implementation from test specification through CLI integration using strict TDD methodology

**Overview**: Comprehensive breakdown of the Stateless Class Linter feature into 3 manageable pull requests
    following Test-Driven Development (RED-GREEN-REFACTOR) cycles. Each PR starts with writing comprehensive
    tests that define expected behavior, implements minimum code to pass tests, then refactors for quality.
    Includes detailed TDD steps, test case specifications, and success criteria for each development phase.

**Dependencies**: pytest, AST module, existing linter patterns (DRY, SRP linters)

**Exports**: TDD implementation plans, test specifications, refactoring strategies for each PR

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Strict RED-GREEN-REFACTOR methodology with tests written before any implementation code

---

## TDD Principles for This Feature

### Red-Green-Refactor Cycle
1. **RED**: Write a test that fails (defines expected behavior)
2. **GREEN**: Write minimum code to make the test pass
3. **REFACTOR**: Improve code quality while keeping tests passing

### Key Rules
- ✅ **Tests first**: Never write implementation before tests
- ✅ **Minimal code**: Only implement what tests require
- ✅ **One cycle at a time**: Complete RED-GREEN-REFACTOR before next test
- ✅ **Refactor fearlessly**: Tests provide safety net

---

## PR1: Core Detection Logic (TDD)

### Overview
Implement the core stateless class detector using TDD. Start by writing tests that define what a "stateless class" is, then implement the detector to satisfy those tests.

### RED Phase: Write Failing Tests

#### Step 1: Setup Test Infrastructure
```bash
# Create test directory
mkdir -p tests/test_linters/test_stateless_class

# Create test file
touch tests/test_linters/test_stateless_class/__init__.py
touch tests/test_linters/test_stateless_class/test_detector.py
```

#### Step 2: Write First Test (Simplest Case)

**Test**: Detect class without `__init__` and with 2+ methods

```python
# tests/test_linters/test_stateless_class/test_detector.py

def test_detects_stateless_class_without_init():
    """Should detect class with methods but no __init__ as violation."""
    code = '''
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
'''
    violations = detect_stateless_classes(code)
    assert len(violations) == 1
    assert "StatelessHelper" in violations[0].message
```

**Run test**: Should fail with `NameError: name 'detect_stateless_classes' is not defined`

#### Step 3: Write Core Test Cases

Write these tests in order (each should fail initially):

1. **test_detects_stateless_class_without_init** ✅ (written above)
2. **test_ignores_class_with_init**
   ```python
   def test_ignores_class_with_init():
       """Should not flag class with __init__."""
       code = '''
   class WithInit:
       def __init__(self):
           self.data = []

       def method(self):
           return self.data
   '''
       violations = detect_stateless_classes(code)
       assert len(violations) == 0
   ```

3. **test_ignores_class_with_instance_attributes**
4. **test_ignores_abc_class**
5. **test_ignores_protocol_class**
6. **test_ignores_decorated_class**
7. **test_ignores_class_with_class_attributes**
8. **test_ignores_class_with_new**
9. **test_ignores_empty_class**
10. **test_ignores_class_with_single_method**
11. **test_detects_real_world_tokenhasher**

**Success Criteria for RED Phase**:
- ✅ All 11 tests written
- ✅ All tests fail appropriately (not due to syntax errors)
- ✅ Tests are clear and well-documented
- ✅ Run `pytest tests/test_linters/test_stateless_class/ -v` shows 11 FAILED

### GREEN Phase: Implement Minimum Code

#### Step 1: Create Module Structure

```bash
mkdir -p src/linters/stateless_class
touch src/linters/stateless_class/__init__.py
touch src/linters/stateless_class/detector.py
touch src/linters/stateless_class/violation.py
```

#### Step 2: Implement Violation Model

**Goal**: Make imports work

```python
# src/linters/stateless_class/violation.py

class StatelessClassViolation:
    """Represents a stateless class violation."""

    def __init__(self, class_name: str, line_number: int):
        self.class_name = class_name
        self.line_number = line_number
        self.message = f"Class '{class_name}' has no state and should be module-level functions"
```

#### Step 3: Implement Minimal Detector

**Goal**: Make first test pass

```python
# src/linters/stateless_class/detector.py
import ast

def detect_stateless_classes(code: str) -> list:
    """Detect classes that should be module-level functions."""
    # Start with simplest implementation
    # Just parse and return empty list
    tree = ast.parse(code)
    return []
```

**Run test**: First test should still fail (returns empty list)

#### Step 4: Incrementally Add Logic

Add logic **one test at a time**:

1. Make `test_detects_stateless_class_without_init` pass:
   - Add AST visitor
   - Check for ClassDef without __init__
   - Check for 2+ methods
   - Return violation

2. Make `test_ignores_class_with_init` pass:
   - Skip classes that have __init__ method

3. Continue for each test...

**Key principle**: After each change, run tests and ensure only the target test passes (or one more passes).

#### Step 5: Complete Implementation

**Success Criteria for GREEN Phase**:
- ✅ All 11 tests pass
- ✅ Run `pytest tests/test_linters/test_stateless_class/ -v` shows 11 PASSED
- ✅ Code is minimal (no extra features beyond tests)

### REFACTOR Phase: Improve Code Quality

#### Step 1: Extract Helper Methods

Identify repeated code and extract:
```python
def _has_init_method(class_node: ast.ClassDef) -> bool:
    """Check if class has __init__ method."""
    ...

def _has_instance_attributes(class_node: ast.ClassDef) -> bool:
    """Check if class has instance attributes."""
    ...
```

**Run tests after each extraction**: Should still pass

#### Step 2: Add Type Hints

```python
from typing import List
from ast import ClassDef

def detect_stateless_classes(code: str) -> List[StatelessClassViolation]:
    """Detect classes that should be module-level functions.

    Args:
        code: Python source code to analyze

    Returns:
        List of stateless class violations
    """
    ...
```

**Run tests**: Should still pass

#### Step 3: Add Docstrings (Google Style)

Add comprehensive docstrings to all methods.

**Run tests**: Should still pass

#### Step 4: Run Quality Checks

```bash
# Run linting
poetry run pylint src/linters/stateless_class/

# Run complexity checks
poetry run xenon --max-absolute A src/linters/stateless_class/

# Run all tests
poetry run pytest tests/test_linters/test_stateless_class/ -v --cov=src/linters/stateless_class
```

**Success Criteria for REFACTOR Phase**:
- ✅ All tests still pass
- ✅ Pylint score: 10.00/10
- ✅ All complexity checks pass (A-grade)
- ✅ Test coverage >90%
- ✅ Code is clean, readable, and well-documented

### PR1 Files Created

```
src/linters/stateless_class/
├── __init__.py
├── detector.py         # Main detection logic
└── violation.py        # Violation model

tests/test_linters/test_stateless_class/
├── __init__.py
└── test_detector.py    # All 11 test cases
```

### PR1 Commit Strategy

1. Commit after RED phase: "test: Add failing tests for stateless class detection"
2. Commit after GREEN phase: "feat: Implement stateless class detector"
3. Commit after REFACTOR: "refactor: Clean up detector code and add documentation"

---

## PR2: CLI Integration & Config (TDD)

### Overview
Integrate the detector with thai-lint CLI using TDD. Write integration tests first, then wire up the CLI.

### RED Phase: Write Integration Tests

#### Step 1: Create Integration Test File

```bash
touch tests/test_cli/test_stateless_class_command.py
```

#### Step 2: Write CLI Test Cases

Write these tests (should fail initially):

1. **test_cli_exits_zero_when_no_violations**
   ```python
   def test_cli_exits_zero_when_no_violations(tmp_path):
       """CLI should exit 0 when file has no violations."""
       test_file = tmp_path / "clean.py"
       test_file.write_text('''
   class WithInit:
       def __init__(self):
           self.data = []
   ''')

       result = runner.invoke(cli, ['stateless-class', str(test_file)])
       assert result.exit_code == 0
   ```

2. **test_cli_exits_one_when_violations_found**
3. **test_cli_outputs_violation_details**
4. **test_config_file_loaded**
5. **test_linter_can_be_disabled_via_config**

#### Step 3: Verify Tests Fail

```bash
pytest tests/test_cli/test_stateless_class_command.py -v
```

Should show all tests FAILED (command doesn't exist yet)

**Success Criteria for RED Phase**:
- ✅ All integration tests written
- ✅ All tests fail appropriately
- ✅ Tests cover CLI behavior comprehensively

### GREEN Phase: Implement CLI Integration

#### Step 1: Add CLI Command

Study existing commands in `src/cli.py`, then add:

```python
@cli.command()
@click.argument('path', type=click.Path(exists=True))
def stateless_class(path):
    """Detect stateless classes that should be functions."""
    # Minimal implementation to make tests pass
    ...
```

#### Step 2: Wire Up Detector

Connect detector to CLI framework (follow DRY/SRP patterns).

#### Step 3: Add Configuration Support

Make config tests pass.

**Success Criteria for GREEN Phase**:
- ✅ All CLI integration tests pass
- ✅ `thai-lint stateless-class` command works

### REFACTOR Phase: Polish CLI

- Improve error messages
- Add helpful suggestions
- Clean up code structure

**Run quality checks**:
```bash
poetry run pylint src/
pytest tests/ -v --cov
```

### PR2 Files Modified/Created

```
src/cli.py                                      # Add stateless-class command
src/linters/stateless_class/__init__.py        # Export for CLI
tests/test_cli/test_stateless_class_command.py # Integration tests
```

---

## PR3: Documentation & Self-Dogfood

### Overview
Document the linter and run it on our own codebase to validate it works.

### Tasks (Not Strictly TDD)

#### Step 1: Run on Our Codebase

```bash
# Find stateless classes in our code
thai-lint stateless-class src/

# Review violations - are they legitimate?
```

#### Step 2: Fix or Justify Violations

For each violation found:
- **Option A**: Refactor class to module functions (if appropriate)
- **Option B**: Add justification comment and suppress (if legitimate)

Document reasoning in PR.

#### Step 3: Write Documentation

Create:
- User guide with examples
- Configuration documentation
- Migration guide (class → functions)
- Update README

#### Step 4: Update Changelog

Document new linter in CHANGELOG.md

### PR3 Files Created/Modified

```
docs/linters/stateless-class.md    # User documentation
README.md                           # Add to linter list
CHANGELOG.md                        # Document new feature
examples/stateless-class/           # Before/after examples
```

---

## Testing Requirements

### Unit Test Coverage
- Minimum 90% coverage for detector module
- All edge cases covered
- Clear test names and documentation

### Integration Test Coverage
- CLI commands tested end-to-end
- Configuration loading tested
- Error handling tested

### Quality Standards
- Pylint score: 10.00/10
- All complexity checks pass (A-grade)
- All tests pass before merge

---

## TDD Success Metrics

### Process Metrics
- Tests written before code: 100%
- Test coverage: >90%
- RED-GREEN-REFACTOR cycles documented

### Quality Metrics
- Zero test failures in final PR
- All quality gates pass
- No false positives found during dogfooding

---

## Implementation Timeline

### PR1: Core Detection (TDD)
**Estimated**: 1 session
- RED: 30 minutes (write 11 tests)
- GREEN: 1 hour (implement detector)
- REFACTOR: 30 minutes (clean up code)

### PR2: CLI Integration (TDD)
**Estimated**: 1 session
- RED: 20 minutes (write 5 CLI tests)
- GREEN: 40 minutes (wire up CLI)
- REFACTOR: 20 minutes (polish)

### PR3: Documentation
**Estimated**: 1 session
- Dogfood: 30 minutes
- Document: 30 minutes
- Update changelog: 10 minutes

**Total**: ~3 sessions (~4 hours)
