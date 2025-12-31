# Performance Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Performance Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from test suite through documentation

**Overview**: Comprehensive breakdown of the Performance Linter feature into 8 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: tree-sitter, existing thai-lint linter infrastructure

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the Performance Linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Test Suite - string-concat-loop (TDD)

**Scope**: Create comprehensive test suite for string concatenation in loop detection

**Branch**: `feature/perf-string-concat-tests`

**Files to Create**:
```
tests/unit/linters/performance/
├── __init__.py
├── test_string_concat_loop.py
└── conftest.py
```

### Step-by-Step Implementation

#### Step 1: Create test directory structure
```bash
mkdir -p tests/unit/linters/performance
touch tests/unit/linters/performance/__init__.py
touch tests/unit/linters/performance/conftest.py
```

#### Step 2: Create test file with test cases

**File**: `tests/unit/linters/performance/test_string_concat_loop.py`

```python
"""Tests for string concatenation in loop detection."""
import pytest

# Tests will import from src.linters.performance once implemented
# For now, tests define expected behavior


class TestPythonStringConcatDetection:
    """Test detection of string += in Python loops."""

    def test_detects_string_concat_in_for_loop(self):
        """Detect result += in for loop."""
        code = '''
def build_message(items):
    result = ""
    for item in items:
        result += str(item)
    return result
'''
        # Expected: 1 violation at line with result +=
        pass  # Implement when linter exists

    def test_detects_string_concat_in_while_loop(self):
        """Detect string += in while loop."""
        code = '''
def read_chunks(stream):
    content = ""
    while chunk := stream.read(1024):
        content += chunk
    return content
'''
        # Expected: 1 violation
        pass

    def test_detects_multiple_concats_in_loop(self):
        """Detect multiple string concats in same loop."""
        code = '''
def format_items(items):
    output = ""
    for item in items:
        output += item.name
        output += ": "
        output += item.value
        output += "\\n"
    return output
'''
        # Expected: 4 violations (or 1 per loop, configurable)
        pass

    def test_detects_nested_loop_concat(self):
        """Detect concat in nested loop (inner loop)."""
        code = '''
def build_table(rows):
    result = ""
    for row in rows:
        for cell in row:
            result += str(cell)
        result += "\\n"
    return result
'''
        # Expected: 2 violations (one per += in loops)
        pass

    def test_ignores_numeric_addition(self):
        """Do not flag numeric += (counters)."""
        code = '''
def count_items(items):
    total = 0
    for item in items:
        total += item.value
    return total
'''
        # Expected: 0 violations
        pass

    def test_ignores_list_extend(self):
        """Do not flag list +=."""
        code = '''
def collect_items(groups):
    result = []
    for group in groups:
        result += group.items
    return result
'''
        # Expected: 0 violations
        pass

    def test_ignores_concat_outside_loop(self):
        """Do not flag string += outside loops."""
        code = '''
def build_greeting(name, title):
    greeting = "Hello, "
    greeting += title
    greeting += " "
    greeting += name
    return greeting
'''
        # Expected: 0 violations (not in loop)
        pass

    def test_detects_fstring_concat_in_loop(self):
        """Detect f-string concat in loop."""
        code = '''
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item}</li>"
    return html
'''
        # Expected: 1 violation
        pass

    def test_suggests_join_alternative(self):
        """Violation message suggests join() as fix."""
        code = '''
def concat_names(names):
    result = ""
    for name in names:
        result += name
    return result
'''
        # Expected: violation message mentions "".join()
        pass


class TestTypeScriptStringConcatDetection:
    """Test detection of string += in TypeScript loops."""

    def test_detects_string_concat_in_for_loop(self):
        """Detect string += in TypeScript for loop."""
        code = '''
function buildMessage(items: string[]): string {
    let result = "";
    for (const item of items) {
        result += item;
    }
    return result;
}
'''
        # Expected: 1 violation
        pass

    def test_detects_string_concat_in_while_loop(self):
        """Detect string += in TypeScript while loop."""
        code = '''
function readAll(reader: Reader): string {
    let content = "";
    while (reader.hasMore()) {
        content += reader.read();
    }
    return content;
}
'''
        # Expected: 1 violation
        pass

    def test_detects_template_literal_concat(self):
        """Detect template literal concat in loop."""
        code = '''
function buildHtml(items: Item[]): string {
    let html = "";
    for (const item of items) {
        html += `<li>${item.name}</li>`;
    }
    return html;
}
'''
        # Expected: 1 violation
        pass

    def test_ignores_number_addition(self):
        """Do not flag numeric += in TypeScript."""
        code = '''
function sumValues(items: number[]): number {
    let total = 0;
    for (const item of items) {
        total += item;
    }
    return total;
}
'''
        # Expected: 0 violations
        pass

    def test_ignores_array_concat(self):
        """Do not flag array concat."""
        code = '''
function collectAll(groups: Item[][]): Item[] {
    let result: Item[] = [];
    for (const group of groups) {
        result = result.concat(group);
    }
    return result;
}
'''
        # Expected: 0 violations
        pass


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handles_empty_file(self):
        """Handle empty file gracefully."""
        code = ""
        # Expected: 0 violations, no error
        pass

    def test_handles_syntax_error(self):
        """Handle syntax errors gracefully."""
        code = "def broken(:"
        # Expected: syntax error reported, not crash
        pass

    def test_handles_nested_functions(self):
        """Detect concat in nested function's loop."""
        code = '''
def outer():
    def inner(items):
        result = ""
        for item in items:
            result += item
        return result
    return inner
'''
        # Expected: 1 violation in inner function
        pass

    def test_class_method_detection(self):
        """Detect concat in class method loop."""
        code = '''
class Builder:
    def build(self, items):
        result = ""
        for item in items:
            result += str(item)
        return result
'''
        # Expected: 1 violation
        pass
```

### Testing Requirements
- All tests should be marked with `pytest.mark.skip` initially
- Tests define expected behavior before implementation
- Run `pytest tests/unit/linters/performance/ -v` to see all test cases

### Success Criteria
- [ ] Test directory created
- [ ] 15+ test cases defined
- [ ] Tests cover Python and TypeScript
- [ ] Edge cases included
- [ ] Tests run (and skip) without error

---

## PR2: Implement string-concat-loop

**Scope**: Implement the string concatenation detector to make PR1 tests pass

**Branch**: `feature/perf-string-concat-impl`

**Files to Create**:
```
src/linters/performance/
├── __init__.py
├── config.py
├── string_concat_analyzer.py
├── python_analyzer.py
├── typescript_analyzer.py
└── linter.py
```

### Step-by-Step Implementation

#### Step 1: Create module structure
```bash
mkdir -p src/linters/performance
```

#### Step 2: Create config.py
```python
"""Configuration for performance linter."""
from dataclasses import dataclass, field


@dataclass
class PerformanceConfig:
    """Configuration for performance linting rules."""

    # String concat in loop
    string_concat_enabled: bool = True

    # Regex in loop
    regex_in_loop_enabled: bool = True

    # Report each += separately or one per loop
    report_each_concat: bool = False
```

#### Step 3: Create python_analyzer.py
- Use `ast` module to parse Python
- Walk AST looking for `For` and `While` nodes
- Within loops, find `AugAssign` with `Add` operator
- Check if target is string-typed (heuristics: name contains str/msg/html/text/result/output)
- Or check if value is string literal or f-string

#### Step 4: Create typescript_analyzer.py
- Use tree-sitter-typescript
- Find for/while loop nodes
- Within loops, find assignment expressions with +=
- Check if left side is string-typed

#### Step 5: Create linter.py
- Orchestrate Python and TypeScript analyzers
- Return list of Violation objects

#### Step 6: Update tests to import and run
- Remove `pytest.mark.skip` from tests
- Import actual linter functions
- Run tests, fix issues

### Testing Requirements
- All PR1 tests must pass
- Run on FastAPI codebase, expect violations at:
  - `fastapi/exceptions.py:197`
  - `fastapi/openapi/docs.py:136`

### Success Criteria
- [ ] All PR1 tests pass
- [ ] Detects FastAPI violations
- [ ] No false positives on numeric +=
- [ ] Python and TypeScript support

---

## PR3: Test Suite - regex-in-loop (TDD)

**Scope**: Create test suite for regex compilation in loop detection

**Branch**: `feature/perf-regex-tests`

**File**: `tests/unit/linters/performance/test_regex_in_loop.py`

### Test Cases to Implement

```python
class TestPythonRegexInLoopDetection:
    """Test detection of re.method() calls in loops."""

    def test_detects_re_match_in_loop(self):
        """Detect re.match() in for loop."""
        pass

    def test_detects_re_search_in_loop(self):
        """Detect re.search() in for loop."""
        pass

    def test_detects_re_sub_in_loop(self):
        """Detect re.sub() in for loop."""
        pass

    def test_detects_re_findall_in_loop(self):
        """Detect re.findall() in for loop."""
        pass

    def test_detects_re_split_in_loop(self):
        """Detect re.split() in for loop."""
        pass

    def test_ignores_compiled_pattern_in_loop(self):
        """Allow pattern.match() in loop (already compiled)."""
        pass

    def test_ignores_re_compile_in_loop(self):
        """Allow re.compile() in loop (intentional)."""
        pass

    def test_ignores_regex_outside_loop(self):
        """Allow re.match() outside loop."""
        pass

    def test_detects_in_while_loop(self):
        """Detect re.match() in while loop."""
        pass

    def test_suggests_compile_alternative(self):
        """Violation message suggests re.compile()."""
        pass
```

### Success Criteria
- [ ] 10+ test cases defined
- [ ] Covers all re module methods
- [ ] Tests compiled vs uncompiled patterns
- [ ] Edge cases included

---

## PR4: Implement regex-in-loop

**Scope**: Implement regex-in-loop detection to make PR3 tests pass

**Branch**: `feature/perf-regex-impl`

**Files to Modify**:
- `src/linters/performance/python_analyzer.py` (add regex detection)
- `src/linters/performance/linter.py` (integrate)

### Implementation Notes
- Only Python support needed (TypeScript regex is different)
- Detect calls to `re.match`, `re.search`, `re.sub`, `re.findall`, `re.split`
- Ignore `pattern.method()` where pattern is result of `re.compile()`
- This requires tracking variable assignments

### Success Criteria
- [ ] All PR3 tests pass
- [ ] Detects FastAPI violation at `scripts/deploy_docs_status.py:83`
- [ ] No false positives on compiled patterns

---

## PR5: CLI Integration

**Scope**: Add `thailint perf` command to CLI

**Branch**: `feature/perf-cli`

**Files to Modify**:
- `src/cli_main.py` - Add perf command
- Create `src/cli/performance.py` - Command implementation

### CLI Interface
```bash
# Basic usage
thailint perf src/

# Specific rules
thailint perf --rule string-concat src/
thailint perf --rule regex-loop src/

# With options
thailint perf --format json src/
thailint perf --config .thailint.yaml src/
```

### Success Criteria
- [ ] `thailint perf --help` works
- [ ] `thailint perf src/` runs both rules
- [ ] `--rule` flag filters to specific rule
- [ ] JSON output works
- [ ] Config file integration works

---

## PR6: Config Template Update

**Scope**: Add performance section to `thailint init-config`

**Branch**: `feature/perf-config-template`

**File to Modify**: `src/templates/thailint_config_template.yaml`

### Config Section to Add
```yaml
# ============================================================================
# PERFORMANCE LINTER
# ============================================================================
# Detects performance anti-patterns in loops
#
performance:
  enabled: true

  # String concatenation in loops (O(n²) pattern)
  string-concat-loop:
    enabled: true
    # Report each += separately, or one violation per loop
    # Default: false (one per loop)
    report_each_concat: false

  # Regex compilation in loops
  regex-in-loop:
    enabled: true

  # -------------------------------------------------------------------------
  # OPTIONAL: File patterns to ignore
  # -------------------------------------------------------------------------
  # ignore:
  #   - "tests/**"
  #   - "scripts/**"
```

### Success Criteria
- [ ] `thailint init-config` includes performance section
- [ ] Comments explain each option
- [ ] Default values are sensible

---

## PR7: Documentation

**Scope**: Create comprehensive documentation for PyPI

**Branch**: `feature/perf-docs`

**Files to Create/Modify**:
- Create `docs/performance-linter.md`
- Update `docs/index.md`
- Update `docs/cli-reference.md`

### Documentation Structure (performance-linter.md)
Follow the pattern in `docs/nesting-linter.md`:
1. Try It Now (quick start)
2. Overview (why it matters)
3. How It Works
4. Configuration
5. Usage (CLI, Library, Docker)
6. Violation Examples
7. Refactoring Patterns
8. Ignoring Violations
9. CI/CD Integration
10. Language Support
11. Troubleshooting
12. Best Practices
13. API Reference

### Success Criteria
- [ ] docs/performance-linter.md complete
- [ ] Follows existing doc format
- [ ] Includes real examples from FastAPI
- [ ] Refactoring patterns with before/after
- [ ] CI/CD integration examples

---

## PR8: Integration Tests

**Scope**: End-to-end validation of performance linter

**Branch**: `feature/perf-integration-tests`

**File**: `tests/integration/test_performance_linter.py`

### Test Cases
1. Full CLI run on test fixtures
2. Config file loading
3. SARIF output format
4. Exit codes
5. Multiple file scanning
6. Ignore patterns

### Success Criteria
- [ ] Integration tests pass
- [ ] CLI works end-to-end
- [ ] Config respected
- [ ] SARIF output valid

---

## Implementation Guidelines

### Code Standards
- Follow existing linter patterns (nesting, magic-numbers)
- Use dataclasses for config
- Type hints on all public functions
- Docstrings with Purpose/Scope/Overview format

### Testing Requirements
- TDD: tests before implementation
- Unit tests: 90%+ coverage for new code
- Integration tests: CLI and config
- Validation: run on FastAPI, expect known violations

### Documentation Standards
- Follow `docs/nesting-linter.md` format
- Include "Try It Now" section
- Real-world examples
- Refactoring patterns with before/after

### Security Considerations
- No execution of analyzed code
- Handle malformed files gracefully
- No file system writes except cache

### Performance Targets
- Single file: <100ms
- 100 files: <2s
- Incremental (cached): <500ms

## Rollout Strategy

### Phase 1: Core Implementation (PR1-PR4)
- TDD development
- Unit test coverage
- Both rules working

### Phase 2: Integration (PR5-PR6)
- CLI command
- Config template
- User-facing interface

### Phase 3: Polish (PR7-PR8)
- Documentation
- Integration tests
- PyPI ready

## Success Metrics

### Launch Metrics
- [ ] All 8 PRs merged
- [ ] 100% test pass rate
- [ ] FastAPI violations detected
- [ ] Zero false positives on thai-lint codebase

### Ongoing Metrics
- User adoption (pip downloads)
- Issue reports (false positives)
- Feature requests
