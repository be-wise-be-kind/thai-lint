# LBYL Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of LBYL linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from infrastructure through dogfooding and documentation

**Overview**: Comprehensive breakdown of the LBYL linter feature into 5 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: stringly_typed linter (reference pattern), src/core/base.py (BaseLintRule), ast module

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the LBYL linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Infrastructure + Dict Key Detection (Foundation)

### Scope
Set up the complete linter infrastructure and implement the first pattern detector.
This PR establishes all patterns that subsequent PRs will follow.

### Files to Create

#### Test Files (Write First - TDD)

**`tests/unit/linters/lbyl/__init__.py`**
```python
"""
Purpose: Test package for LBYL linter unit tests

Scope: All unit tests for LBYL pattern detection

Overview: Package initialization for lbyl linter tests...
"""
```

**`tests/unit/linters/lbyl/conftest.py`**
```python
"""
Purpose: Shared pytest fixtures for LBYL linter tests

Scope: Fixtures for mock contexts, sample code, and configurations
"""
import pytest
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def lbyl_config() -> dict:
    """Standard configuration for testing."""
    return {
        "enabled": True,
        "detect_dict_key": True,
        # ... other pattern toggles
    }

@pytest.fixture
def mock_context():
    """Factory for creating mock lint contexts."""
    def _create(code: str, filename: str = "test.py"):
        context = Mock()
        context.file_path = Path(filename)
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        return context
    return _create
```

**`tests/unit/linters/lbyl/test_config.py`** (~10 tests)
- Test default values
- Test from_dict() loading
- Test pattern toggle behavior
- Test invalid config handling

**`tests/unit/linters/lbyl/test_dict_key_detector.py`** (~15 tests)
```python
class TestDictKeyDetectorBasic:
    """Tests for basic dict key LBYL detection."""

    def test_detects_if_in_dict_before_access(self):
        """Detect if key in dict: dict[key] pattern."""

    def test_detects_if_key_in_dict_with_different_variable_names(self):
        """Detect pattern with various variable names."""

    def test_no_false_positive_for_different_dict(self):
        """No detection when if and access use different dicts."""

    def test_no_false_positive_for_different_key(self):
        """No detection when if and access use different keys."""

class TestDictKeyDetectorEdgeCases:
    """Edge case tests for dict key detection."""

    def test_handles_nested_dict_access(self):
        """Detect nested dict patterns."""

    def test_handles_f_string_keys(self):
        """Detect patterns with f-string keys."""

    def test_ignores_walrus_operator_pattern(self):
        """Don't flag: if (x := d.get(k)) is not None"""

class TestDictKeyDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except_keyerror(self):
        """Suggestion should mention try/except KeyError."""
```

**`tests/unit/linters/lbyl/test_linter.py`** (~10 tests)
- Test rule_id property
- Test rule_name property
- Test description property
- Test check() method with Python context
- Test check() returns empty list for non-Python

#### Source Files

**`src/linters/lbyl/__init__.py`**
```python
"""
Purpose: LBYL (Look Before You Leap) linter package exports

Scope: Detect LBYL anti-patterns in Python code and suggest EAFP alternatives

Overview: Package providing LBYL pattern detection for Python code. Identifies
    common anti-patterns where explicit checks are performed before operations
    (e.g., if key in dict before dict[key]) and suggests EAFP (Easier to Ask
    Forgiveness than Permission) alternatives using try/except blocks.

Dependencies: ast module for Python parsing, src.core for base classes

Exports: LBYLRule, LBYLConfig, lint convenience function

Interfaces: LBYLRule.check(context) -> list[Violation]

Implementation: AST-based pattern detection with configurable pattern toggles
"""

from .config import LBYLConfig
from .linter import LBYLRule

__all__ = ["LBYLRule", "LBYLConfig"]
```

**`src/linters/lbyl/config.py`**
```python
"""
Purpose: Configuration dataclass for LBYL linter

Scope: Pattern toggles, ignore patterns, and validation

Overview: Provides LBYLConfig dataclass with pattern-specific toggles...
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LBYLConfig:
    """Configuration for LBYL linter."""

    enabled: bool = True

    # Pattern toggles
    detect_dict_key: bool = True
    detect_hasattr: bool = True
    detect_isinstance: bool = False    # Disabled - many valid uses
    detect_file_exists: bool = True
    detect_len_check: bool = True
    detect_none_check: bool = False    # Disabled - many valid uses
    detect_string_validation: bool = True
    detect_division_check: bool = True

    ignore: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "LBYLConfig":
        """Load configuration from dictionary."""
        # Implementation
```

**`src/linters/lbyl/linter.py`**
```python
"""
Purpose: LBYL linter rule implementing BaseLintRule

Scope: Main entry point for LBYL pattern detection

Overview: Implements LBYLRule extending BaseLintRule...
"""
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation

from .config import LBYLConfig
from .python_analyzer import PythonLBYLAnalyzer


class LBYLRule(BaseLintRule):
    """Detects LBYL anti-patterns in Python code."""

    @property
    def rule_id(self) -> str:
        return "lbyl"

    @property
    def rule_name(self) -> str:
        return "Look Before You Leap Detection"

    @property
    def description(self) -> str:
        return "Detects LBYL anti-patterns and suggests EAFP alternatives"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for LBYL violations."""
        # Implementation
```

**`src/linters/lbyl/python_analyzer.py`**
```python
"""
Purpose: Python code analyzer coordinating LBYL pattern detection

Scope: Orchestrates multiple pattern detectors for Python AST analysis

Overview: Coordinates all pattern detectors (dict_key, hasattr, etc.)...
"""
import ast
from pathlib import Path

from src.core.types import Violation

from .config import LBYLConfig
from .violation_builder import LBYLViolationBuilder
from .pattern_detectors import DictKeyDetector


class PythonLBYLAnalyzer:
    """Analyzes Python code for LBYL patterns."""

    def __init__(self, config: LBYLConfig) -> None:
        self.config = config
        self.violation_builder = LBYLViolationBuilder()

    def analyze(self, code: str, file_path: Path) -> list[Violation]:
        """Analyze code and return violations."""
        # Parse AST
        # Run enabled detectors
        # Convert patterns to violations
```

**`src/linters/lbyl/violation_builder.py`**
```python
"""
Purpose: Build violations with EAFP suggestions for LBYL patterns

Scope: Generate contextual error messages and fix suggestions

Overview: Creates Violation objects with pattern-specific EAFP suggestions...
"""
from src.core.types import Violation


class LBYLViolationBuilder:
    """Builds violations with EAFP suggestions."""

    def build_dict_key_violation(
        self,
        file_path: str,
        line: int,
        column: int,
        dict_name: str,
        key_name: str
    ) -> Violation:
        """Create violation for dict key LBYL pattern."""
        return Violation(
            rule_id="lbyl.dict-key-check",
            message=f"LBYL pattern: checking '{key_name} in {dict_name}' before access",
            suggestion=f"Use try/except KeyError instead: try: value = {dict_name}[{key_name}] except KeyError: ...",
            file_path=file_path,
            line=line,
            column=column,
        )
```

**`src/linters/lbyl/pattern_detectors/__init__.py`**
```python
"""
Purpose: Pattern detector exports for LBYL linter

Scope: All AST-based pattern detectors
"""
from .dict_key_detector import DictKeyDetector

__all__ = ["DictKeyDetector"]
```

**`src/linters/lbyl/pattern_detectors/base.py`**
```python
"""
Purpose: Base class for LBYL pattern detectors

Scope: Abstract base providing common detector interface

Overview: Defines BaseLBYLDetector with find_patterns() method...
"""
import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LBYLPattern:
    """Base pattern data."""
    line_number: int
    column: int


class BaseLBYLDetector(ast.NodeVisitor, ABC):
    """Base class for LBYL pattern detectors."""

    @abstractmethod
    def find_patterns(self, tree: ast.AST) -> list[LBYLPattern]:
        """Find LBYL patterns in AST."""
        raise NotImplementedError
```

**`src/linters/lbyl/pattern_detectors/dict_key_detector.py`**
```python
"""
Purpose: Detect dict key LBYL patterns in Python AST

Scope: Find 'if key in dict: dict[key]' patterns

Overview: AST NodeVisitor that detects LBYL patterns where dictionary key
    membership is checked before accessing the value...
"""
import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class DictKeyPattern(LBYLPattern):
    """Detected dict key LBYL pattern."""
    dict_name: str
    key_expression: str


class DictKeyDetector(BaseLBYLDetector):
    """Detects 'if key in dict: dict[key]' patterns."""

    def __init__(self) -> None:
        self.patterns: list[DictKeyPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[DictKeyPattern]:
        """Find dict key LBYL patterns."""
        self.patterns = []
        self.visit(tree)
        return self.patterns

    def visit_If(self, node: ast.If) -> None:
        """Check if statement for dict key LBYL pattern."""
        # Check if test is 'key in dict' comparison
        # Check if body contains dict[key] access with same dict/key
        # If match, add to patterns
        self.generic_visit(node)
```

### CLI Registration

Update CLI to register the lbyl command (follow existing pattern in `src/cli/linters/`).

### Testing Steps

```bash
# Run tests (should fail initially - TDD)
just test tests/unit/linters/lbyl/

# Implement until tests pass
just test tests/unit/linters/lbyl/

# Verify all output formats
thailint lbyl --format text .
thailint lbyl --format json .
thailint lbyl --format sarif .

# Quality gates
just lint-full
```

### Success Criteria
- [ ] All tests pass
- [ ] Dict key pattern detected correctly
- [ ] No false positives for different dict/key
- [ ] All 3 output formats work
- [ ] Pylint 10.00/10
- [ ] Xenon A-grade

---

## PR2: hasattr + isinstance Detectors

### Scope
Add detection for hasattr and isinstance LBYL patterns.

### Files to Create

**`tests/unit/linters/lbyl/test_hasattr_detector.py`** (~15 tests)
```python
class TestHasattrDetectorBasic:
    def test_detects_hasattr_before_getattr(self):
        """Detect: if hasattr(obj, 'attr'): obj.attr"""

    def test_detects_hasattr_before_method_call(self):
        """Detect: if hasattr(obj, 'method'): obj.method()"""

    def test_no_false_positive_different_attribute(self):
        """No detection when hasattr and access use different attrs."""

class TestHasattrDetectorSuggestions:
    def test_suggestion_includes_attributeerror(self):
        """Suggestion mentions AttributeError."""
```

**`tests/unit/linters/lbyl/test_isinstance_detector.py`** (~15 tests)
```python
class TestIsinstanceDetectorBasic:
    def test_detects_isinstance_before_type_operation(self):
        """Detect: if isinstance(x, int): x + 1"""

    def test_disabled_by_default(self):
        """isinstance detection is disabled by default."""

    def test_enabled_via_config(self):
        """isinstance detection can be enabled via config."""

class TestIsinstanceDetectorFalsePositives:
    def test_no_flag_for_type_narrowing(self):
        """Don't flag valid type narrowing patterns."""
```

**`src/linters/lbyl/pattern_detectors/hasattr_detector.py`**
```python
"""
Purpose: Detect hasattr LBYL patterns in Python AST

Scope: Find 'if hasattr(obj, attr): obj.attr' patterns
"""
```

**`src/linters/lbyl/pattern_detectors/isinstance_detector.py`**
```python
"""
Purpose: Detect isinstance LBYL patterns in Python AST

Scope: Find 'if isinstance(x, Type): x.type_specific_op()' patterns
"""
```

### Implementation Notes
- isinstance is disabled by default (`detect_isinstance: bool = False`)
- Only flag isinstance when type-specific operations follow
- hasattr detection must match the attribute name in check and access

### Success Criteria
- [ ] hasattr patterns detected with correct suggestions
- [ ] isinstance detection is configurable
- [ ] No false positives for valid type narrowing

---

## PR3: File Exists + Len Check Detectors

### Scope
Add detection for file existence and length check patterns.

### Files to Create

**`tests/unit/linters/lbyl/test_file_exists_detector.py`** (~15 tests)
```python
class TestFileExistsDetectorBasic:
    def test_detects_os_path_exists_before_open(self):
        """Detect: if os.path.exists(f): open(f)"""

    def test_detects_pathlib_exists_before_open(self):
        """Detect: if Path(f).exists(): open(f)"""

    def test_handles_import_aliases(self):
        """Detect with: from os.path import exists"""

class TestFileExistsDetectorEdgeCases:
    def test_no_flag_for_directory_check(self):
        """Don't flag: if os.path.isdir(d): os.listdir(d)"""
```

**`tests/unit/linters/lbyl/test_len_check_detector.py`** (~15 tests)
```python
class TestLenCheckDetectorBasic:
    def test_detects_len_greater_before_index(self):
        """Detect: if len(lst) > i: lst[i]"""

    def test_detects_len_gte_before_index(self):
        """Detect: if len(lst) >= i: lst[i-1]"""

    def test_detects_index_less_than_len(self):
        """Detect: if i < len(lst): lst[i]"""

class TestLenCheckDetectorFalsePositives:
    def test_no_flag_for_different_list(self):
        """Don't flag when len and access use different lists."""
```

**`src/linters/lbyl/pattern_detectors/file_exists_detector.py`**
```python
"""
Purpose: Detect file existence LBYL patterns in Python AST

Scope: Find 'if os.path.exists(f): open(f)' patterns
"""
```

**`src/linters/lbyl/pattern_detectors/len_check_detector.py`**
```python
"""
Purpose: Detect length check LBYL patterns in Python AST

Scope: Find 'if len(lst) > i: lst[i]' patterns
"""
```

### Implementation Notes
- file_exists must track import aliases (os.path.exists, Path.exists, exists)
- len_check must handle various comparison operators (>, >=, <, <=)
- Match the collection variable between check and access

### Success Criteria
- [ ] Both os.path.exists and Path.exists detected
- [ ] All comparison operators handled
- [ ] No false positives for legitimate bounds checking

---

## PR4: None + String + Division Detectors

### Scope
Add detection for None checks, string validation, and division safety checks.

### Files to Create

**`tests/unit/linters/lbyl/test_none_check_detector.py`** (~15 tests)
```python
class TestNoneCheckDetectorBasic:
    def test_detects_is_not_none_before_method(self):
        """Detect: if x is not None: x.method()"""

    def test_disabled_by_default(self):
        """None check detection is disabled by default."""

class TestNoneCheckDetectorConfiguration:
    def test_enabled_via_config(self):
        """None check detection can be enabled via config."""
```

**`tests/unit/linters/lbyl/test_string_validator_detector.py`** (~15 tests)
```python
class TestStringValidatorDetectorBasic:
    def test_detects_isnumeric_before_int(self):
        """Detect: if s.isnumeric(): int(s)"""

    def test_detects_isdigit_before_int(self):
        """Detect: if s.isdigit(): int(s)"""

    def test_detects_isalpha_before_operation(self):
        """Detect: if s.isalpha(): process_alpha(s)"""
```

**`tests/unit/linters/lbyl/test_division_check_detector.py`** (~15 tests)
```python
class TestDivisionCheckDetectorBasic:
    def test_detects_nonzero_check_before_division(self):
        """Detect: if x != 0: a / x"""

    def test_detects_zero_not_equal_check(self):
        """Detect: if 0 != x: a / x"""

    def test_handles_truthy_check(self):
        """Detect: if x: a / x (where x could be 0)"""
```

**`src/linters/lbyl/pattern_detectors/none_check_detector.py`**
**`src/linters/lbyl/pattern_detectors/string_validator_detector.py`**
**`src/linters/lbyl/pattern_detectors/division_check_detector.py`**

### Implementation Notes
- None check is disabled by default (`detect_none_check: bool = False`)
- String validation covers: isnumeric, isdigit, isalpha, isdecimal
- Division check handles both != 0 and truthy checks

### Success Criteria
- [ ] None check detection is conservative (opt-in)
- [ ] String validation covers all common patterns
- [ ] Division checks handle complex expressions

---

## PR5: Integration, Dogfooding, Documentation

### Scope
Complete integration tests, dogfood on thai-lint codebase, and add documentation.

### Files to Create

**`tests/unit/linters/lbyl/test_cli_interface.py`** (~15 tests)
```python
class TestLBYLCLI:
    def test_cli_help_available(self):
        """CLI help for lbyl command works."""

    def test_cli_text_output(self):
        """CLI produces readable text output."""

    def test_cli_json_output(self):
        """CLI produces valid JSON output."""

    def test_cli_sarif_output(self):
        """CLI produces valid SARIF v2.1.0 output."""

    def test_cli_config_file_loading(self):
        """CLI loads configuration from .thailint.yaml."""
```

**`tests/unit/linters/lbyl/test_edge_cases.py`** (~15 tests)
```python
class TestLBYLEdgeCases:
    def test_empty_file(self):
        """Empty file produces no violations."""

    def test_syntax_error_handling(self):
        """Syntax errors are handled gracefully."""

    def test_nested_lbyl_patterns(self):
        """Nested LBYL patterns are all detected."""

    def test_complex_expressions(self):
        """Complex key/attribute expressions are handled."""
```

**`tests/unit/linters/lbyl/test_ignore_directives.py`** (~10 tests)
```python
class TestLBYLIgnoreDirectives:
    def test_inline_ignore_directive(self):
        """# thaiLint: ignore[lbyl] suppresses violations."""

    def test_rule_specific_ignore(self):
        """# thaiLint: ignore[lbyl.dict-key-check] suppresses specific rule."""
```

**`docs/lbyl.md`**
```markdown
# LBYL (Look Before You Leap) Linter

Detects LBYL anti-patterns in Python code and suggests EAFP alternatives.

## Overview

Python favors EAFP (Easier to Ask Forgiveness than Permission) over LBYL...

## Patterns Detected

### Dict Key Checking
...

## Configuration

```yaml
lbyl:
  enabled: true
  detect_isinstance: false  # Many valid uses
  detect_none_check: false  # Many valid uses
```

## Examples
...
```

### Dogfooding Tasks

1. Run linter on thai-lint codebase:
   ```bash
   thailint lbyl src/
   ```

2. Review findings:
   - Identify true positives
   - Identify false positives
   - Configure exceptions for legitimate patterns

3. Update configuration:
   - Add ignore directives for valid LBYL patterns
   - Document findings in this PR

4. Update README.md:
   - Add lbyl to feature list
   - Add to linter table

### Success Criteria
- [ ] All integration tests pass
- [ ] Linter runs successfully on thai-lint codebase
- [ ] False positives documented and configured
- [ ] Documentation complete
- [ ] README updated

---

## Implementation Guidelines

### Code Standards
- All files must have proper headers per FILE_HEADER_STANDARDS.md
- Pylint score must be exactly 10.00/10
- All code must be A-grade complexity (Xenon)
- Type hints required for all functions

### Testing Requirements
- TDD approach: write tests before implementation
- ~15 tests per detector
- Cover basic detection, edge cases, and suggestions
- Integration tests for CLI

### Documentation Standards
- File headers on all new files
- Docstrings on all public classes and methods
- User documentation in docs/lbyl.md

### Security Considerations
- No command injection risks (AST-based analysis only)
- Handle malformed code gracefully

### Performance Targets
- Analysis time < 100ms per file
- Memory usage proportional to file size

## Rollout Strategy

### Phase 1: PR1
- Infrastructure and first detector
- Validates architecture decisions

### Phase 2: PR2-4 (Parallel)
- Remaining detectors
- Can be developed in parallel

### Phase 3: PR5
- Integration and polish
- Dogfooding validates real-world usage

## Success Metrics

### Launch Metrics
- [ ] All 8 patterns detected
- [ ] 150+ tests passing
- [ ] All quality gates pass

### Ongoing Metrics
- False positive rate
- User feedback
- Performance benchmarks
