# Method Should Be Property Linter - Executive Summary

**Purpose**: Executive summary of the method-should-be-property linter feature for future reference

**Scope**: Feature overview, technical highlights, verification results, and future considerations

**Overview**: The method-should-be-property linter detects Python methods that should use the @property
    decorator instead of explicit getter methods. This fills a gap in the Python linting ecosystem -
    no major linter implements this check despite it being a well-documented best practice in PEP 8.

---

## Feature Overview

### Problem Solved
Python developers, especially those coming from Java or other OOP languages, often write explicit getter methods (`get_name()`) instead of using Python's `@property` decorator. This violates Pythonic conventions and creates unnecessary API complexity.

### Solution
The method-should-be-property linter uses AST analysis to detect methods that should be converted to properties:

- **Simple accessors**: `def name(self): return self._name`
- **Java-style getters**: `def get_name(self): return self._name`
- **Simple computed values**: `def area(self): return self._width * self._height`
- **Chained access**: `def config(self): return self._settings.config`

### Value Proposition
- **First-of-its-kind**: No existing major linter (Pylint, Ruff, SonarQube) implements this check
- **Enforces PEP 8 best practices**: "For simple public data attributes, expose just the attribute name"
- **Reduces API complexity**: Properties provide cleaner access patterns than getter methods
- **AI-generated code governance**: Catches a common anti-pattern in AI-generated Python code

---

## Technical Highlights

### Implementation Architecture
```
src/linters/method_property/
├── __init__.py           # Package exports
├── config.py             # Configuration (max_body_statements, ignore patterns, action verb exclusions)
├── linter.py             # MethodPropertyRule class (MultiLanguageLintRule interface)
├── python_analyzer.py    # PythonMethodAnalyzer (AST traversal and pattern detection)
└── violation_builder.py  # ViolationBuilder (message generation)
```

### Key Design Decisions

1. **Comprehensive Exclusion Rules** - Minimizes false positives:
   - Methods with parameters (beyond `self`)
   - Methods with side effects (assignments, loops, try/except)
   - Decorated methods (staticmethod, classmethod, abstractmethod, property)
   - Dunder methods (`__str__`, `__repr__`)
   - Test files (`test_*.py`, `*_test.py`)
   - Action verb methods (`to_dict()`, `serialize()`, `validate()`)

2. **Configurable Thresholds**:
   - `max_body_statements`: Maximum method body size (default: 3)
   - `ignore_methods`: Skip specific method names
   - `exclude_prefixes`: Action verb prefixes to ignore
   - `exclude_names`: Specific action verb names to ignore

3. **Standard Integration**:
   - CLI command: `thailint method-property`
   - Output formats: text, JSON, SARIF
   - Inline ignore: `# thailint: ignore[method-property]` or `# noqa`

---

## Test Coverage

- **111 unit tests** in `tests/unit/linters/method_property/`
- **681 total tests** in the project (all passing)
- **87% code coverage** for the method-property module
- **Test categories**:
  - Basic detection (16 tests)
  - Exclusion rules (31 tests)
  - Configuration (14 tests)
  - Ignore directives (11 tests)
  - Edge cases (22 tests)
  - Violation details (17 tests)

---

## Self-Dogfooding Results

The linter was run against the thai-lint codebase itself. Five violations were found and fixed:

| Class | Method | Fix |
|-------|--------|-----|
| `LinterConfigLoader` | `get_defaults()` | Converted to `defaults` property |
| `BaseBlockFilter` | `get_name()` | Converted to `name` abstract property |
| `KeywordArgumentFilter` | `get_name()` | Converted to `name` property |
| `ImportGroupFilter` | `get_name()` | Converted to `name` property |
| `DRYCache` | `get_duplicate_hashes()` | Converted to `duplicate_hashes` property |
| `DuplicateStorage` | `get_duplicate_hashes()` | Converted to `duplicate_hashes` property |

**False positive rate**: 0% after adding action verb exclusions

---

## Verification Results (2025-12-17)

### DockerHub Verification
- **Image**: `washad/thailint:0.8.0`
- **Status**: Pulls successfully, command works correctly
- **Test**: Detected violation in sample file as expected

### PyPI Verification
- **Package**: `thailint==0.8.0`
- **Status**: Installs cleanly, all dependencies resolve
- **Test**: All three output formats (text, JSON, SARIF) work correctly

---

## Quality Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Pylint score | 10.00/10 | 10.00/10 |
| Xenon complexity | A-grade | A-grade |
| Test coverage | >= 80% | 87% |
| False positive rate | < 5% | 0% |
| All tests pass | Yes | 681/681 |

---

## Version Information

- **Released in**: v0.8.0
- **Implementation commits**:
  - PR1 (tests): 111 tests created
  - PR2 (implementation): All tests pass
  - PR3 (CLI): db268dc
  - PR4 (dogfooding): b837f3b
  - PR5 (documentation): 81851f7

---

## Future Considerations

1. **set_* Detection**: Extend to detect `set_*` methods that should use `@property.setter`
2. **TypeScript Support**: Add detection for TypeScript getter/setter patterns
3. **Auto-fix Capability**: Provide automatic code transformation
4. **Configurable Severity**: Allow users to set violation severity (warning vs error)

---

## Documentation

- **User guide**: `docs/method-property-linter.md` (800+ lines)
- **CLI reference**: `docs/cli-reference.md` (method-property section)
- **Configuration**: `docs/configuration.md` (method-property section)

---

## Key References

- [PEP 8 - Properties Section](https://peps.python.org/pep-0008/#designing-for-inheritance)
- [Pylint Issue #7172](https://github.com/pylint-dev/pylint/issues/7172) (feature request - not implemented)
- [Python Properties vs Getters/Setters](https://python-course.eu/oop/properties-vs-getters-and-setters.php)
