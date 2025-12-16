# Method Should Be Property Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Method Should Be Property Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from test suite through documentation and publishing

**Overview**: Comprehensive breakdown of the Method Should Be Property Linter into 5 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: BaseLintRule interface, Python AST, pytest, Click CLI framework

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with TDD methodology and comprehensive testing validation

---

## Overview
This document breaks down the Method Should Be Property Linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Test Suite for Python Method Detection

### Scope
Write comprehensive test suite for Python method-should-be-property detection using TDD approach. All tests should fail initially (red phase).

### Files to Create

```
tests/unit/linters/method_property/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_basic_detection.py        # Core detection tests
├── test_exclusion_rules.py        # Tests for what NOT to flag
├── test_configuration.py          # Config loading and defaults
├── test_ignore_directives.py      # Inline ignore support
├── test_edge_cases.py             # Edge cases and error handling
└── test_violation_details.py      # Message and suggestion validation
```

### Test Categories and Coverage

#### 1. Basic Detection Tests (`test_basic_detection.py`)
```python
class TestSimpleAttributeReturn:
    """Tests for methods returning self._attribute or self.attribute"""
    def test_detects_return_private_attribute(self):
        # def name(self): return self._name
    def test_detects_return_public_attribute(self):
        # def value(self): return self.value
    def test_detects_return_nested_attribute(self):
        # def config(self): return self._settings.config

class TestGetPrefixMethods:
    """Tests for get_* prefixed methods (Java-style)"""
    def test_detects_get_prefix_simple(self):
        # def get_name(self): return self._name
    def test_detects_get_prefix_computed(self):
        # def get_total(self): return self._a + self._b

class TestSimpleComputation:
    """Tests for simple computed property candidates"""
    def test_detects_arithmetic_computation(self):
        # def area(self): return self._w * self._h
    def test_detects_string_formatting(self):
        # def full_name(self): return f"{self._first} {self._last}"
    def test_detects_boolean_expression(self):
        # def is_valid(self): return self._value > 0
```

#### 2. Exclusion Rules Tests (`test_exclusion_rules.py`)
```python
class TestParameterExclusions:
    """Methods with parameters should NOT be flagged"""
    def test_ignores_method_with_required_param(self):
        # def get_item(self, index): return self._items[index]
    def test_ignores_method_with_default_param(self):
        # def get_value(self, default=None): ...

class TestSideEffectExclusions:
    """Methods with side effects should NOT be flagged"""
    def test_ignores_method_with_assignment(self):
        # def value(self): self._cached = True; return self._value
    def test_ignores_method_with_augmented_assignment(self):
        # def count(self): self._count += 1; return self._count
    def test_ignores_method_with_loop(self):
        # def items(self): for i in self._data: yield i
    def test_ignores_method_with_try_except(self):
        # def safe_value(self): try: return self._v except: return None

class TestDecoratorExclusions:
    """Decorated methods should NOT be flagged"""
    def test_ignores_staticmethod(self):
    def test_ignores_classmethod(self):
    def test_ignores_abstractmethod(self):
    def test_ignores_property_already(self):
    def test_ignores_cached_property(self):

class TestComplexBodyExclusions:
    """Complex method bodies should NOT be flagged"""
    def test_ignores_body_over_3_statements(self):
    def test_ignores_method_with_external_call(self):
    def test_ignores_method_with_await(self):

class TestSpecialCases:
    """Special cases that should NOT be flagged"""
    def test_ignores_dunder_methods(self):
        # def __str__(self): return self._name
    def test_ignores_test_files(self):
    def test_ignores_returns_none(self):
    def test_ignores_no_return(self):
```

#### 3. Configuration Tests (`test_configuration.py`)
```python
class TestConfigurationDefaults:
    """Test default configuration values"""
    def test_default_enabled_true(self):
    def test_default_max_body_statements(self):
    def test_default_ignore_patterns(self):

class TestConfigurationLoading:
    """Test configuration loading from various sources"""
    def test_loads_from_context_config(self):
    def test_loads_from_metadata(self):
    def test_loads_from_yaml_file(self):

class TestConfigurationOverrides:
    """Test configuration option overrides"""
    def test_custom_max_body_statements(self):
    def test_custom_ignore_patterns(self):
    def test_disabled_linter(self):
```

#### 4. Ignore Directives Tests (`test_ignore_directives.py`)
```python
class TestInlineIgnore:
    """Test inline ignore directives"""
    def test_respects_thailint_ignore_specific(self):
        # def get_name(self): return self._name  # thailint: ignore[method-property]
    def test_respects_thailint_ignore_generic(self):
        # def get_name(self): return self._name  # thailint: ignore
    def test_respects_noqa(self):
        # def get_name(self): return self._name  # noqa
```

#### 5. Edge Cases Tests (`test_edge_cases.py`)
```python
class TestEdgeCases:
    """Test edge cases and error handling"""
    def test_handles_empty_file(self):
    def test_handles_syntax_error(self):
    def test_handles_unicode_content(self):
    def test_handles_no_classes(self):
    def test_handles_nested_classes(self):
    def test_handles_multiple_classes(self):
```

#### 6. Violation Details Tests (`test_violation_details.py`)
```python
class TestViolationMessages:
    """Test violation message formatting"""
    def test_get_prefix_message(self):
        # Should suggest: "Method 'get_name()' should be a @property 'name'"
    def test_simple_return_message(self):
        # Should suggest: "Method 'value()' should be a @property"
    def test_computed_value_message(self):
        # Should suggest: "Method 'area()' should be a @property"

class TestViolationMetadata:
    """Test violation metadata correctness"""
    def test_correct_line_number(self):
    def test_correct_column_number(self):
    def test_correct_rule_id(self):
    def test_correct_severity(self):
```

### Success Criteria
- [ ] 40+ tests created covering all categories
- [ ] All tests fail initially (TDD red phase)
- [ ] Tests pass linting (Pylint 10.00/10, Xenon A-grade)
- [ ] Tests follow project conventions (fixtures, naming)

---

## PR2: Python Implementation

### Scope
Implement Python method-should-be-property detection to pass PR1 tests.

### Files to Create

```
src/linters/method_property/
├── __init__.py                    # Package exports
├── linter.py                      # MethodPropertyRule class
├── config.py                      # MethodPropertyConfig dataclass
├── python_analyzer.py             # AST-based method analysis
└── violation_builder.py           # Violation message creation
```

### Module Design

#### `__init__.py`
```python
"""Method Property Linter package exports."""
from .linter import MethodPropertyRule
from .config import MethodPropertyConfig

__all__ = ["MethodPropertyRule", "MethodPropertyConfig"]
```

#### `config.py`
```python
@dataclass
class MethodPropertyConfig:
    """Configuration for method-property linter."""
    enabled: bool = True
    max_body_statements: int = 3
    ignore: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config: dict, language: str | None = None) -> "MethodPropertyConfig":
        """Load configuration from dictionary."""
```

#### `python_analyzer.py`
Key methods to implement:
```python
class PythonMethodAnalyzer:
    """Analyzes Python methods for property candidacy."""

    def find_property_candidates(self, tree: ast.AST) -> list[PropertyCandidate]:
        """Find all methods that should be properties."""

    def _is_property_candidate(self, method: ast.FunctionDef) -> bool:
        """Check if method should be a property."""

    def _takes_only_self(self, method: ast.FunctionDef) -> bool:
        """Check if method takes only self parameter."""

    def _has_simple_body(self, method: ast.FunctionDef) -> bool:
        """Check if body is 1-3 statements ending with return."""

    def _returns_value(self, method: ast.FunctionDef) -> bool:
        """Check if method returns a non-None value."""

    def _has_side_effects(self, method: ast.FunctionDef) -> bool:
        """Check for assignments, loops, try/except, external calls."""

    def _is_excluded_decorator(self, method: ast.FunctionDef) -> bool:
        """Check for @staticmethod, @classmethod, @abstractmethod, @property."""

    def _is_dunder_method(self, method: ast.FunctionDef) -> bool:
        """Check if method is a dunder method (__str__, etc.)."""
```

#### `linter.py`
```python
class MethodPropertyRule(MultiLanguageLintRule):
    """Detects methods that should be @property decorators."""

    @property
    def rule_id(self) -> str:
        return "method-property.should-be-property"

    @property
    def rule_name(self) -> str:
        return "Method Should Be Property"

    @property
    def description(self) -> str:
        return "Method should be converted to @property decorator"

    def _check_python(self, context: BaseLintContext, config: MethodPropertyConfig) -> list[Violation]:
        """Check Python code for property candidates."""
```

### Success Criteria
- [ ] All PR1 tests pass (40+ tests)
- [ ] Linting passes (`just lint-full` exits with code 0)
- [ ] Pylint score exactly 10.00/10
- [ ] Xenon complexity A-grade
- [ ] MyPy passes with no errors

---

## PR3: CLI Integration

### Scope
Add CLI command for method-property linter.

### Files to Modify

- `src/cli.py` - Add `method-property` command

### Command Implementation

```python
@cli.command("method-property")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option  # Supports text, json, sarif
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@click.pass_context
def method_property(ctx, paths, config_file, format, recursive):
    """Check for methods that should be @property decorators.

    Detects Python methods that could be converted to properties:
    - Methods returning only self._attribute
    - get_* prefixed methods (Java-style)
    - Simple computed values

    Examples:
        thailint method-property src/
        thailint method-property --format json src/
        thailint method-property --format sarif src/ > report.sarif
    """
```

### Success Criteria
- [ ] Command registered and appears in `thailint --help`
- [ ] `thailint method-property --help` shows help text
- [ ] Text output format works
- [ ] JSON output format works
- [ ] SARIF output format works (SARIF v2.1.0 compliant)
- [ ] Exit codes: 0 (clean), 1 (violations), 2 (error)

---

## PR4: Self-Dogfooding

### Scope
Run method-property linter on thai-lint codebase and fix violations.

### Process

1. **Run linter on codebase**:
   ```bash
   thailint method-property src/
   ```

2. **Categorize violations**:
   - True positives to fix
   - False positives (add to exclusion rules or tests)
   - Legitimate exceptions (add ignore directive with justification)

3. **Fix violations**:
   - Convert appropriate methods to @property
   - Add ignore directives where necessary (with user permission)
   - Update tests if false positives found

### Success Criteria
- [ ] Linter runs on entire `src/` directory
- [ ] All violations addressed (fixed or documented)
- [ ] No false positives remain (or exclusion rules updated)
- [ ] All tests still pass
- [ ] `just lint-full` passes

---

## PR5: Documentation & Publishing

### Scope
Complete documentation for ReadTheDocs and PyPI users.

### Files to Create

#### `docs/method-property-linter.md`
Comprehensive user guide following pattern from `docs/magic-numbers-linter.md`:

```markdown
# Method Property Linter

**Purpose**: Guide to using the method-property linter for detecting methods that should be @property decorators

**Scope**: Configuration, usage, refactoring patterns, and best practices

## Overview
[Description of what the linter does and why it matters]

## Configuration
[YAML and JSON configuration examples]

## CLI Usage
[Command examples with all options]

## Detection Patterns
[Examples of what gets flagged]

## Exclusion Rules
[What doesn't get flagged and why]

## Refactoring Guide
[How to convert methods to properties]

## Ignore Patterns
[How to suppress violations]

## Integration with CI/CD
[SARIF output usage]

## Troubleshooting
[Common issues and solutions]
```

### Files to Modify

#### `mkdocs.yml`
Add nav entry:
```yaml
nav:
  - Linters:
      - Method Property: method-property-linter.md  # Add this line
```

#### `README.md`
- Add to linter list in features section
- Add quick example

#### `docs/cli-reference.md`
Add command documentation

#### `docs/configuration.md`
Add configuration section

#### `docs/index.md`
Update linter count and list

### Success Criteria
- [ ] `docs/method-property-linter.md` created (comprehensive guide)
- [ ] `mkdocs.yml` updated with nav entry
- [ ] `README.md` updated with linter in feature list
- [ ] `docs/cli-reference.md` updated
- [ ] `docs/configuration.md` updated
- [ ] `docs/index.md` updated
- [ ] Documentation builds without errors (`mkdocs build`)
- [ ] All tests pass
- [ ] `just lint-full` passes

---

## Implementation Guidelines

### Code Standards
- All files must have proper headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Follow existing linter patterns (see `src/linters/print_statements/`)
- Use type hints throughout
- Docstrings for all public functions (Google-style)

### Testing Requirements
- Minimum 40 tests for PR1
- Test coverage >= 80%
- Tests must pass Pylint 10.00/10
- Tests must be independent and deterministic

### Documentation Standards
- Follow header format from `.ai/docs/FILE_HEADER_STANDARDS.md`
- Use atemporal language (no "currently", "now", "new")
- Include code examples for all features
- Cross-reference related documentation

### Output Format Requirements (Mandatory)
- Text format (default): Human-readable console output
- JSON format: Machine-readable structured output
- SARIF format: SARIF v2.1.0 for CI/CD integration (see `.ai/docs/SARIF_STANDARDS.md`)

---

## Success Metrics

### Launch Metrics
- All 5 PRs merged to main
- Zero violations in thai-lint codebase (or documented exceptions)
- Documentation complete and accessible

### Ongoing Metrics
- False positive rate < 5%
- No regressions in existing tests
- Positive user feedback
