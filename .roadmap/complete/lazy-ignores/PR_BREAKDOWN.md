# Lazy Ignores Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown for the lazy-ignores linter

**Scope**: 8 atomic pull requests from initial tests through documentation

**Overview**: Comprehensive breakdown of the lazy-ignores linter into 8 manageable, atomic pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality while incrementally building toward the complete feature. Uses TDD approach where PR1 creates failing tests and subsequent PRs implement features.

**Dependencies**: Existing file-header linter, CLI infrastructure, core types

**Exports**: PR implementation plans, file structures, testing strategies, success criteria

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD with atomic PRs, each independently testable and revertible

---

## Overview

This document breaks down the lazy-ignores linter into 8 manageable PRs:

| PR | Focus | Approach |
|----|-------|----------|
| PR1 | Tests & Infrastructure | TDD - Write failing tests first |
| PR2 | Python Detection | Implement to pass tests |
| PR3 | Header Parser | Implement to pass tests |
| PR4 | TypeScript/JS Detection | Implement to pass tests |
| PR5 | Test Skip Detection | Implement to pass tests |
| PR6 | CLI Integration | Wire everything together |
| PR7 | Dogfooding | Use on ourselves |
| PR8 | Documentation | Prepare for release |

---

## PR1: Core Infrastructure & Python Tests (TDD)

**Goal**: Write failing tests that define expected behavior, plus minimal types/config

**Scope**: Test files, type definitions, configuration dataclass

### Files to Create

```
src/linters/lazy_ignores/
├── __init__.py                 # Empty, just exports
├── types.py                    # IgnoreDirective, SuppressionEntry dataclasses
└── config.py                   # LazyIgnoresConfig dataclass

tests/unit/linters/lazy_ignores/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_python_ignore_detection.py
├── test_header_parser.py
├── test_orphaned_detection.py
├── test_violation_messages.py
└── test_typescript_detection.py
```

### Step-by-Step Implementation

#### Step 1: Create types.py

```python
"""
Purpose: Type definitions for lazy-ignores linter
Scope: Data structures for ignore directives and suppression entries
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class IgnoreType(Enum):
    """Type of linting ignore directive."""
    NOQA = "noqa"
    TYPE_IGNORE = "type:ignore"
    PYLINT_DISABLE = "pylint:disable"
    NOSEC = "nosec"
    TS_IGNORE = "ts-ignore"
    TS_NOCHECK = "ts-nocheck"
    TS_EXPECT_ERROR = "ts-expect-error"
    ESLINT_DISABLE = "eslint-disable"


@dataclass(frozen=True)
class IgnoreDirective:
    """Represents a linting ignore found in code."""
    ignore_type: IgnoreType
    rule_ids: tuple[str, ...]  # Can have multiple: noqa: PLR0912, PLR0915
    line: int
    column: int
    raw_text: str  # Original comment text
    file_path: Path


@dataclass(frozen=True)
class SuppressionEntry:
    """Represents a suppression declared in file header."""
    rule_id: str  # Normalized rule ID
    justification: str
    raw_text: str  # Original header line
```

#### Step 2: Create config.py

```python
"""
Purpose: Configuration for lazy-ignores linter
Scope: All configurable options
"""
from dataclasses import dataclass, field


@dataclass
class LazyIgnoresConfig:
    """Configuration for the lazy-ignores linter."""
    # Pattern detection toggles
    check_noqa: bool = True
    check_type_ignore: bool = True
    check_pylint_disable: bool = True
    check_nosec: bool = True
    check_ts_ignore: bool = True
    check_eslint_disable: bool = True
    check_test_skips: bool = True

    # Orphaned detection
    check_orphaned: bool = True  # Header entries without matching ignores

    # File patterns to ignore
    ignore_patterns: list[str] = field(default_factory=lambda: [
        "tests/**",  # Don't enforce in test files by default
        "**/__pycache__/**",
    ])

    @classmethod
    def from_dict(cls, config_dict: dict) -> "LazyIgnoresConfig":
        """Create config from dictionary."""
        return cls(
            check_noqa=config_dict.get("check_noqa", True),
            check_type_ignore=config_dict.get("check_type_ignore", True),
            check_pylint_disable=config_dict.get("check_pylint_disable", True),
            check_nosec=config_dict.get("check_nosec", True),
            check_ts_ignore=config_dict.get("check_ts_ignore", True),
            check_eslint_disable=config_dict.get("check_eslint_disable", True),
            check_test_skips=config_dict.get("check_test_skips", True),
            check_orphaned=config_dict.get("check_orphaned", True),
            ignore_patterns=config_dict.get("ignore_patterns", []),
        )
```

#### Step 3: Create test files with failing tests

**tests/unit/linters/lazy_ignores/test_python_ignore_detection.py**:

```python
"""Tests for Python ignore pattern detection."""
import pytest
from src.linters.lazy_ignores.python_analyzer import PythonIgnoreDetector


class TestNoqaDetection:
    """Tests for # noqa pattern detection."""

    def test_detects_bare_noqa(self) -> None:
        """Detects # noqa without rule IDs."""
        code = "x = 1  # noqa"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert directives[0].rule_ids == ()

    def test_detects_noqa_with_single_rule(self) -> None:
        """Detects # noqa: PLR0912."""
        code = "def complex():  # noqa: PLR0912"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "PLR0912" in directives[0].rule_ids

    def test_detects_noqa_with_multiple_rules(self) -> None:
        """Detects # noqa: PLR0912, PLR0915."""
        code = "def complex():  # noqa: PLR0912, PLR0915"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "PLR0912" in directives[0].rule_ids
        assert "PLR0915" in directives[0].rule_ids


class TestTypeIgnoreDetection:
    """Tests for # type: ignore detection."""

    def test_detects_bare_type_ignore(self) -> None:
        """Detects # type: ignore."""
        code = "x: int = 'string'  # type: ignore"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1

    def test_detects_type_ignore_with_code(self) -> None:
        """Detects # type: ignore[arg-type]."""
        code = "foo(x)  # type: ignore[arg-type]"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "arg-type" in directives[0].rule_ids


class TestPylintDisableDetection:
    """Tests for # pylint: disable detection."""

    def test_detects_pylint_disable(self) -> None:
        """Detects # pylint: disable=no-member."""
        code = "obj.method()  # pylint: disable=no-member"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "no-member" in directives[0].rule_ids


class TestNosecDetection:
    """Tests for # nosec detection."""

    def test_detects_nosec_with_rule(self) -> None:
        """Detects # nosec B602."""
        code = "subprocess.run(cmd, shell=True)  # nosec B602"
        detector = PythonIgnoreDetector()
        directives = detector.find_ignores(code)
        assert len(directives) == 1
        assert "B602" in directives[0].rule_ids
```

**tests/unit/linters/lazy_ignores/test_header_parser.py**:

```python
"""Tests for header Suppressions section parsing."""
import pytest
from src.linters.lazy_ignores.header_parser import SuppressionsParser


class TestSuppressionsExtraction:
    """Tests for extracting Suppressions section from headers."""

    def test_parses_single_suppression(self) -> None:
        """Parses a single suppression entry."""
        header = '''"""
Purpose: Test file

Suppressions:
    PLR0912: Complex branching required for state machine
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert len(entries) == 1
        assert entries["PLR0912"] == "Complex branching required for state machine"

    def test_parses_multiple_suppressions(self) -> None:
        """Parses multiple suppression entries."""
        header = '''"""
Purpose: Test file

Suppressions:
    PLR0912: State machine complexity
    type:ignore[arg-type]: Pydantic validation
    nosec B602: Trusted subprocess call
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert len(entries) == 3
        assert "PLR0912" in entries
        assert "type:ignore[arg-type]" in entries
        assert "nosec B602" in entries

    def test_returns_empty_when_no_suppressions(self) -> None:
        """Returns empty dict when no Suppressions section."""
        header = '''"""
Purpose: Test file
Scope: Testing
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert entries == {}


class TestRuleIdNormalization:
    """Tests for rule ID normalization."""

    def test_normalizes_case(self) -> None:
        """Normalizes rule ID case for matching."""
        parser = SuppressionsParser()
        # These should all match the same rule
        assert parser.normalize_rule_id("PLR0912") == parser.normalize_rule_id("plr0912")

    def test_preserves_type_ignore_brackets(self) -> None:
        """Preserves type:ignore[code] format."""
        parser = SuppressionsParser()
        normalized = parser.normalize_rule_id("type:ignore[arg-type]")
        assert "arg-type" in normalized
```

**tests/unit/linters/lazy_ignores/test_orphaned_detection.py**:

```python
"""Tests for orphaned suppression detection."""
import pytest
from src.linters.lazy_ignores.linter import LazyIgnoresRule


class TestOrphanedDetection:
    """Tests for detecting orphaned header entries."""

    def test_detects_orphaned_suppression(self) -> None:
        """Header declares PLR0912 but no such ignore in code."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: Some justification
"""

def simple_function():
    return 1
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 1

    def test_no_orphaned_when_ignore_exists(self) -> None:
        """No orphaned violation when ignore actually exists."""
        code = '''"""
Purpose: Test

Suppressions:
    PLR0912: State machine complexity
"""

def complex():  # noqa: PLR0912
    # ... complex code ...
    pass
'''
        rule = LazyIgnoresRule()
        violations = rule.check_content(code, "test.py")
        orphaned = [v for v in violations if "orphaned" in v.rule_id.lower()]
        assert len(orphaned) == 0
```

**tests/unit/linters/lazy_ignores/test_violation_messages.py**:

```python
"""Tests for violation message formatting."""
import pytest
from src.linters.lazy_ignores.violation_builder import build_unjustified_violation


class TestAgentGuidance:
    """Tests for AI agent guidance in violation messages."""

    def test_violation_includes_header_instruction(self) -> None:
        """Error message tells agent to add header entry."""
        violation = build_unjustified_violation(
            file_path="src/routes.py",
            line=45,
            column=20,
            rule_id="PLR0912",
            raw_text="# noqa: PLR0912",
        )
        assert "Suppressions:" in violation.suggestion
        assert "PLR0912" in violation.suggestion

    def test_violation_requires_human_approval(self) -> None:
        """Error message emphasizes human approval requirement."""
        violation = build_unjustified_violation(
            file_path="src/routes.py",
            line=45,
            column=20,
            rule_id="PLR0912",
            raw_text="# noqa: PLR0912",
        )
        assert "human" in violation.suggestion.lower()
        assert "approval" in violation.suggestion.lower() or "permission" in violation.suggestion.lower()
```

### Success Criteria

- [ ] All test files created
- [ ] Tests fail with ImportError or NotImplementedError (not syntax errors)
- [ ] types.py has IgnoreDirective and SuppressionEntry dataclasses
- [ ] config.py has LazyIgnoresConfig with all options
- [ ] `pytest tests/unit/linters/lazy_ignores/ -v` runs (tests fail but no crashes)

### Testing

```bash
# Should fail with import/not-implemented errors
pytest tests/unit/linters/lazy_ignores/ -v --tb=short
```

---

## PR2: Python Ignore Detection

**Goal**: Implement Python ignore pattern detection to pass tests from PR1

**Scope**: Detect noqa, type:ignore, pylint:disable, nosec patterns

### Files to Create

```
src/linters/lazy_ignores/
├── ignore_detector.py      # Base detector interface
└── python_analyzer.py      # Python-specific detection
```

### Step-by-Step Implementation

#### Step 1: Create ignore_detector.py (base interface)

```python
"""
Purpose: Base interface for ignore directive detection
Scope: Abstract base for language-specific analyzers
"""
from abc import ABC, abstractmethod
from src.linters.lazy_ignores.types import IgnoreDirective


class BaseIgnoreDetector(ABC):
    """Abstract base for ignore directive detectors."""

    @abstractmethod
    def find_ignores(self, code: str) -> list[IgnoreDirective]:
        """Find all ignore directives in the given code."""
```

#### Step 2: Create python_analyzer.py

```python
"""
Purpose: Detect Python linting ignore directives
Scope: noqa, type:ignore, pylint:disable, nosec patterns
"""
import re
from pathlib import Path
from src.linters.lazy_ignores.ignore_detector import BaseIgnoreDetector
from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType


class PythonIgnoreDetector(BaseIgnoreDetector):
    """Detects Python linting ignore directives."""

    # Regex patterns for each ignore type
    PATTERNS = {
        IgnoreType.NOQA: re.compile(
            r"#\s*noqa(?::\s*([A-Z0-9,\s]+))?",
            re.IGNORECASE
        ),
        IgnoreType.TYPE_IGNORE: re.compile(
            r"#\s*type:\s*ignore(?:\[([^\]]+)\])?"
        ),
        IgnoreType.PYLINT_DISABLE: re.compile(
            r"#\s*pylint:\s*disable=([a-z0-9\-,]+)",
            re.IGNORECASE
        ),
        IgnoreType.NOSEC: re.compile(
            r"#\s*nosec(?:\s+([A-Z0-9]+))?",
            re.IGNORECASE
        ),
    }

    def find_ignores(self, code: str, file_path: Path | None = None) -> list[IgnoreDirective]:
        """Find all Python ignore directives in code."""
        directives: list[IgnoreDirective] = []

        for line_num, line in enumerate(code.splitlines(), start=1):
            for ignore_type, pattern in self.PATTERNS.items():
                match = pattern.search(line)
                if match:
                    rule_ids = self._extract_rule_ids(match, ignore_type)
                    directives.append(IgnoreDirective(
                        ignore_type=ignore_type,
                        rule_ids=tuple(rule_ids),
                        line=line_num,
                        column=match.start(),
                        raw_text=match.group(0),
                        file_path=file_path or Path("unknown"),
                    ))

        return directives

    def _extract_rule_ids(self, match: re.Match, ignore_type: IgnoreType) -> list[str]:
        """Extract rule IDs from regex match."""
        group = match.group(1)
        if not group:
            return []

        # Split on comma and clean up
        ids = [r.strip() for r in group.split(",")]
        return [r for r in ids if r]
```

### Success Criteria

- [ ] All tests in test_python_ignore_detection.py pass
- [ ] Handles edge cases (whitespace, case sensitivity)
- [ ] Returns correct line/column positions

---

## PR3: Header Suppressions Parser

**Goal**: Parse Suppressions: section from file headers

**Scope**: Extract and normalize suppression entries from Python and TypeScript headers

### Files to Create

```
src/linters/lazy_ignores/
└── header_parser.py        # Suppressions section parser
```

### Step-by-Step Implementation

#### Step 1: Create header_parser.py

```python
"""
Purpose: Parse Suppressions section from file headers
Scope: Python docstrings and TypeScript JSDoc comments
"""
import re
from src.linters.lazy_ignores.types import SuppressionEntry


class SuppressionsParser:
    """Parses Suppressions section from file headers."""

    # Pattern to find Suppressions section
    SUPPRESSIONS_SECTION = re.compile(
        r"Suppressions:\s*\n((?:\s+\S+:.*\n?)+)",
        re.MULTILINE
    )

    # Pattern to parse individual entries
    ENTRY_PATTERN = re.compile(
        r"^\s+([^:]+):\s*(.+)$",
        re.MULTILINE
    )

    def parse(self, header: str) -> dict[str, str]:
        """Parse Suppressions section, return rule_id -> justification mapping."""
        section_match = self.SUPPRESSIONS_SECTION.search(header)
        if not section_match:
            return {}

        entries: dict[str, str] = {}
        section_content = section_match.group(1)

        for match in self.ENTRY_PATTERN.finditer(section_content):
            rule_id = self.normalize_rule_id(match.group(1).strip())
            justification = match.group(2).strip()
            entries[rule_id] = justification

        return entries

    def normalize_rule_id(self, rule_id: str) -> str:
        """Normalize rule ID for matching."""
        # Lowercase for case-insensitive matching
        # But preserve structure like type:ignore[arg-type]
        return rule_id.lower()

    def extract_header(self, code: str, language: str = "python") -> str:
        """Extract the header section from code."""
        if language == "python":
            return self._extract_python_header(code)
        elif language in ("typescript", "javascript"):
            return self._extract_ts_header(code)
        return ""

    def _extract_python_header(self, code: str) -> str:
        """Extract Python docstring header."""
        # Match triple-quoted docstring at start of file
        match = re.match(r'^"""(.*?)"""', code, re.DOTALL)
        if match:
            return match.group(0)
        match = re.match(r"^'''(.*?)'''", code, re.DOTALL)
        if match:
            return match.group(0)
        return ""

    def _extract_ts_header(self, code: str) -> str:
        """Extract TypeScript/JavaScript JSDoc header."""
        match = re.match(r"^/\*\*(.*?)\*/", code, re.DOTALL)
        if match:
            return match.group(0)
        return ""
```

### Success Criteria

- [ ] All tests in test_header_parser.py pass
- [ ] Correctly extracts Python docstring headers
- [ ] Correctly extracts TypeScript JSDoc headers
- [ ] Normalizes rule IDs for matching

---

## PR4: TypeScript/JavaScript Detection

**Goal**: Detect TypeScript and JavaScript ignore patterns

**Scope**: @ts-ignore, @ts-nocheck, @ts-expect-error, eslint-disable patterns

### Files to Create

```
src/linters/lazy_ignores/
└── typescript_analyzer.py  # TypeScript/JavaScript detection

tests/unit/linters/lazy_ignores/
└── test_typescript_detection.py  # Tests (if not in PR1)
```

### Patterns to Detect

| Pattern | Regex | Example |
|---------|-------|---------|
| @ts-ignore | `//\s*@ts-ignore` | `// @ts-ignore` |
| @ts-nocheck | `//\s*@ts-nocheck` | `// @ts-nocheck` |
| @ts-expect-error | `//\s*@ts-expect-error` | `// @ts-expect-error` |
| eslint-disable-next-line | `//\s*eslint-disable-next-line` | `// eslint-disable-next-line` |
| eslint-disable (block) | `/\*\s*eslint-disable` | `/* eslint-disable */` |

### Success Criteria

- [ ] All TypeScript pattern tests pass
- [ ] Handles both single-line (//) and block (/* */) comments
- [ ] Correctly identifies line numbers

---

## PR5: Test Skip Detection

**Goal**: Detect test skips without reasons

**Scope**: pytest skips (Python), it.skip/describe.skip (JavaScript)

### Files to Create

```
src/linters/lazy_ignores/
└── test_skip_detector.py   # Test skip detection

tests/unit/linters/lazy_ignores/
└── test_test_skip_detection.py  # Tests
```

### Python Patterns

```python
# VIOLATIONS (no reason):
@pytest.mark.skip
@pytest.mark.skip()
pytest.skip()

# ALLOWED (has reason):
@pytest.mark.skip(reason="...")
@pytest.mark.skipif(condition, reason="...")
pytest.skip("reason")
```

### JavaScript Patterns

```javascript
// VIOLATIONS (lazy skips):
it.skip('test name', ...)
describe.skip('suite', ...)
test.skip('test', ...)

// Note: These are always violations in JS because
// the proper way is to remove or fix the test
```

### Success Criteria

- [ ] Detects pytest skips without reason
- [ ] Allows pytest skips with reason
- [ ] Detects JavaScript test skips

---

## PR6: CLI Integration & Output Formats

**Goal**: Wire everything together with CLI command and output formatting

**Scope**: CLI command, text/json/sarif output, main linter class

### Files to Create/Modify

```
src/linters/lazy_ignores/
├── linter.py               # Main rule class
└── violation_builder.py    # Agent-friendly messages

src/cli/linters/
└── code_patterns.py        # MODIFY - Add command
```

### CLI Command

```bash
thailint lazy-ignores [OPTIONS] [PATHS]...

Options:
  --format, -f [text|json|sarif]  Output format
  --check-orphaned/--no-check-orphaned  Check for orphaned suppressions
  --check-tests/--no-check-tests  Check test skip patterns
  -v, --verbose  Verbose output
```

### Error Message Format

```
lazy-ignores.unjustified  src/routes.py:45:20  ERROR
  Unjustified suppression: # noqa: PLR0912

  To fix, add entry to file header Suppressions section:

      Suppressions:
          PLR0912: [Your justification here]

  IMPORTANT: Suppression requires human approval. Do not add
  without explicit permission from a human reviewer.
```

### Success Criteria

- [ ] `thailint lazy-ignores src/` works
- [ ] All three output formats work
- [ ] Error messages include agent guidance
- [ ] Orphaned detection works end-to-end

---

## PR7: Dogfooding - Internal Use

**Goal**: Add lazy-ignores to thai-lint's own quality gates

**Scope**: Fix own violations, add to just lint-full, update docs

### Files to Modify

```
justfile                              # Add to lint-full
.ai/docs/FILE_HEADER_STANDARDS.md     # Document Suppressions section
AGENTS.md                             # Update with new linter
```

### Steps

1. Run `thailint lazy-ignores src/` on thai-lint
2. Add proper Suppressions sections to files with ignores
3. Add to justfile: `just lint-lazy-ignores`
4. Add to lint-full target
5. Update FILE_HEADER_STANDARDS.md with Suppressions format
6. Update AGENTS.md with new command

### Success Criteria

- [ ] `thailint lazy-ignores src/` passes on thai-lint
- [ ] `just lint-full` includes lazy-ignores check
- [ ] All existing ignores have header justifications

---

## PR8: Documentation & PyPI Prep

**Goal**: Complete user documentation

**Scope**: User guide, examples, README update

### Files to Create/Modify

```
docs/linters/lazy-ignores.md           # NEW - User guide
.ai/howtos/how-to-fix-lazy-ignores.md  # NEW - Fix guide
README.md                              # Add to linter list
```

### Documentation Contents

1. **What it detects** - Pattern list with examples
2. **How to fix** - Step-by-step for adding Suppressions
3. **Configuration** - All options explained
4. **Examples** - Before/after code
5. **CI Integration** - GitHub Actions, pre-commit

### Success Criteria

- [ ] User documentation complete
- [ ] AI agent guide complete
- [ ] README updated with new linter
- [ ] Examples tested and working

---

## Implementation Guidelines

### Code Standards
- Follow existing linter patterns (see `src/linters/nesting/`)
- Pylint score exactly 10.00/10
- Xenon A-grade complexity (every function)
- Full type hints, no `Any` unless absolutely necessary
- Docstrings on all public functions (Google style)

### Testing Requirements
- TDD: Write failing tests first (PR1)
- Target 90%+ coverage
- Test edge cases (empty files, malformed headers)
- Include both positive and negative test cases

### Documentation Standards
- Follow `.ai/docs/FILE_HEADER_STANDARDS.md`
- Use atemporal language (no "currently", "now")
- Include code examples

---

## Success Metrics

### Launch Metrics
- [ ] All 8 PRs merged
- [ ] 90%+ test coverage
- [ ] Zero false positives on thai-lint codebase
- [ ] Performance < 100ms per file

### Ongoing Metrics
- User adoption (pypi downloads)
- False positive reports
- Feature requests
