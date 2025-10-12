# Magic Numbers Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Magic Numbers Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from test creation through production deployment and self-dogfooding

**Overview**: Comprehensive breakdown of the Magic Numbers Linter feature into 6 manageable, atomic
    pull requests following Test-Driven Development (TDD) principles. Each PR is designed to be self-contained,
    testable, and maintains application functionality while incrementally building toward the complete feature.
    Includes detailed implementation steps, file structures, testing requirements, and success criteria for each
    PR. Follows red-green-refactor TDD cycle with explicit validation gates.

**Dependencies**: BaseLintRule interface, Python AST parsing, Tree-sitter (TypeScript), pytest framework, thai-lint orchestrator

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with TDD methodology, detailed step-by-step implementation guidance, and comprehensive quality validation

---

## Overview
This document breaks down the Magic Numbers Linter feature into 6 manageable, atomic PRs following TDD principles. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Follows red-green-refactor TDD cycle
- Incrementally builds toward the complete feature
- Revertible if needed

**TDD Approach**:
- **Red**: Write failing tests first
- **Green**: Implement minimal code to pass tests
- **Refactor**: Improve code quality to meet standards

---

## PR1: Test Suite for Python Magic Numbers Detection

**Scope**: Write comprehensive failing tests for Python magic number detection (TDD RED phase)

**Branch**: `feature/magic-numbers-python-tests`

**Complexity**: Medium (test design requires understanding detection patterns)

**Estimated Effort**: 3-4 hours

### Files to Create

```
tests/unit/linters/magic_numbers/
├── __init__.py                          # Package init
├── conftest.py                          # Shared fixtures
├── test_python_magic_numbers.py         # Core Python detection tests
├── test_config_loading.py               # Configuration tests
├── test_ignore_directives.py            # Ignore directive tests
├── test_edge_cases.py                   # Edge cases and corner cases
└── test_library_api.py                  # Library API convenience function
```

### Implementation Steps

#### Step 1: Review Reference Materials
```bash
# Read test writing guide
cat .ai/howtos/how-to-write-tests.md

# Review example implementation (for patterns only)
cat /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/literals/magic_number_rules.py

# Review existing test patterns
ls -la tests/unit/linters/nesting/
cat tests/unit/linters/nesting/test_python_nesting.py
```

#### Step 2: Create Test Directory Structure
```bash
mkdir -p tests/unit/linters/magic_numbers
touch tests/unit/linters/magic_numbers/__init__.py
touch tests/unit/linters/magic_numbers/conftest.py
```

#### Step 3: Write `conftest.py` with Shared Fixtures
```python
"""Shared fixtures for magic numbers linter tests."""
import pytest
from pathlib import Path

@pytest.fixture
def magic_numbers_config():
    """Standard magic numbers configuration."""
    return {
        "enabled": True,
        "allowed_numbers": [-1, 0, 1, 2, 10, 100, 1000],
        "max_small_integer": 10,
    }

@pytest.fixture
def python_file_with_magic_numbers(mock_project_root):
    """Create a Python file with magic numbers."""
    test_file = mock_project_root / "test_magic.py"
    test_file.write_text("""
def calculate_timeout():
    return 3600  # Magic number - should be named constant

def process_items(items):
    for i in range(5):  # Small int in range - acceptable
        items[i] *= 3.14159  # Magic number - PI should be constant
""")
    return test_file
```

#### Step 4: Write Core Detection Tests (`test_python_magic_numbers.py`)

Focus areas:
- **Basic detection**: Detect numeric literals in expressions
- **Acceptable contexts**:
  - Constants (UPPERCASE names)
  - Small integers in `range()` or `enumerate()`
  - Test files
  - Configuration contexts
- **Type coverage**: int, float (NOT strings)
- **Ignore directives**: Inline comments

Example test structure:
```python
class TestBasicDetection:
    """Test basic magic number detection."""

    def test_detects_integer_literal_in_assignment(self):
        """Should detect integer magic number in assignment."""
        # Test code with magic number
        # Assert violation found

    def test_detects_float_literal_in_calculation(self):
        """Should detect float magic number in calculation."""
        # Test code with 3.14159
        # Assert violation found

class TestAcceptableContexts:
    """Test contexts where numbers are acceptable."""

    def test_ignores_constant_definitions(self):
        """Should not flag numbers in UPPERCASE constant definitions."""
        # TIMEOUT = 3600 should be acceptable

    def test_ignores_small_integers_in_range(self):
        """Should not flag small integers used in range()."""
        # range(5) should be acceptable

    def test_ignores_test_files(self):
        """Should not flag numbers in test files."""
        # Files matching test_*.py pattern

class TestIgnoreDirectives:
    """Test inline ignore directives."""

    def test_respects_inline_ignore_directive(self):
        """Should ignore violations with inline ignore comment."""
        # x = 3600  # thailint: ignore[magic-numbers]
```

#### Step 5: Write Configuration Tests (`test_config_loading.py`)

Test:
- Default configuration
- Custom allowed_numbers list
- max_small_integer threshold
- Disabled state

#### Step 6: Write Edge Case Tests (`test_edge_cases.py`)

Test:
- Negative numbers
- Very large numbers
- Scientific notation (1e6)
- Zero and one (should be allowed by default)
- Numbers in different contexts (comparisons, returns, arguments)

#### Step 7: Write Library API Tests (`test_library_api.py`)

Test convenience function:
```python
from src.linters.magic_numbers import lint

def test_lint_convenience_function():
    """Test the convenience lint() function."""
    # Create file with magic numbers
    # violations = lint(file_path, config={'allowed_numbers': [1, 2, 3]})
    # Assert violations found
```

### Validation

```bash
# Step 1: Verify tests are written
ls -la tests/unit/linters/magic_numbers/

# Step 2: Run tests (should ALL FAIL - this is TDD RED phase)
pytest tests/unit/linters/magic_numbers/ -v
# Expected: Multiple failures because implementation doesn't exist yet

# Step 3: Lint the test code itself
just lint-full
# Expected: Exit code 0 (test code must be clean)

# Step 4: Verify test code passes all quality gates
poetry run pylint tests/unit/linters/magic_numbers/
# Expected: 10.00/10

poetry run xenon --max-absolute A tests/unit/linters/magic_numbers/
# Expected: No errors (all A-grade)
```

### Success Criteria
- [ ] Test directory structure created
- [ ] 5+ test files with comprehensive coverage
- [ ] All tests FAIL (because implementation doesn't exist - TDD RED)
- [ ] Test code passes linting (Pylint 10.00/10)
- [ ] Test code is A-grade complexity (Xenon)
- [ ] Tests follow project conventions (from how-to-write-tests.md)
- [ ] No implementation code written yet (tests only)

### Commit Message
```
feat(tests): Add comprehensive test suite for Python magic numbers linter

TDD RED phase - all tests fail as expected. Tests cover:
- Basic numeric literal detection (int, float)
- Acceptable contexts (constants, range(), test files)
- Ignore directives
- Configuration loading
- Edge cases (negative, large, scientific notation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR2: Python Magic Numbers Implementation

**Scope**: Implement Python magic number detection to pass PR1 tests (TDD GREEN phase)

**Branch**: `feature/magic-numbers-python-impl`

**Complexity**: Medium

**Estimated Effort**: 4-5 hours

**Prerequisites**: PR1 merged

### Files to Create

```
src/linters/magic_numbers/
├── __init__.py                          # Package init with exports
├── linter.py                            # MagicNumberRule (BaseLintRule)
├── config.py                            # MagicNumberConfig dataclass
├── python_analyzer.py                   # Python AST analysis
├── context_analyzer.py                  # Context detection (range, constants, etc)
└── violation_builder.py                 # Violation message construction
```

### Implementation Steps

#### Step 1: Create Module Structure
```bash
mkdir -p src/linters/magic_numbers
touch src/linters/magic_numbers/{__init__.py,linter.py,config.py,python_analyzer.py,context_analyzer.py,violation_builder.py}
```

#### Step 2: Implement `config.py`
```python
"""Magic numbers linter configuration."""
from dataclasses import dataclass, field

@dataclass
class MagicNumberConfig:
    """Configuration for magic number detection."""
    enabled: bool = True
    allowed_numbers: set[int | float] = field(
        default_factory=lambda: {-1, 0, 1, 2, 10, 100, 1000}
    )
    max_small_integer: int = 10
```

#### Step 3: Implement `context_analyzer.py`

Extract context detection logic:
- `is_constant_definition()` - Check if UPPERCASE name
- `is_in_range_context()` - Check if inside range() or enumerate()
- `is_test_file()` - Check if file matches test_*.py pattern
- `is_acceptable_context()` - Main decision function

Reference: `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/literals/magic_number_rules.py` lines 27-135

#### Step 4: Implement `python_analyzer.py`

AST visitor to find numeric literals:
```python
class MagicNumberAnalyzer(ast.NodeVisitor):
    """AST visitor to find numeric literals."""

    def visit_Constant(self, node):
        """Visit constant nodes and check for numeric literals."""
        if isinstance(node.value, (int, float)):
            # Check context and collect if magic number
            pass
```

#### Step 5: Implement `violation_builder.py`

Create violation messages:
```python
class MagicNumberViolationBuilder:
    """Builds violation messages for magic numbers."""

    def create_violation(self, node, value, context):
        """Create a violation for a magic number."""
        return Violation(
            rule_id="magic-numbers.numeric-literal",
            message=f"Magic number {value} should be a named constant",
            # ... other fields
        )
```

#### Step 6: Implement `linter.py` (Main Rule Class)

```python
class MagicNumberRule(BaseLintRule):
    """Detects magic numbers in code."""

    @property
    def rule_id(self) -> str:
        return "magic-numbers.numeric-literal"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for magic number violations."""
        if context.language == "python":
            return self._check_python(context)
        return []

    def _check_python(self, context, config):
        # Parse AST
        # Run analyzer
        # Build violations
        pass
```

Follow pattern from `src/linters/nesting/linter.py`

#### Step 7: Implement `__init__.py` with Exports

```python
"""Magic numbers linter package."""
from .linter import MagicNumberRule
from .config import MagicNumberConfig

__all__ = ["MagicNumberRule", "MagicNumberConfig", "lint"]

def lint(path, config=None):
    """Convenience function for linting."""
    # Setup orchestrator and run linter
    pass
```

#### Step 8: Iterative Development (Green Phase)

```bash
# Run tests repeatedly
pytest tests/unit/linters/magic_numbers/test_python_magic_numbers.py -v

# Fix failures one by one until all pass
# Start with simplest tests, work up to complex ones
```

#### Step 9: Refactor Phase

Once tests pass:
```bash
# Run full linting
just lint-full
# Fix any violations

# Check complexity
poetry run xenon --max-absolute A src/linters/magic_numbers/
# Refactor functions that are B-grade or worse

# Ensure Pylint score
poetry run pylint src/linters/magic_numbers/
# Must be exactly 10.00/10
```

### Validation

```bash
# Step 1: All PR1 tests now pass (GREEN phase)
pytest tests/unit/linters/magic_numbers/ -v
# Expected: All tests pass

# Step 2: Implementation passes linting
just lint-full
# Expected: Exit code 0, Pylint 10.00/10, Xenon A-grade

# Step 3: No regressions in other linters
just test
# Expected: All tests pass
```

### Success Criteria
- [ ] All PR1 tests pass (TDD GREEN)
- [ ] Implementation follows BaseLintRule interface
- [ ] Code passes linting (Pylint 10.00/10)
- [ ] Code is A-grade complexity (Xenon)
- [ ] Convenience `lint()` function works
- [ ] File headers present (per FILE_HEADER_STANDARDS.md)
- [ ] No regressions in existing tests

### Commit Message
```
feat(linters): Implement Python magic numbers linter

TDD GREEN phase - all tests pass. Implementation includes:
- MagicNumberRule implementing BaseLintRule
- Python AST analysis for numeric literals
- Context detection (constants, range(), test files)
- Configurable allowed numbers
- Ignore directive support

Passes all quality gates:
- Pylint: 10.00/10
- Xenon: A-grade
- All tests passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR3: Test Suite for TypeScript Magic Numbers Detection

**Scope**: Write comprehensive failing tests for TypeScript magic number detection (TDD RED phase)

**Branch**: `feature/magic-numbers-typescript-tests`

**Complexity**: Medium

**Estimated Effort**: 2-3 hours

**Prerequisites**: PR2 merged (to avoid conflicts)

### Files to Create

```
tests/unit/linters/magic_numbers/
├── test_typescript_magic_numbers.py     # TypeScript detection tests
```

### Implementation Steps

#### Step 1: Review TypeScript Test Patterns
```bash
# Review existing TypeScript tests
cat tests/unit/linters/nesting/test_typescript_nesting.py
```

#### Step 2: Write TypeScript-Specific Tests

Test cases:
- Basic numeric literals in TypeScript
- Numbers in const assertions
- Numbers in enums (may be acceptable context)
- Numbers in type definitions
- Arrow functions vs regular functions
- Ignore directives in TypeScript comments

Example structure:
```python
class TestTypeScriptDetection:
    """Test TypeScript magic number detection."""

    def test_detects_number_in_const_variable(self):
        """Should detect magic number in const variable."""
        code = "const timeout = 3600;"
        # Parse and check violations

    def test_ignores_enum_values(self):
        """Should not flag numbers in enum definitions."""
        code = "enum Status { ACTIVE = 1, INACTIVE = 0 }"
        # Should be acceptable context

class TestTypeScriptIgnoreDirectives:
    """Test TypeScript ignore comments."""

    def test_respects_single_line_comment(self):
        """Should ignore with // thailint: ignore[magic-numbers]."""
        code = "const x = 3600; // thailint: ignore[magic-numbers]"
```

### Validation

```bash
# Tests should FAIL (RED phase)
pytest tests/unit/linters/magic_numbers/test_typescript_magic_numbers.py -v
# Expected: Failures (TypeScript implementation doesn't exist yet)

# Test code passes linting
just lint-full
# Expected: Exit code 0
```

### Success Criteria
- [ ] TypeScript test file created
- [ ] Tests cover TypeScript-specific contexts
- [ ] All tests FAIL (TDD RED)
- [ ] Test code passes linting

---

## PR4: TypeScript Magic Numbers Implementation

**Scope**: Implement TypeScript magic number detection using Tree-sitter (TDD GREEN phase)

**Branch**: `feature/magic-numbers-typescript-impl`

**Complexity**: High (Tree-sitter integration)

**Estimated Effort**: 5-6 hours

**Prerequisites**: PR3 merged

### Files to Create

```
src/linters/magic_numbers/
├── typescript_analyzer.py               # Tree-sitter TypeScript analysis
```

### Implementation Steps

#### Step 1: Review Tree-sitter Patterns
```bash
# Review existing TypeScript analyzer
cat src/linters/nesting/typescript_analyzer.py
```

#### Step 2: Implement TypeScript Analyzer

```python
class TypeScriptMagicNumberAnalyzer:
    """Analyzes TypeScript code for magic numbers using Tree-sitter."""

    def find_numeric_literals(self, tree):
        """Find all numeric literal nodes in TypeScript AST."""
        # Query: (number) @literal
        # Return list of (node, value) tuples
        pass

    def is_enum_context(self, node):
        """Check if number is in enum definition."""
        # Check parent nodes for enum_declaration
        pass
```

Tree-sitter node types:
- `number` - Numeric literal
- `enum_declaration` - Enum definition (acceptable context)

#### Step 3: Integrate with Main Linter

Update `src/linters/magic_numbers/linter.py`:
```python
def check(self, context: BaseLintContext) -> list[Violation]:
    """Check for magic number violations."""
    if context.language == "python":
        return self._check_python(context)
    if context.language in ("typescript", "javascript"):
        return self._check_typescript(context)
    return []

def _check_typescript(self, context, config):
    # Parse with Tree-sitter
    # Find numeric literals
    # Filter acceptable contexts
    # Build violations
    pass
```

#### Step 4: Iterative Green Phase

```bash
# Run TypeScript tests repeatedly
pytest tests/unit/linters/magic_numbers/test_typescript_magic_numbers.py -v

# Fix failures incrementally
```

#### Step 5: Refactor Phase

```bash
just lint-full
# Ensure Pylint 10.00/10, Xenon A-grade
```

### Validation

```bash
# All TypeScript tests pass
pytest tests/unit/linters/magic_numbers/test_typescript_magic_numbers.py -v
# Expected: All pass

# All Python tests still pass (no regression)
pytest tests/unit/linters/magic_numbers/test_python_magic_numbers.py -v
# Expected: All pass

# Linting passes
just lint-full
# Expected: Exit code 0
```

### Success Criteria
- [ ] TypeScript analyzer using Tree-sitter
- [ ] All PR3 tests pass
- [ ] No regressions in Python tests
- [ ] Code passes linting (Pylint 10.00/10, Xenon A-grade)

### Commit Message
```
feat(linters): Add TypeScript magic numbers detection

TDD GREEN phase - all TypeScript tests pass. Implementation includes:
- Tree-sitter based TypeScript analyzer
- Numeric literal detection in TS/JS
- Enum context detection (acceptable)
- Ignore directive support

Passes all quality gates.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR5: Self-Dogfooding: Lint Own Codebase

**Scope**: Run magic numbers linter on thai-lint codebase and fix all violations

**Branch**: `feature/magic-numbers-dogfooding`

**Complexity**: Medium (unknown number of violations)

**Estimated Effort**: 3-5 hours

**Prerequisites**: PR4 merged

### Implementation Steps

#### Step 1: Register Linter in Orchestrator

Update orchestrator to discover MagicNumberRule automatically.

#### Step 2: Run Linter on Entire Codebase

```bash
# Run magic numbers linter
python -m src.cli lint --rule magic-numbers src/

# Capture violations
python -m src.cli lint --rule magic-numbers src/ > magic-numbers-violations.txt
```

#### Step 3: Categorize Violations

Review violations and categorize:
1. **True violations** - Should be fixed (extract to constants)
2. **False positives** - Add to allowed_numbers or fix detection logic
3. **Acceptable in context** - Add ignore directive with justification

#### Step 4: Fix True Violations

Example fixes:
```python
# Before
def retry_connection():
    max_attempts = 5  # Magic number
    timeout = 30      # Magic number

# After
MAX_CONNECTION_ATTEMPTS = 5
DEFAULT_TIMEOUT_SECONDS = 30

def retry_connection():
    max_attempts = MAX_CONNECTION_ATTEMPTS
    timeout = DEFAULT_TIMEOUT_SECONDS
```

#### Step 5: Add Ignore Directives for Acceptable Cases

**CRITICAL**: Get user permission first!

Example:
```python
# Acceptable: Small array index
items[2]  # thailint: ignore[magic-numbers] - array index for third item
```

#### Step 6: Adjust Linter if Needed

If false positives discovered:
- Add to acceptable contexts
- Adjust default allowed_numbers
- Update tests to cover new cases

### Validation

```bash
# Step 1: No violations remain
python -m src.cli lint --rule magic-numbers src/
# Expected: Exit code 0 (no violations)

# Step 2: All tests still pass
just test
# Expected: All pass

# Step 3: Linting passes
just lint-full
# Expected: Exit code 0
```

### Success Criteria
- [ ] Magic numbers linter runs on thai-lint codebase
- [ ] All violations resolved (fixed or ignored with justification)
- [ ] No false positives remain (or detection logic adjusted)
- [ ] All tests pass
- [ ] Linting passes

### Commit Message
```
fix: Resolve magic number violations in codebase

Self-dogfooding the magic numbers linter revealed X violations:
- Y violations fixed by extracting constants
- Z violations suppressed with justification

All violations resolved. Linter validated on real codebase.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## PR6: Documentation and Integration

**Scope**: Complete documentation and finalize integration

**Branch**: `feature/magic-numbers-docs`

**Complexity**: Low

**Estimated Effort**: 2-3 hours

**Prerequisites**: PR5 merged

### Files to Create/Update

```
docs/linters/magic-numbers.md            # Linter documentation
examples/magic_numbers_usage.py          # Example usage
README.md                                 # Update with magic-numbers section
```

### Implementation Steps

#### Step 1: Write Linter Documentation

Create `docs/linters/magic-numbers.md`:
```markdown
# Magic Numbers Linter

## Overview
Detects magic numbers (unnamed numeric literals) in Python and TypeScript code.

## What are Magic Numbers?
...

## Configuration
...

## Examples
...

## Acceptable Contexts
...
```

#### Step 2: Create Example Usage

Create `examples/magic_numbers_usage.py`:
```python
"""Example usage of magic numbers linter."""
from src.linters.magic_numbers import lint

# Example 1: Basic usage
violations = lint("src/my_module.py")

# Example 2: Custom configuration
violations = lint("src/", config={
    "allowed_numbers": [0, 1, 2, 60, 3600],
    "max_small_integer": 10
})
```

#### Step 3: Update README

Add magic-numbers section to main README.md:
```markdown
### Magic Numbers Linter
Detects unnamed numeric literals that should be extracted to named constants.

```bash
python -m src.cli lint --rule magic-numbers src/
```
```

#### Step 4: Ensure Orchestrator Integration

Verify MagicNumberRule is discoverable:
```python
# In orchestrator
from src.linters.magic_numbers import MagicNumberRule

rules = [MagicNumberRule()]
```

#### Step 5: Add CLI Integration

Ensure magic-numbers appears in CLI help:
```bash
python -m src.cli lint --help
# Should show magic-numbers as available rule
```

### Validation

```bash
# Documentation exists and is readable
cat docs/linters/magic-numbers.md

# Examples run successfully
python examples/magic_numbers_usage.py

# CLI shows magic-numbers
python -m src.cli lint --help | grep magic-numbers

# All tests pass
just test

# Linting passes
just lint-full
```

### Success Criteria
- [ ] Documentation complete in `docs/linters/magic-numbers.md`
- [ ] Examples created and working
- [ ] README updated
- [ ] CLI integration verified
- [ ] Orchestrator integration verified
- [ ] All tests pass
- [ ] Linting passes

### Commit Message
```
docs(linters): Add magic numbers linter documentation and examples

Completes magic numbers linter feature:
- Comprehensive documentation
- Example usage scripts
- README updates
- CLI integration verified

Feature complete and production-ready.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Implementation Guidelines

### Code Standards
- **Follow BaseLintRule interface**: All rules must implement the interface
- **File headers required**: Per `.ai/docs/FILE_HEADER_STANDARDS.md`
- **Pylint score**: Exactly 10.00/10 (not 9.98, not 9.99)
- **Complexity**: ALL code must be A-grade (Xenon)
- **Type hints**: Required for all functions
- **Docstrings**: Google-style for all public functions

### Testing Requirements
- **TDD mandatory**: Tests before implementation
- **Coverage**: Minimum 80%, aim for 100% on new code
- **Test isolation**: Each test independent
- **Fixtures**: Use `mock_project_root` from `conftest.py`
- **Assertions**: Descriptive with helpful error messages

### Documentation Standards
- **File headers**: All files need headers (Purpose, Scope, Overview, etc.)
- **Inline comments**: Explain WHY not WHAT
- **Examples**: Provide working examples
- **README**: Keep main README updated

### Security Considerations
- **No secrets**: Never commit API keys or tokens
- **Input validation**: Validate file paths and config
- **Safe AST parsing**: Handle syntax errors gracefully

### Performance Targets
- **Fast tests**: Unit tests < 1s each
- **Efficient parsing**: Cache parsed ASTs when possible
- **Minimal memory**: Don't load entire codebases into memory

## Rollout Strategy

### Phase 1: Python Support (PR1-PR2)
- Focus on Python first (simpler)
- Validate TDD approach
- Establish patterns

### Phase 2: TypeScript Support (PR3-PR4)
- Add TypeScript using Tree-sitter
- Reuse patterns from Python

### Phase 3: Validation (PR5)
- Self-dogfooding validates real-world usefulness
- Discover edge cases
- Refine detection logic

### Phase 4: Production (PR6)
- Documentation for users
- Integration complete
- Ready for general use

## Success Metrics

### Launch Metrics
- [ ] All 6 PRs merged
- [ ] Zero failing tests
- [ ] Linting score 10.00/10
- [ ] Complexity A-grade
- [ ] Documentation complete

### Ongoing Metrics
- [ ] False positive rate < 5%
- [ ] User adoption in CI/CD
- [ ] Community feedback positive
