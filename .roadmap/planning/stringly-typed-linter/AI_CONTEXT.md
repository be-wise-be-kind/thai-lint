# Stringly-Typed Linter - AI Context

**Purpose**: AI agent context document for implementing stringly-typed linter

**Scope**: Detect "stringly typed" code where strings are used instead of proper enums in Python and TypeScript

**Overview**: Comprehensive context document for AI agents working on the stringly-typed linter feature.
    This linter detects code patterns where plain strings are used where enums or typed constants
    would provide better type safety, IDE support, and maintainability. Addresses a common anti-pattern
    in AI-generated code.

**Dependencies**: MultiLanguageLintRule base class, SQLite for cross-file storage, tree-sitter for TypeScript, Click for CLI

**Exports**: StringlyTypedRule linter class, configuration options, CLI command

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Multi-language linter with cross-file analysis using finalize() hook pattern

---

## Overview

The stringly-typed linter detects code patterns where plain strings are used instead of proper enums or typed alternatives. This is a common anti-pattern, especially in AI-generated code, that leads to:

- **Non-determinism**: Typos like "stagng" or "Staging" fail silently at runtime
- **Poor IDE support**: No autocomplete for valid values
- **Scattered validation**: Same string sets validated in multiple places
- **Maintenance burden**: Changing a valid value requires finding all occurrences

## Project Background

The term "stringly typed" was coined to describe code that uses strings where stronger types would be appropriate. This is the opposite of "strongly typed."

### Research Sources
- [Stringly Typed Anti-pattern - devcards.io](https://devcards.io/stringly-typed)
- [Scott Hanselman: Stringly Typed vs Strongly Typed](https://www.hanselman.com/blog/stringly-typed-vs-strongly-typed)
- [Clean Code by Robert C. Martin](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29)

### Real-World Examples

Found in `tb-automation-py` codebase:

```python
# Pattern 1: Repeated validation across files
# File: ci_cd/build.py
if env not in ("staging", "production"):
    raise BuildError(f"Invalid environment: {env}")

# File: ci_cd/publish.py
if env not in ("staging", "production"):
    raise PublishError(f"Invalid environment: {env}")

# File: azure/web_config_backup.py
if env not in WEB_CONFIG_PATHS:
    raise WebConfigBackupError(f"Unknown environment: {env}")
```

```python
# Pattern 2: String equality chains
if status == "success":
    handle_success()
elif status == "failure":
    handle_failure()
elif status == "pending":
    handle_pending()
```

```python
# Pattern 3: Dataclass with string fields
@dataclass
class DeploymentState:
    env: str  # Only ever "staging" or "production"
    current_color: str  # Only ever "blue" or "green"
    status: str  # Only "success", "failure", "pending"
```

## Feature Vision

1. **Detect repeated string validation** - Find the same string sets validated in multiple files
2. **Suggest enums for equality chains** - When a variable is compared to multiple string literals
3. **Track function call patterns** - When a `str` parameter is only called with 2-6 specific values
4. **Low false positive rate** - Filter out logging, error messages, dict keys, format strings
5. **Cross-language support** - Work for both Python and TypeScript

## Current Application Context

Thai-lint already has several linters that detect code smells:
- **magic-numbers**: Detects unnamed numeric literals (similar concept)
- **dry**: Detects duplicate code blocks using cross-file analysis
- **print-statements**: Detects print/console statements

The stringly-typed linter follows the same patterns established by these linters.

## Target Architecture

### Core Components

```
src/linters/stringly_typed/
├── __init__.py                 # Exports StringlyTypedRule
├── linter.py                   # MultiLanguageLintRule implementation
├── config.py                   # StringlyTypedConfig dataclass
├── config_loader.py            # Configuration loading
├── storage.py                  # SQLite cross-file storage
├── storage_initializer.py      # Database setup
├── violation_generator.py      # Create violations from analysis
├── violation_builder.py        # Build individual Violation objects
├── context_filter.py           # False positive filtering
├── ignore_checker.py           # Ignore directive support
│
├── python/
│   ├── __init__.py
│   ├── analyzer.py             # Python AST coordination
│   ├── validation_detector.py  # Detects in/not in patterns
│   ├── conditional_detector.py # Detects ==, elif chains, match
│   └── call_tracker.py         # Tracks function calls with string args
│
└── typescript/
    ├── __init__.py
    ├── analyzer.py             # TypeScript tree-sitter coordination
    ├── validation_detector.py  # Detects .includes() patterns
    ├── conditional_detector.py # Detects ===, switch statements
    └── call_tracker.py         # Tracks function calls
```

### Data Flow

```
1. check() called for each file
   ├── Python files → python/analyzer.py
   │   ├── validation_detector.py → string_validations table
   │   ├── conditional_detector.py → string_validations table
   │   └── call_tracker.py → function_calls table
   └── TypeScript files → typescript/analyzer.py
       ├── validation_detector.py → string_validations table
       ├── conditional_detector.py → string_validations table
       └── call_tracker.py → function_calls table

2. finalize() called after all files processed
   ├── Query string_validations for duplicate hashes
   ├── Query function_calls for limited unique values
   ├── Apply context_filter to remove false positives
   ├── Apply ignore_checker for ignore directives
   └── Generate Violation objects via violation_generator
```

### Rule IDs

| Rule ID | Pattern | Description |
|---------|---------|-------------|
| `stringly-typed.repeated-validation` | Pattern 1 | Same string set validated in 2+ files |
| `stringly-typed.equality-chain` | Pattern 2 | Variable compared to 2+ string literals |
| `stringly-typed.limited-values` | Pattern 3 | Function param only called with limited strings |

## Key Decisions Made

### 1. Cross-File Analysis with SQLite

**Decision**: Use SQLite storage with `finalize()` hook (same as DRY linter)

**Rationale**:
- Pattern 1 requires tracking validations across files
- Pattern 3 requires aggregating function calls across files
- SQLite provides efficient querying and persistence

**Reference**: `src/linters/dry/duplicate_storage.py`

### 2. Hash-Based Duplicate Detection

**Decision**: Hash sorted string sets to find duplicates

**Implementation**:
```python
def hash_string_set(values: set[str]) -> int:
    return hash(tuple(sorted(values)))
```

**Rationale**:
- Order-independent matching (set vs tuple doesn't matter)
- Efficient storage and lookup
- Same hash = same string set

### 3. Configurable Thresholds

**Decision**: Make enum suggestion thresholds configurable

**Configuration**:
```yaml
stringly_typed:
  min_values_for_enum: 2   # Minimum values to suggest enum
  max_values_for_enum: 6   # Maximum values (above this, probably not enum-worthy)
  min_occurrences: 2       # Minimum cross-file occurrences to flag
```

**Rationale**:
- 1 value is just a constant, not enum-worthy
- 7+ values might be intentional (e.g., HTTP methods)
- Different projects have different tolerances

### 4. Context-Aware Filtering

**Decision**: Filter out common false positive contexts

**Excluded Contexts**:
- Logging calls (logger.info, console.log)
- Error messages (raise/throw)
- Dictionary keys (config dicts, TypedDict)
- Format strings (f-strings, template literals)
- URL/path patterns

**Rationale**: These use strings legitimately and shouldn't trigger warnings

## Integration Points

### With Existing Features

| Feature | Integration |
|---------|-------------|
| CLI | New `stringly-typed` command |
| Orchestrator | Uses `finalize()` hook for cross-file analysis |
| Registry | Auto-discovered via rule discovery |
| Output Formatters | text/json/sarif support |

### With Base Classes

```python
from src.core.base import MultiLanguageLintRule, BaseLintContext
from src.core.types import Violation, Severity

class StringlyTypedRule(MultiLanguageLintRule):
    @property
    def rule_id(self) -> str:
        return "stringly-typed"

    def _load_config(self, context: BaseLintContext) -> StringlyTypedConfig:
        return load_stringly_typed_config(context)

    def _check_python(self, context, config) -> list[Violation]:
        ...

    def _check_typescript(self, context, config) -> list[Violation]:
        ...

    def finalize(self) -> list[Violation]:
        # Cross-file analysis
        ...
```

## Success Metrics

| Metric | Target |
|--------|--------|
| False positive rate | <5% |
| Detection accuracy | >95% |
| Single file analysis | <100ms |
| Cross-file finalize | <1s for 100 files |
| Test coverage | >87% |

## Technical Constraints

1. **Python 3.10+**: Uses match statement support
2. **Tree-sitter**: Required for TypeScript parsing
3. **SQLite**: For cross-file storage
4. **Click**: For CLI integration
5. **SARIF 2.1.0**: For CI/CD output format

## AI Agent Guidance

### When Implementing Detection

1. Start with tests (TDD approach)
2. Use AST for Python, tree-sitter for TypeScript
3. Reference existing linters:
   - `src/linters/magic_numbers/` for false positive filtering
   - `src/linters/dry/` for cross-file storage pattern
4. Follow file header standards

### When Adding Tests

1. Create fixtures in `conftest.py`
2. Test both detection and non-detection
3. Test edge cases and false positives
4. Verify rule_id format in violations

### Common Patterns

```python
# AST visitor for Python
class ValidationVisitor(ast.NodeVisitor):
    def visit_Compare(self, node: ast.Compare) -> None:
        if isinstance(node.ops[0], (ast.In, ast.NotIn)):
            if self._is_string_collection(node.comparators[0]):
                self._record_validation(node)
        self.generic_visit(node)
```

```python
# Tree-sitter query for TypeScript
INCLUDES_QUERY = """
(call_expression
  function: (member_expression
    object: (array)
    property: (property_identifier) @method)
  arguments: (arguments (identifier) @arg)
  (#eq? @method "includes"))
"""
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| High false positive rate | Comprehensive context filtering |
| Performance on large codebases | SQLite indexing, efficient queries |
| Missing edge cases | Extensive test coverage, dogfooding |
| TypeScript parsing errors | Graceful degradation, error handling |

## Future Enhancements

1. **Auto-fix suggestions**: Generate enum definition code
2. **TypeScript Literal inference**: Detect when Literal types would help
3. **Configuration file suggestions**: Propose `.thailint.yaml` additions
4. **VS Code extension**: Real-time detection in editor
