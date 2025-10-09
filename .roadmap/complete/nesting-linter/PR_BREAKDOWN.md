# Nesting Depth Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Nesting Depth Linter into manageable, atomic pull requests with strict TDD approach

**Scope**: Complete feature implementation from test suite through dogfooding and documentation

**Overview**: Comprehensive breakdown of the Nesting Depth Linter feature into 6 manageable, atomic pull requests. Each
    PR follows strict TDD methodology: PR1 writes ALL tests first with zero implementation, PR2 implements to pass tests,
    PR3 integrates with deployment modes, PRs 4-6 dogfood the linter on thai-lint itself and document findings. PRs are
    designed to be self-contained, testable, and maintain application functionality while incrementally building toward
    the complete feature with comprehensive refactoring examples.

**Dependencies**: Python 3.11+, Python ast module, @typescript-eslint/typescript-estree for TypeScript parsing, Poetry, pytest

**Exports**: PR implementation plans, file structures, testing strategies, TDD workflows, refactoring patterns, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking, reference implementation at /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py

**Implementation**: Strict TDD approach - Complete test suite first (PR1), then implementation (PR2), integration (PR3), followed by dogfooding and comprehensive refactoring (PR4-6)

---

## 🚀 PROGRESS TRACKER - MUST BE UPDATED AFTER EACH PR!

### ✅ Completed PRs
- ⬜ None yet - Planning phase just completed

### 🎯 NEXT PR TO IMPLEMENT
➡️ **START HERE: PR1** - Complete Test Suite (Pure TDD)

### 📋 Remaining PRs
- ⬜ PR1: Complete Test Suite (Pure TDD)
- ⬜ PR2: Core Implementation (Python + TypeScript)
- ⬜ PR3: Integration (CLI + Library + Docker)
- ⬜ PR4: Dogfooding Discovery
- ⬜ PR5: Dogfooding Fixes (Batch 1)
- ⬜ PR6: Dogfooding Fixes (Batch 2) + Documentation

**Progress**: 0% Complete (0/6 PRs)

---

## Overview
This document breaks down the Nesting Depth Linter feature into 6 manageable, atomic PRs. Each PR:
- **Follows strict TDD**: Tests written before implementation (PR1 = all tests, PR2 = all implementation)
- **Is self-contained and testable**: Can be reviewed and merged independently
- **Maintains working application**: No broken states
- **Builds incrementally**: Each PR adds value
- **Is revertible**: Can be rolled back without breaking functionality

---

# Phase 1: Test-First Development (PR1-PR2)

## PR1: Complete Test Suite (Pure TDD)

### Scope
Write comprehensive test suite for nesting depth linter with ZERO implementation code. All tests should fail appropriately (ModuleNotFoundError or ImportError).

### TDD Workflow
**Step 1: Write Tests First (NO implementation)**

### Files to Create

#### Test Directory Structure
```
tests/unit/linters/nesting/
├── __init__.py
├── test_python_nesting.py          # 15 tests - Python depth analysis
├── test_typescript_nesting.py      # 15 tests - TypeScript depth analysis
├── test_config_loading.py          # 8 tests - Configuration
├── test_violation_messages.py      # 6 tests - Error messages
├── test_ignore_directives.py       # 8 tests - Inline ignores
├── test_cli_interface.py           # 4 tests - CLI commands
├── test_library_api.py             # 4 tests - Programmatic API
└── test_edge_cases.py              # 8 tests - Edge cases
```

Total: **68 tests**

### Detailed Steps

#### Step 1: Review Reference Implementation
```bash
# Read the reference implementation to understand patterns
cat /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py
```

**Key patterns to extract**:
- DEFAULT_MAX_NESTING_DEPTH = 4
- Depth calculation starts at 1 for function body
- Nodes that increase depth: If, For, While, With, AsyncWith, Try, ExceptHandler, Match
- Helpful violation messages with refactoring suggestions

#### Step 2: Write `test_python_nesting.py`

```python
"""
Purpose: Test suite for Python nesting depth analysis
Scope: Python AST-based nesting depth calculation and violation detection
Overview: Comprehensive tests for Python code nesting depth analysis. Tests cover simple nesting
    (single if/for/while), complex nesting (multiple levels), various statement types (if, for,
    while, with, try, match), depth calculation accuracy, and violation detection. Verifies that
    depth counting starts at 1 for function body and increments for each nested block. Tests both
    passing cases (depth within limits) and violation cases (depth exceeds limits).
Dependencies: pytest, NestingDepthRule (to be implemented), Python ast module
Exports: 15 test cases covering Python nesting depth analysis
Interfaces: NestingDepthRule.check(context) -> list[Violation]
Implementation: Uses sample Python code strings, parses with ast, and verifies depth calculation
"""

import pytest
from pathlib import Path
from src.linters.nesting.linter import NestingDepthRule
from src.core.types import Violation


class TestSimplePythonNesting:
    """Test basic Python nesting depth detection."""

    def test_no_nesting_passes(self):
        """Function with no nesting should pass."""
        code = '''
def simple_function():
    x = 1
    y = 2
    return x + y
'''
        # Create context, run rule, expect no violations

    def test_single_if_within_limit(self):
        """Single if statement (depth 2) should pass with limit 4."""
        code = '''
def check_value(x):
    if x > 0:
        return True
    return False
'''
        # Depth: function=1, if=2 → passes with limit 4

    def test_triple_nesting_within_limit(self):
        """Triple nesting (depth 4) should pass with limit 4."""
        code = '''
def process_data(items):
    for item in items:
        if item.valid:
            for sub in item.children:
                print(sub)
'''
        # Depth: function=1, for=2, if=3, for=4 → passes with limit 4

    def test_quad_nesting_violates_default(self):
        """Quadruple nesting (depth 5) should violate default limit 4."""
        code = '''
def complex_logic(data):
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    print(child)
'''
        # Depth: function=1, for=2, if=3, for=4, if=5 → VIOLATION


class TestPythonStatementTypes:
    """Test various Python statement types that increase nesting."""

    def test_for_loop_nesting(self):
        """For loops should increase nesting depth."""
        # Test nested for loops

    def test_while_loop_nesting(self):
        """While loops should increase nesting depth."""
        # Test nested while loops

    def test_with_statement_nesting(self):
        """With statements should increase nesting depth."""
        # Test nested with statements

    def test_try_except_nesting(self):
        """Try/except blocks should increase nesting depth."""
        # Test nested try/except

    def test_match_statement_nesting(self):
        """Match statements (Python 3.10+) should increase nesting depth."""
        # Test nested match statements

    def test_mixed_statement_nesting(self):
        """Mixed statement types should all contribute to depth."""
        # Test if + for + while + with all nested


class TestPythonDepthCalculation:
    """Test accurate depth calculation for Python code."""

    def test_depth_starts_at_one_for_function_body(self):
        """Function body statements should start at depth 1."""
        # Verify depth tracking starts at 1, not 0

    def test_sibling_blocks_dont_increase_depth(self):
        """Sequential (non-nested) blocks should not increase depth."""
        code = '''
def multiple_ifs(x):
    if x > 0:
        print("positive")
    if x < 0:
        print("negative")
    if x == 0:
        print("zero")
'''
        # All three ifs are depth 2 (siblings), not cumulative

    def test_max_depth_tracking(self):
        """Should report maximum depth found, not current depth."""
        # Test with branching paths with different depths

    def test_async_function_nesting(self):
        """Async functions should track nesting same as sync."""
        # Test async def + await patterns


# Total: 15 tests in test_python_nesting.py
```

#### Step 3: Write `test_typescript_nesting.py`

```python
"""
Purpose: Test suite for TypeScript nesting depth analysis
Scope: TypeScript AST-based nesting depth calculation and violation detection
Overview: Comprehensive tests for TypeScript code nesting depth analysis. Tests cover simple
    nesting (single if/for/while), complex nesting (multiple levels), various statement types
    (if, for, while, switch, try), depth calculation accuracy, and violation detection. Verifies
    TypeScript-specific constructs like for-of loops and arrow functions. Tests both passing cases
    (depth within limits) and violation cases (depth exceeds limits).
Dependencies: pytest, NestingDepthRule, TypeScript parser (@typescript-eslint/typescript-estree)
Exports: 15 test cases covering TypeScript nesting depth analysis
Interfaces: NestingDepthRule.check(context) -> list[Violation]
Implementation: Uses sample TypeScript code strings, parses with typescript-estree, verifies depth
"""

import pytest
from pathlib import Path
from src.linters.nesting.linter import NestingDepthRule


class TestSimpleTypeScriptNesting:
    """Test basic TypeScript nesting depth detection."""

    def test_no_nesting_passes(self):
        """Function with no nesting should pass."""
        code = '''
function simpleFunction() {
    const x = 1;
    const y = 2;
    return x + y;
}
'''

    def test_single_if_within_limit(self):
        """Single if statement should pass with limit 4."""
        code = '''
function checkValue(x: number): boolean {
    if (x > 0) {
        return true;
    }
    return false;
}
'''

    def test_triple_nesting_within_limit(self):
        """Triple nesting should pass with limit 4."""
        code = '''
function processData(items: Item[]) {
    for (const item of items) {
        if (item.valid) {
            for (const sub of item.children) {
                console.log(sub);
            }
        }
    }
}
'''

    def test_quad_nesting_violates_default(self):
        """Quadruple nesting should violate default limit 4."""
        code = '''
function complexLogic(data: Data[]) {
    for (const item of data) {
        if (item.active) {
            for (const child of item.children) {
                if (child.valid) {
                    console.log(child);
                }
            }
        }
    }
}
'''


class TestTypeScriptStatementTypes:
    """Test various TypeScript statement types."""

    def test_for_of_loop_nesting(self):
        """For-of loops should increase nesting depth."""
        # Test nested for-of loops

    def test_switch_statement_nesting(self):
        """Switch statements should increase nesting depth."""
        # Test switch with nested blocks

    def test_try_catch_nesting(self):
        """Try/catch blocks should increase nesting depth."""
        # Test nested try/catch

    def test_arrow_function_nesting(self):
        """Arrow functions should track nesting correctly."""
        # Test arrow functions with nested blocks

    def test_while_loop_nesting(self):
        """While loops should increase nesting depth."""
        # Test nested while loops


class TestTypeScriptDepthCalculation:
    """Test accurate depth calculation for TypeScript."""

    def test_depth_starts_at_one_for_function_body(self):
        """Function body should start at depth 1."""

    def test_sibling_blocks_dont_increase_depth(self):
        """Sequential blocks should not increase depth."""

    def test_max_depth_tracking(self):
        """Should report maximum depth found."""

    def test_async_function_nesting(self):
        """Async functions should track nesting correctly."""

    def test_class_method_nesting(self):
        """Class methods should track nesting correctly."""

    def test_callback_nesting(self):
        """Callbacks should contribute to nesting depth."""

# Total: 15 tests in test_typescript_nesting.py
```

#### Step 4: Write `test_config_loading.py`

```python
"""
Purpose: Test configuration loading for nesting depth linter
Scope: YAML/JSON configuration parsing, max_nesting_depth validation
Overview: Tests configuration loading and validation for nesting depth linter. Verifies default
    max_nesting_depth (4), custom limits from config files (YAML and JSON), invalid config handling,
    and limit enforcement. Tests config merging (global vs per-file) and validation of limit ranges.
Dependencies: pytest, NestingDepthRule, configuration loader
Exports: 8 test cases for configuration loading
Interfaces: Config loading via .thailint.yaml or inline rules
Implementation: Uses temporary config files and verifies limit application
"""

import pytest
from src.linters.nesting.linter import NestingDepthRule
from src.linters.nesting.config import NestingConfig


class TestConfigLoading:
    """Test nesting depth configuration."""

    def test_default_max_depth_is_four(self):
        """Default max_nesting_depth should be 4."""
        config = NestingConfig()
        assert config.max_nesting_depth == 4

    def test_custom_max_depth_from_yaml(self):
        """Should load custom max_nesting_depth from YAML config."""
        yaml_content = '''
linters:
  nesting:
    max_nesting_depth: 3
'''
        # Load config, verify max_depth = 3

    def test_custom_max_depth_from_json(self):
        """Should load custom max_nesting_depth from JSON config."""
        json_content = '''
{
  "linters": {
    "nesting": {
      "max_nesting_depth": 5
    }
  }
}
'''
        # Load config, verify max_depth = 5

    def test_invalid_max_depth_rejects(self):
        """Should reject invalid max_nesting_depth values."""
        # Test negative numbers, zero, non-integers

    def test_max_depth_applies_to_violations(self):
        """Custom max_depth should affect violation detection."""
        # Code with depth 3 should pass with limit 4 but fail with limit 2

    def test_per_file_config_override(self):
        """Per-file config should override global config."""
        # Test directory-level config overriding repo-level

    def test_disabled_linter_skips_checks(self):
        """When enabled: false, should skip all checks."""
        config = '''
linters:
  nesting:
    enabled: false
'''

    def test_config_validation_errors(self):
        """Should provide helpful errors for malformed config."""
        # Test missing fields, wrong types, etc.

# Total: 8 tests in test_config_loading.py
```

#### Step 5: Write `test_violation_messages.py`

```python
"""
Purpose: Test violation message formatting and suggestions
Scope: Error message content, refactoring suggestions, context information
Overview: Tests that violation messages are helpful and actionable. Verifies messages include
    function name, max depth found, limit exceeded, line numbers, and specific refactoring
    suggestions. Tests suggestion quality (early returns, extract method, guard clauses).
Dependencies: pytest, NestingDepthRule, Violation dataclass
Exports: 6 test cases for violation messages
Interfaces: Violation.message, Violation.suggestion, Violation.context
Implementation: Parses violation messages and verifies helpful content
"""

import pytest
from src.linters.nesting.linter import NestingDepthRule


class TestViolationMessages:
    """Test helpful violation messages."""

    def test_message_includes_function_name(self):
        """Violation message should include function name."""
        # Verify format like "Function 'process_data' has excessive nesting"

    def test_message_includes_depth_info(self):
        """Message should include depth found and limit."""
        # Verify "depth of 5 exceeds limit of 4"

    def test_suggestion_recommends_refactoring(self):
        """Should provide actionable refactoring suggestions."""
        # Check for suggestions like:
        # - "Consider extracting nested logic to separate function"
        # - "Use early returns to reduce nesting"
        # - "Consider using guard clauses"

    def test_violation_includes_line_number(self):
        """Violation should include accurate line number."""
        # Verify line number of function or deepest nesting

    def test_violation_context_has_details(self):
        """Violation context should include metadata."""
        # Verify context contains: function_name, depth, max_allowed

    def test_multiple_violations_separate_messages(self):
        """Multiple functions with violations get separate messages."""
        # File with 3 functions, 2 violating → 2 violations

# Total: 6 tests in test_violation_messages.py
```

#### Step 6: Write `test_ignore_directives.py`

```python
"""
Purpose: Test inline ignore directives for nesting violations
Scope: Inline comments to suppress nesting depth warnings (# thailint: ignore nesting)
Overview: Tests inline ignore directive functionality. Verifies that violations can be suppressed
    with inline comments, supports multiple ignore formats (whole-line, end-of-line), respects
    rule-specific ignores (nesting vs other rules), and requires explicit rule names. Tests that
    ignores only apply to the specific line or function where they appear.
Dependencies: pytest, NestingDepthRule, ignore directive parser
Exports: 8 test cases for ignore directives
Interfaces: Inline comments: # thailint: ignore nesting or // thailint: ignore nesting
Implementation: Parses code with ignore comments, verifies violations suppressed
"""

import pytest
from src.linters.nesting.linter import NestingDepthRule


class TestIgnoreDirectives:
    """Test inline ignore directives."""

    def test_ignore_suppresses_violation(self):
        """# thailint: ignore nesting should suppress violation."""
        code = '''
def complex_function(data):  # thailint: ignore nesting
    for item in data:
        if item.active:
            for child in item.children:
                if child.valid:
                    if child.important:
                        process(child)
'''
        # Should NOT report violation due to ignore comment

    def test_ignore_all_suppresses_any_rule(self):
        """# thailint: ignore-all should suppress all rules."""
        # Test # thailint: ignore-all

    def test_ignore_wrong_rule_doesnt_suppress(self):
        """# thailint: ignore other-rule should NOT suppress nesting."""
        # Ignore comment for different rule shouldn't affect nesting

    def test_ignore_applies_to_function_scope(self):
        """Function-level ignore should apply to whole function."""
        # Test ignore on function definition line

    def test_typescript_ignore_syntax(self):
        """// thailint: ignore nesting should work in TypeScript."""
        # Test TypeScript comment syntax

    def test_block_ignore_start_end(self):
        """Block ignore with start/end markers."""
        # Test /* thailint: ignore-start nesting */ ... /* thailint: ignore-end */

    def test_ignore_requires_rule_name(self):
        """Generic # thailint: ignore without rule should fail gracefully."""
        # Ensure rule name is required

    def test_multiple_ignores_same_line(self):
        """# thailint: ignore nesting, file-placement should handle multiple."""
        # Test comma-separated rule ignores

# Total: 8 tests in test_ignore_directives.py
```

#### Step 7: Write `test_cli_interface.py`

```python
"""
Purpose: Test CLI interface for nesting depth linter
Scope: CLI command `thai lint nesting`, output formatting, exit codes
Overview: Tests CLI interface for nesting linter. Verifies `thai lint nesting <path>` command works,
    supports text and JSON output formats, provides proper exit codes (0 for pass, 1 for violations),
    handles custom config files, and displays helpful error messages. Tests both file and directory
    scanning modes.
Dependencies: pytest, Click CliRunner, CLI implementation
Exports: 4 test cases for CLI interface
Interfaces: thai lint nesting [OPTIONS] PATH
Implementation: Uses CliRunner to invoke commands and verify output
"""

import pytest
from click.testing import CliRunner
from src.cli import cli


class TestNestingCLI:
    """Test CLI interface for nesting linter."""

    def test_cli_command_exists(self):
        """thai lint nesting command should be available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['lint', 'nesting', '--help'])
        assert result.exit_code == 0
        assert 'nesting' in result.output.lower()

    def test_cli_reports_violations(self):
        """CLI should report violations with text output."""
        # Create temp file with nesting violation
        # Run: thai lint nesting <file>
        # Verify exit code = 1 and violation message in output

    def test_cli_json_output(self):
        """CLI should support JSON output format."""
        # Run: thai lint nesting --format json <file>
        # Verify JSON structure with violations array

    def test_cli_custom_config(self):
        """CLI should support --config flag."""
        # Run: thai lint nesting --config custom.yaml <file>
        # Verify custom max_depth applied

# Total: 4 tests in test_cli_interface.py
```

#### Step 8: Write `test_library_api.py`

```python
"""
Purpose: Test programmatic library API for nesting linter
Scope: Python API usage via Linter class
Overview: Tests library API for nesting linter. Verifies programmatic usage via Linter class,
    rule filtering (rules=['nesting']), violation objects with metadata, and integration with
    orchestrator. Tests both file and directory scanning modes from Python code.
Dependencies: pytest, Linter class from src.api
Exports: 4 test cases for library API
Interfaces: Linter(config_file=...).lint(path, rules=[...])
Implementation: Calls library API directly, verifies violation objects
"""

import pytest
from pathlib import Path
from src.api import Linter


class TestNestingLibraryAPI:
    """Test programmatic library API."""

    def test_library_api_detects_violations(self):
        """Linter.lint() should detect nesting violations."""
        linter = Linter()
        violations = linter.lint('test_file.py', rules=['nesting'])
        assert len(violations) > 0

    def test_library_api_rule_filtering(self):
        """rules=['nesting'] should only run nesting linter."""
        # Verify only nesting violations returned, not file-placement

    def test_library_api_violation_objects(self):
        """Violations should have proper metadata."""
        # Verify Violation.rule_id, message, line_number, context

    def test_library_api_custom_config(self):
        """Should accept custom config file."""
        linter = Linter(config_file='custom.yaml')
        # Verify custom max_depth applied

# Total: 4 tests in test_library_api.py
```

#### Step 9: Write `test_edge_cases.py`

```python
"""
Purpose: Test edge cases for nesting depth linter
Scope: Empty files, no functions, malformed code, extreme nesting
Overview: Tests edge cases and error handling. Verifies behavior with empty files, files with no
    functions, syntax errors, extremely deep nesting (10+ levels), empty function bodies, comments
    only, and mixed Python/TypeScript detection. Tests graceful failure modes and helpful errors.
Dependencies: pytest, NestingDepthRule
Exports: 8 test cases for edge cases
Interfaces: NestingDepthRule.check(context)
Implementation: Tests error conditions and boundary cases
"""

import pytest
from src.linters.nesting.linter import NestingDepthRule


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file_no_violations(self):
        """Empty file should produce no violations."""
        code = ''
        # Should return empty violations list

    def test_no_functions_no_violations(self):
        """File with no functions should produce no violations."""
        code = 'x = 1\ny = 2\nprint(x + y)'
        # Module-level code has no nesting depth to check

    def test_syntax_error_handled_gracefully(self):
        """Syntax errors should be handled gracefully."""
        code = 'def broken(\n  x = 1'  # Missing closing paren
        # Should not crash, maybe return parsing error violation

    def test_extremely_deep_nesting(self):
        """Extremely deep nesting (10+ levels) should be detected."""
        # Generate code with 10 nested ifs
        # Should report violation with depth 11

    def test_empty_function_body(self):
        """Empty function (only pass) should pass."""
        code = 'def empty():\n    pass'
        # Depth 1, no violations

    def test_comments_only_no_nesting(self):
        """Function with only comments should pass."""
        code = '''
def documented():
    # This function does nothing
    # But it has comments
    pass
'''

    def test_mixed_sync_async_functions(self):
        """Mix of sync and async functions should work."""
        # Test file with both def and async def

    def test_nested_functions(self):
        """Nested function definitions should track depth."""
        code = '''
def outer():
    def inner():
        if True:
            print("nested")
'''
        # Inner function depth should start fresh at 1

# Total: 8 tests in test_edge_cases.py
```

#### Step 10: Verify ALL Tests Fail

```bash
# Run tests - ALL should fail with ModuleNotFoundError
pytest tests/unit/linters/nesting/ -v

# Expected output:
# test_python_nesting.py::TestSimplePythonNesting::test_no_nesting_passes FAILED
# test_python_nesting.py::TestSimplePythonNesting::test_single_if_within_limit FAILED
# ... (68 failures total)
#
# ModuleNotFoundError: No module named 'src.linters.nesting'
```

### Completion Criteria
- ✅ All 68 tests written
- ✅ All 68 tests fail with ModuleNotFoundError or ImportError
- ✅ Test suite is comprehensive and well-documented
- ✅ Tests cover both Python and TypeScript
- ✅ Tests include edge cases and error handling
- ✅ PROGRESS_TRACKER.md updated with PR1 completion

### Success Metrics
- 68 tests written across 8 test files
- 100% test blueprint complete
- 0% implementation (as intended)
- Clear test names describing expected behavior
- Comprehensive coverage of nesting depth analysis

---

## PR2: Core Implementation (Python + TypeScript)

### Scope
Implement AST-based nesting depth analyzer to pass ALL PR1 tests (excluding CLI/integration tests which belong in PR3).

### Files to Create

```
src/linters/nesting/
├── __init__.py
├── linter.py                 # NestingDepthRule class
├── python_analyzer.py        # Python AST depth calculator
├── typescript_analyzer.py    # TypeScript AST depth calculator
└── config.py                 # NestingConfig dataclass
```

### Detailed Steps

#### Step 1: Review Reference Implementation Patterns

```bash
# Study the reference implementation depth calculation algorithm
cat /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py

# Key patterns:
# 1. Visitor pattern for AST traversal
# 2. nonlocal max_depth tracking
# 3. Depth increments for specific node types
# 4. Start at depth 1 for function body
```

#### Step 2: Implement `src/linters/nesting/config.py`

```python
"""
Purpose: Configuration schema for nesting depth linter
Scope: NestingConfig dataclass with max_nesting_depth setting
Overview: Defines configuration schema for nesting depth linter. Provides NestingConfig dataclass
    with max_nesting_depth field (default 4), validation logic, and config loading from YAML/JSON.
    Supports per-file and per-directory config overrides. Validates that max_depth is positive integer.
Dependencies: dataclasses, typing
Exports: NestingConfig dataclass
Interfaces: NestingConfig(max_nesting_depth: int = 4)
Implementation: Dataclass with validation and defaults
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class NestingConfig:
    """Configuration for nesting depth linter."""

    max_nesting_depth: int = 4  # Default from reference implementation
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_nesting_depth <= 0:
            raise ValueError(f"max_nesting_depth must be positive, got {self.max_nesting_depth}")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> 'NestingConfig':
        """Load configuration from dictionary."""
        return cls(
            max_nesting_depth=config.get('max_nesting_depth', 4),
            enabled=config.get('enabled', True)
        )
```

#### Step 3: Implement `src/linters/nesting/python_analyzer.py`

```python
"""
Purpose: Python AST-based nesting depth calculator
Scope: Python code nesting depth analysis using ast module
Overview: Analyzes Python code to calculate maximum nesting depth using AST traversal. Implements
    visitor pattern to walk AST, tracking current depth and maximum depth found. Increments depth
    for If, For, While, With, AsyncWith, Try, ExceptHandler, Match, and match_case nodes. Starts
    depth counting at 1 for function body. Returns maximum depth found and location information.
Dependencies: ast module for Python parsing
Exports: PythonNestingAnalyzer class with calculate_max_depth method
Interfaces: calculate_max_depth(func_node: ast.FunctionDef) -> tuple[int, int]
Implementation: AST visitor pattern with depth tracking, based on reference implementation
"""

import ast
from typing import Optional


class PythonNestingAnalyzer:
    """Calculates maximum nesting depth in Python functions."""

    def calculate_max_depth(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
        """Calculate maximum nesting depth in a function.

        Args:
            func_node: AST node for function definition

        Returns:
            Tuple of (max_depth, line_number_of_max_depth)
        """
        max_depth = 0
        max_depth_line = func_node.lineno

        def visit_node(node: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_depth, max_depth_line

            if current_depth > max_depth:
                max_depth = current_depth
                max_depth_line = getattr(node, 'lineno', func_node.lineno)

            # Nodes that increase nesting depth
            if isinstance(node, (
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.AsyncWith,
                ast.Try,
                ast.ExceptHandler,
                ast.Match,
                ast.match_case,
            )):
                current_depth += 1

            # Visit children
            for child in ast.iter_child_nodes(node):
                visit_node(child, current_depth)

        # Start at depth 1 for function body (matching reference implementation)
        for stmt in func_node.body:
            visit_node(stmt, 1)

        return max_depth, max_depth_line

    def find_all_functions(self, tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
        """Find all function definitions in AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
        return functions
```

#### Step 4: Implement `src/linters/nesting/typescript_analyzer.py`

```python
"""
Purpose: TypeScript AST-based nesting depth calculator
Scope: TypeScript code nesting depth analysis using typescript-estree parser
Overview: Analyzes TypeScript code to calculate maximum nesting depth using AST traversal.
    Implements visitor pattern to walk TypeScript AST, tracking current depth and maximum depth
    found. Increments depth for IfStatement, ForStatement, ForInStatement, ForOfStatement,
    WhileStatement, DoWhileStatement, TryStatement, CatchClause, and SwitchStatement nodes.
    Starts depth counting at 1 for function body. Returns maximum depth found and location.
Dependencies: subprocess for calling typescript-estree parser (Node.js)
Exports: TypeScriptNestingAnalyzer class with calculate_max_depth method
Interfaces: calculate_max_depth(func_node: dict) -> tuple[int, int]
Implementation: AST visitor pattern with depth tracking for TypeScript
"""

import json
import subprocess
from typing import Any


class TypeScriptNestingAnalyzer:
    """Calculates maximum nesting depth in TypeScript functions."""

    NESTING_NODE_TYPES = {
        'IfStatement',
        'ForStatement',
        'ForInStatement',
        'ForOfStatement',
        'WhileStatement',
        'DoWhileStatement',
        'TryStatement',
        'CatchClause',
        'SwitchStatement',
        'WithStatement',  # Deprecated but exists
    }

    def parse_typescript(self, code: str) -> dict[str, Any]:
        """Parse TypeScript code to AST using typescript-estree.

        Note: Requires Node.js and @typescript-eslint/typescript-estree
        For now, returns stub for testing - full implementation would call Node parser.
        """
        # TODO: Implement actual TypeScript parsing via Node.js
        # For testing, return empty AST
        return {'type': 'Program', 'body': []}

    def calculate_max_depth(self, func_node: dict[str, Any]) -> tuple[int, int]:
        """Calculate maximum nesting depth in a TypeScript function.

        Args:
            func_node: TypeScript function AST node (dict from typescript-estree)

        Returns:
            Tuple of (max_depth, line_number_of_max_depth)
        """
        max_depth = 0
        max_depth_line = func_node.get('loc', {}).get('start', {}).get('line', 0)

        def visit_node(node: dict[str, Any], current_depth: int = 0) -> None:
            nonlocal max_depth, max_depth_line

            if current_depth > max_depth:
                max_depth = current_depth
                max_depth_line = node.get('loc', {}).get('start', {}).get('line', 0)

            # Check if node increases nesting depth
            if node.get('type') in self.NESTING_NODE_TYPES:
                current_depth += 1

            # Visit children (recursively walk all dict/list values)
            for key, value in node.items():
                if isinstance(value, dict) and 'type' in value:
                    visit_node(value, current_depth)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and 'type' in item:
                            visit_node(item, current_depth)

        # Start at depth 1 for function body
        body = func_node.get('body', {})
        if body:
            visit_node(body, 1)

        return max_depth, max_depth_line
```

#### Step 5: Implement `src/linters/nesting/linter.py`

```python
"""
Purpose: Main nesting depth linter rule implementation
Scope: NestingDepthRule class implementing BaseLintRule interface
Overview: Implements nesting depth linter rule following BaseLintRule interface. Detects excessive
    nesting depth in Python and TypeScript code using AST analysis. Supports configurable
    max_nesting_depth limit (default 4). Provides helpful violation messages with refactoring
    suggestions. Integrates with orchestrator for automatic rule discovery. Handles both Python
    (using ast) and TypeScript (using typescript-estree) code analysis.
Dependencies: BaseLintRule, BaseLintContext, Violation, PythonNestingAnalyzer, TypeScriptNestingAnalyzer
Exports: NestingDepthRule class
Interfaces: NestingDepthRule.check(context) -> list[Violation]
Implementation: AST-based analysis with configurable limits and helpful error messages
"""

import ast
from pathlib import Path
from typing import Optional

from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation, Severity
from .config import NestingConfig
from .python_analyzer import PythonNestingAnalyzer
from .typescript_analyzer import TypeScriptNestingAnalyzer


class NestingDepthRule(BaseLintRule):
    """Detects excessive nesting depth in functions."""

    @property
    def rule_id(self) -> str:
        return "nesting.excessive-depth"

    @property
    def rule_name(self) -> str:
        return "Excessive Nesting Depth"

    @property
    def description(self) -> str:
        return "Functions should not have excessive nesting depth for better readability"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for excessive nesting depth violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if context.file_content is None:
            return []

        # Load configuration
        config = self._load_config(context)
        if not config.enabled:
            return []

        # Analyze based on language
        if context.language == 'python':
            return self._check_python(context, config)
        elif context.language in ('typescript', 'javascript'):
            return self._check_typescript(context, config)
        else:
            return []

    def _load_config(self, context: BaseLintContext) -> NestingConfig:
        """Load configuration from context metadata."""
        metadata = getattr(context, 'metadata', {})
        config_dict = metadata.get('linters', {}).get('nesting', {})
        return NestingConfig.from_dict(config_dict)

    def _check_python(self, context: BaseLintContext, config: NestingConfig) -> list[Violation]:
        """Check Python code for nesting violations."""
        try:
            tree = ast.parse(context.file_content or '')
        except SyntaxError as e:
            return [
                Violation(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    message=f"Syntax error: {e.msg}",
                    file_path=context.file_path,
                    line_number=e.lineno or 0,
                    severity=Severity.ERROR,
                    suggestion="Fix syntax errors before checking nesting depth",
                )
            ]

        analyzer = PythonNestingAnalyzer()
        functions = analyzer.find_all_functions(tree)
        violations = []

        for func in functions:
            max_depth, line = analyzer.calculate_max_depth(func)

            if max_depth > config.max_nesting_depth:
                violations.append(
                    Violation(
                        rule_id=self.rule_id,
                        rule_name=self.rule_name,
                        message=f"Function '{func.name}' has excessive nesting depth ({max_depth})",
                        file_path=context.file_path,
                        line_number=func.lineno,
                        severity=Severity.ERROR,
                        suggestion=(
                            f"Maximum nesting depth of {max_depth} exceeds limit of {config.max_nesting_depth}. "
                            "Consider extracting nested logic to separate functions, using early returns, "
                            "or applying guard clauses to reduce nesting."
                        ),
                        context={
                            'function_name': func.name,
                            'depth': max_depth,
                            'max_allowed': config.max_nesting_depth,
                            'deepest_line': line,
                        }
                    )
                )

        return violations

    def _check_typescript(self, context: BaseLintContext, config: NestingConfig) -> list[Violation]:
        """Check TypeScript code for nesting violations."""
        analyzer = TypeScriptNestingAnalyzer()

        # Parse TypeScript code
        ast_tree = analyzer.parse_typescript(context.file_content or '')

        # Find function nodes and check depth
        # TODO: Implement TypeScript function finding and depth checking
        # For now, return empty list (tests will fail until implemented)

        return []
```

#### Step 6: Run Tests and Verify Pass Rate

```bash
# Run all nesting linter tests
pytest tests/unit/linters/nesting/ -v

# Expected results:
# - 60+/68 tests passing (all Python tests, most config tests)
# - ~8 tests failing (CLI interface, some integration tests)
# - Test failures are expected for PR3 scope (CLI/integration)

# Check coverage
pytest tests/unit/linters/nesting/ --cov=src/linters/nesting --cov-report=term-missing

# Expected coverage: >85% on src/linters/nesting/
```

### Completion Criteria
- ✅ 60+/68 tests pass (remaining 8 are CLI/integration for PR3)
- ✅ Python nesting depth analysis working correctly
- ✅ TypeScript nesting depth analysis working correctly (or stubbed with TODO)
- ✅ Configurable max_nesting_depth with validation
- ✅ Helpful violation messages with refactoring suggestions
- ✅ Test coverage >85% on linter modules
- ✅ PROGRESS_TRACKER.md updated with PR2 completion

### Success Metrics
- At least 60/68 tests passing
- Python depth calculation matches reference implementation
- Configuration loading functional
- Violation messages include context and suggestions
- No regressions in existing tests

---

## PR3: Integration (CLI + Library + Docker)

### Scope
Integrate nesting depth linter with orchestrator, CLI, Library API, and Docker deployment modes.

### Files to Modify

```
src/cli.py                                    # Add `thai lint nesting` command
src/__init__.py                               # Export nesting_lint convenience function
tests/unit/integration/test_nesting_integration.py  # New integration tests
```

### Detailed Steps

#### Step 1: Verify Auto-Discovery

The orchestrator should automatically discover NestingDepthRule via the plugin registry. Verify this works:

```python
# Test auto-discovery
from src.orchestrator.core import Orchestrator

orchestrator = Orchestrator()
rules = orchestrator.registry.get_all_rules()

# Should include NestingDepthRule
nesting_rules = [r for r in rules if 'nesting' in r.rule_id]
assert len(nesting_rules) > 0
```

#### Step 2: Add CLI Command

Modify `src/cli.py` to add `thai lint nesting` subcommand:

```python
@lint.command('nesting')
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True), help='Custom config file')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
@click.option('--max-depth', type=int, help='Override max nesting depth')
def lint_nesting(path: str, config: Optional[str], format: str, max_depth: Optional[int]) -> None:
    """Check for excessive nesting depth in code.

    Analyzes Python and TypeScript files for deeply nested code structures
    (if/for/while/try statements) and reports violations.

    Examples:
        thai lint nesting src/
        thai lint nesting --max-depth 3 src/module.py
        thai lint nesting --format json src/
    """
    from pathlib import Path
    from src.orchestrator.core import Orchestrator

    # Load orchestrator with config
    orchestrator = Orchestrator(config_file=config)

    # Override max_depth if provided
    if max_depth:
        # TODO: Apply max_depth override to config
        pass

    # Run linting
    path_obj = Path(path)
    if path_obj.is_file():
        violations = orchestrator.lint_file(path_obj, rules=['nesting.excessive-depth'])
    else:
        violations = orchestrator.lint_directory(path_obj, rules=['nesting.excessive-depth'])

    # Format output
    if format == 'json':
        import json
        output = json.dumps([v.__dict__ for v in violations], indent=2)
        click.echo(output)
    else:
        for v in violations:
            click.echo(f"{v.file_path}:{v.line_number}: {v.message}")
            if v.suggestion:
                click.echo(f"  Suggestion: {v.suggestion}")

    # Exit with appropriate code
    sys.exit(1 if violations else 0)
```

#### Step 3: Export Library API

Modify `src/__init__.py`:

```python
# Add to exports
from src.linters.nesting.linter import NestingDepthRule

__all__ = [
    'Linter',
    'Orchestrator',
    'FilePlacementRule',
    'NestingDepthRule',  # New export
    # ... other exports
]

# Convenience function
def nesting_lint(path, config_file=None, max_depth=4):
    """Convenience function for nesting depth linting.

    Args:
        path: File or directory to lint
        config_file: Optional config file path
        max_depth: Maximum allowed nesting depth (default 4)

    Returns:
        List of Violation objects
    """
    linter = Linter(config_file=config_file)
    return linter.lint(path, rules=['nesting'])
```

#### Step 4: Write Integration Tests

Create `tests/unit/integration/test_nesting_integration.py`:

```python
"""
Purpose: Integration tests for nesting depth linter with orchestrator
Scope: E2E integration testing with CLI, Library API, and orchestrator
Overview: Tests full integration of nesting linter with all deployment modes. Verifies orchestrator
    auto-discovers nesting rule, CLI command works, Library API works, and Docker deployment works.
    Tests config loading, rule filtering, and violation reporting across all interfaces.
Dependencies: pytest, Orchestrator, Linter, CliRunner
Exports: 8 integration test cases
Interfaces: Full stack from CLI/API down to rule execution
Implementation: E2E testing with temp files and realistic scenarios
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

from src.orchestrator.core import Orchestrator
from src.api import Linter
from src.cli import cli


class TestNestingIntegration:
    """E2E integration tests for nesting linter."""

    def test_orchestrator_discovers_nesting_rule(self):
        """Orchestrator should auto-discover NestingDepthRule."""
        orch = Orchestrator()
        rules = orch.registry.get_all_rules()
        nesting_rules = [r for r in rules if 'nesting' in r.rule_id]
        assert len(nesting_rules) > 0

    def test_orchestrator_lints_python_file(self, tmp_path):
        """Orchestrator should lint Python file with nesting rule."""
        # Create Python file with nesting violation
        # Run orchestrator.lint_file()
        # Verify violations returned

    def test_cli_command_works(self, tmp_path):
        """CLI command `thai lint nesting` should work."""
        # Create temp Python file with violation
        # Run CLI via CliRunner
        # Verify exit code and output

    def test_library_api_works(self, tmp_path):
        """Library API should work for nesting linter."""
        # Create temp file with violation
        # Use Linter().lint(path, rules=['nesting'])
        # Verify violations returned

    def test_custom_max_depth_config(self, tmp_path):
        """Custom max_depth in config should be respected."""
        # Create config with max_depth=2
        # Lint file with depth=3
        # Verify violation reported

    def test_ignore_directive_works(self, tmp_path):
        """Inline ignore directives should suppress violations."""
        # Create file with violation + ignore comment
        # Verify no violation reported

    def test_multiple_files_in_directory(self, tmp_path):
        """Should lint all files in directory."""
        # Create directory with multiple Python files
        # Some with violations, some without
        # Verify correct violation count

    def test_mixed_python_typescript(self, tmp_path):
        """Should handle mixed Python and TypeScript files."""
        # Create directory with both .py and .ts files
        # Verify both get linted correctly

# Total: 8 integration tests
```

#### Step 5: Test Docker Deployment

Verify nesting linter works in Docker:

```bash
# Build Docker image
docker build -t thailint/thailint .

# Test nesting linter in container
docker run --rm -v $(pwd):/workspace thailint/thailint lint nesting /workspace/src/

# Verify output and exit code
```

### Completion Criteria
- ✅ All 68/68 tests pass (100%)
- ✅ CLI command `thai lint nesting` works
- ✅ Library API `linter.lint(rules=['nesting'])` works
- ✅ Docker deployment works
- ✅ Orchestrator auto-discovers NestingDepthRule
- ✅ Integration tests pass (8/8)
- ✅ Test coverage >90% overall
- ✅ PROGRESS_TRACKER.md updated with PR3 completion

### Success Metrics
- All deployment modes functional (CLI, Library, Docker)
- Zero test failures
- Integration tests demonstrate E2E functionality
- Documentation updated with usage examples

---

# Phase 2: Dogfooding & Quality (PR4-PR6)

## PR4: Dogfooding Discovery

### Scope
Run nesting depth linter on thai-lint codebase and catalog ALL violations found. This is pure discovery - NO fixes in this PR.

### Detailed Steps

#### Step 1: Run Nesting Linter on Codebase

```bash
# Run nesting linter on entire src/ directory
thai lint nesting src/ > nesting-violations.txt

# Alternative: Use library API
python -c "
from src import Linter
linter = Linter()
violations = linter.lint('src/', rules=['nesting'])
for v in violations:
    print(f'{v.file_path}:{v.line_number} {v.message}')
"
```

#### Step 2: Catalog Violations

Create `.roadmap/planning/nesting-linter/VIOLATIONS.md`:

```markdown
# Nesting Depth Violations in thai-lint

**Date Discovered**: 2025-XX-XX
**Total Violations**: XX
**Max Allowed Depth**: 4

## Summary
- Total violations: XX
- Files affected: XX
- Functions affected: XX

## Violations by Severity

### Easy Refactors (Early Returns) - XX violations
Simple cases where early returns or guard clauses will fix the issue.

1. **src/cli.py:45** - Function `load_config` (depth 5)
   - Current structure: if → if → if → if → if
   - Refactor: Use early returns for validation

2. **src/orchestrator/core.py:120** - Function `lint_file` (depth 5)
   - Current structure: try → if → for → if → if
   - Refactor: Extract nested for loop to helper method

### Medium Refactors (Extract Method) - XX violations
Cases requiring extraction of nested logic to separate functions.

1. **src/linters/file_placement/linter.py:78** - Function `check_patterns` (depth 6)
   - Current structure: for → if → for → if → for → if
   - Refactor: Extract inner loops to _check_pattern_match() helper

### Hard Refactors (Redesign) - XX violations
Complex cases requiring significant restructuring.

1. **src/api.py:200** - Function `complex_operation` (depth 7)
   - Current structure: Complex nested if/for/try blocks
   - Refactor: Consider state machine or strategy pattern

## Violations by File

### src/cli.py (X violations)
- Line 45: load_config (depth 5)
- Line 123: validate_input (depth 5)

### src/orchestrator/core.py (X violations)
- Line 120: lint_file (depth 5)

[... continue for all files ...]

## Refactoring Plan

### PR5 Targets (Easy + Medium)
Focus on violations that can be fixed with:
- Early returns and guard clauses
- Simple method extraction
- Estimated violations: ~XX/XX (~50%)

### PR6 Targets (Remaining + Hard)
Focus on:
- Complex refactorings
- Remaining medium cases
- Any violations requiring inline ignores with justification
- Estimated violations: ~XX/XX (~50%)
```

#### Step 3: Categorize and Plan

Group violations by:
1. **Easy**: Early returns, guard clauses (target for PR5)
2. **Medium**: Extract method, simple restructuring (split PR5/PR6)
3. **Hard**: Complex redesign, may require inline ignores (target for PR6)

### Completion Criteria
- ✅ Complete catalog of all violations in VIOLATIONS.md
- ✅ Violations categorized by difficulty
- ✅ Refactoring plan for PR5/PR6 split documented
- ✅ Estimated 20-50 violations found
- ✅ No code changes in this PR (discovery only)
- ✅ PROGRESS_TRACKER.md updated with PR4 completion

### Success Metrics
- Comprehensive violation catalog
- Clear categorization for planning
- Realistic split for PR5/PR6
- Understanding of refactoring scope

---

## PR5: Dogfooding Fixes (Batch 1)

### Scope
Fix approximately 50% of nesting violations using straightforward refactoring patterns.

### Refactoring Patterns to Apply

#### Pattern 1: Early Returns
```python
# BEFORE (depth 5)
def validate_input(data):
    if data is not None:
        if isinstance(data, dict):
            if 'key' in data:
                if data['key'] is not None:
                    if data['key'] > 0:
                        return True
    return False

# AFTER (depth 2)
def validate_input(data):
    if data is None:
        return False
    if not isinstance(data, dict):
        return False
    if 'key' not in data:
        return False
    if data['key'] is None:
        return False
    if data['key'] <= 0:
        return False
    return True
```

#### Pattern 2: Extract Method
```python
# BEFORE (depth 6)
def process_items(items):
    for item in items:
        if item.valid:
            for child in item.children:
                if child.active:
                    for sub in child.subs:
                        if sub.enabled:
                            print(sub)

# AFTER (depth 3)
def process_items(items):
    for item in items:
        if item.valid:
            _process_children(item.children)

def _process_children(children):
    for child in children:
        if child.active:
            _process_subs(child.subs)

def _process_subs(subs):
    for sub in subs:
        if sub.enabled:
            print(sub)
```

#### Pattern 3: Guard Clauses
```python
# BEFORE (depth 5)
def handle_request(request):
    if request is not None:
        if request.valid:
            if request.user is not None:
                if request.user.authenticated:
                    process(request)

# AFTER (depth 2)
def handle_request(request):
    if request is None:
        return
    if not request.valid:
        return
    if request.user is None:
        return
    if not request.user.authenticated:
        return
    process(request)
```

### Detailed Steps

#### Step 1: Review VIOLATIONS.md

Focus on "Easy" and first half of "Medium" violations.

#### Step 2: Fix Violations Systematically

For each violation:
1. Read the function and understand its logic
2. Choose appropriate refactoring pattern
3. Apply refactoring
4. Run tests: `just test` (verify no breakage)
5. Run linter: `thai lint nesting <file>` (verify violation fixed)
6. Commit with message describing refactoring

#### Step 3: Verify No Functionality Broken

```bash
# Run full test suite after all refactorings
just test

# Expected: All tests pass (exit code 0)

# Run full linting
just lint-full

# Expected: No new violations introduced
```

#### Step 4: Update VIOLATIONS.md

Mark fixed violations as complete, update remaining count.

### Completion Criteria
- ✅ ~50% of violations fixed
- ✅ All tests still pass (just test exits with code 0)
- ✅ just lint-full still passes
- ✅ No functionality broken
- ✅ VIOLATIONS.md updated with progress
- ✅ Clear commit messages describing refactorings
- ✅ PROGRESS_TRACKER.md updated with PR5 completion

### Success Metrics
- Violation count reduced by ~50%
- Zero test failures
- Zero functionality regressions
- Clean refactoring patterns applied

---

## PR6: Dogfooding Fixes (Batch 2) + Documentation

### Scope
Fix remaining nesting violations (or acknowledge with inline ignores) and complete comprehensive documentation.

### Detailed Steps

#### Step 1: Fix Remaining Violations

Focus on:
- Remaining "Medium" violations
- "Hard" violations (may require complex refactoring)
- Violations that legitimately need to stay deep (use inline ignores)

#### Step 2: Use Inline Ignores When Appropriate

```python
# Example: Complex CLI argument parsing may legitimately be deep
def parse_args(args):  # thailint: ignore nesting
    # Complex nested logic for CLI parsing
    # Justification: CLI arg parsing inherently has many nested conditions
    # for handling different flag combinations
    if args.verbose:
        if args.format == 'json':
            # ... many levels ...
```

**Rule**: Every inline ignore MUST have a justification comment explaining why the nesting is necessary.

#### Step 3: Verify Zero Violations

```bash
# Run nesting linter on full codebase
thai lint nesting src/

# Expected output: Zero violations (or all explicitly ignored)

# Verify exit code
echo $?  # Should be 0
```

#### Step 4: Create Comprehensive Documentation

##### Update README.md

Add nesting linter section:

```markdown
## Nesting Depth Linter

Detects excessive code nesting (if/for/while/try statements) that harms readability.

### Usage

```bash
# Lint entire project
thai lint nesting src/

# Lint specific file
thai lint nesting src/module.py

# Custom nesting depth limit
thai lint nesting --max-depth 3 src/

# JSON output
thai lint nesting --format json src/
```

### Configuration

```yaml
# .thailint.yaml
linters:
  nesting:
    enabled: true
    max_nesting_depth: 4  # Default
```

### Refactoring Patterns

When the linter finds violations, consider these patterns:

**Early Returns**:
```python
# Instead of deeply nested ifs, use early returns
def validate(data):
    if data is None:
        return False
    if not data.valid:
        return False
    return True
```

[... more patterns ...]
```

##### Create docs/nesting-linter.md

```markdown
# Nesting Depth Linter

**Purpose**: Comprehensive guide to nesting depth linter usage, configuration, and refactoring patterns

**Scope**: Nesting depth analysis for Python and TypeScript code

**Overview**: Complete documentation for the nesting depth linter. Explains how excessive nesting
    harms code readability and maintainability, provides configuration options, demonstrates
    refactoring patterns with before/after examples, and documents inline ignore directives.
    Includes real-world examples from thai-lint refactoring experience.

## Overview

The nesting depth linter detects excessive code nesting...

## Configuration

[Detailed config options]

## Supported Languages

### Python
- Tracks: if, for, while, with, try, match statements
- Uses Python ast module for accurate parsing

### TypeScript
- Tracks: if, for, while, switch, try statements
- Uses @typescript-eslint/typescript-estree parser

## Refactoring Patterns

### Pattern 1: Early Returns
[Detailed examples with before/after code]

### Pattern 2: Extract Method
[Detailed examples]

### Pattern 3: Guard Clauses
[Detailed examples]

### Pattern 4: Functional Approaches
[Detailed examples using map/filter/reduce]

## Real-World Examples

[Examples from thai-lint refactoring]

## Inline Ignores

[How to use # thailint: ignore nesting]

## CI/CD Integration

[How to enforce in CI/CD pipelines]
```

##### Create Configuration Example

Create `examples/nesting-config-example.yaml`:

```yaml
# Example: Nesting depth linter configuration
linters:
  nesting:
    enabled: true
    max_nesting_depth: 4  # Default limit

    # Common overrides:
    # max_nesting_depth: 3  # Stricter limit
    # max_nesting_depth: 5  # More lenient for complex domains
```

#### Step 5: Update CHANGELOG.md

```markdown
## [0.2.0] - 2025-XX-XX

### Added
- **Nesting Depth Linter**: New linter for detecting excessive code nesting
  - Supports Python and TypeScript
  - Configurable max_nesting_depth (default 4)
  - Helpful refactoring suggestions
  - CLI: `thai lint nesting <path>`
  - Library API: `linter.lint(path, rules=['nesting'])`
  - Docker support included

### Changed
- Refactored thai-lint codebase to meet nesting depth standards
  - Applied early return patterns
  - Extracted nested logic to helper methods
  - Used guard clauses to flatten control flow
  - Zero nesting violations in production code

### Documentation
- Added comprehensive nesting linter guide (docs/nesting-linter.md)
- Updated README with nesting linter examples
- Documented refactoring patterns from dogfooding experience
```

### Completion Criteria
- ✅ Zero nesting violations (or all explicitly ignored with justification)
- ✅ All tests pass (just test exits with code 0)
- ✅ just lint-full exits with code 0
- ✅ README.md updated with nesting linter section
- ✅ docs/nesting-linter.md created with comprehensive guide
- ✅ examples/nesting-config-example.yaml created
- ✅ CHANGELOG.md updated with v0.2.0 entry
- ✅ All inline ignores have justification comments
- ✅ PROGRESS_TRACKER.md updated with PR6 completion

### Success Metrics
- Codebase is clean (zero violations)
- Comprehensive documentation
- Real-world refactoring examples documented
- Quality gate: just lint-full passes

---

## 🚀 Overall Success Criteria

The nesting depth linter feature is complete when:

- [ ] All 6 PRs merged to main
- [ ] 68/68 tests passing
- [ ] Both Python and TypeScript support functional
- [ ] All deployment modes working (CLI, Library, Docker)
- [ ] thai-lint codebase has zero nesting violations
- [ ] just lint-full exits with code 0
- [ ] Comprehensive documentation complete
- [ ] Real-world refactoring patterns documented
- [ ] CHANGELOG.md updated with v0.2.0

---

## 📝 Notes for AI Agents

### Key Principles
1. **TDD First**: PR1 writes ALL tests, PR2 implements to pass tests
2. **Quality Focus**: PRs 4-6 ensure the linter finds real issues
3. **Dogfooding**: Using the linter on itself validates its value
4. **Documentation**: Document refactoring patterns learned during dogfooding

### Common Mistakes to Avoid
- ❌ Implementing before writing tests (PR1 must be pure TDD)
- ❌ Skipping dogfooding (PRs 4-6 are critical for quality)
- ❌ Using inline ignores without justification
- ❌ Breaking functionality during refactoring
- ❌ Incomplete documentation

### Resources
- **Reference**: /home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/style/nesting_rules.py
- **Pattern Example**: src/linters/file_placement/ (existing linter structure)
- **Test Patterns**: tests/unit/linters/file_placement/ (test structure examples)
