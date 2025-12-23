# LBYL Linter - AI Context

**Purpose**: AI agent context document for implementing LBYL (Look Before You Leap) pattern detection linter

**Scope**: Python linter detecting LBYL anti-patterns and suggesting EAFP alternatives

**Overview**: Comprehensive context document for AI agents working on the LBYL linter feature.
    Provides background on EAFP vs LBYL philosophy, architectural decisions, pattern detection
    strategies, and integration guidance for implementing a linter that identifies common LBYL
    anti-patterns in Python code and suggests Pythonic EAFP alternatives.

**Dependencies**: stringly_typed linter (reference pattern), src/core/base.py (BaseLintRule),
    ast module for Python parsing, src/core/types.py (Violation)

**Exports**: Feature context, architectural decisions, pattern detection strategies, AI guidance

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: AST-based pattern detection with configurable pattern toggles and EAFP suggestions

---

## Overview

The LBYL linter detects "Look Before You Leap" anti-patterns in Python code and suggests
EAFP (Easier to Ask Forgiveness than Permission) alternatives. This is a Python-specific
linter since EAFP is a Pythonic idiom that doesn't apply to other languages.

## Project Background

### Why This Linter?

AI-generated Python code often exhibits LBYL patterns because:
1. Training data includes code from other languages where LBYL is idiomatic
2. Explicit checks seem "safer" to models
3. EAFP patterns require understanding Python's exception philosophy

### Research Sources

- [Real Python: LBYL vs EAFP](https://realpython.com/python-lbyl-vs-eafp/)
- [Microsoft Python Blog: Idiomatic Python](https://devblogs.microsoft.com/python/idiomatic-python-eafp-versus-lbyl/)
- [mathspp: EAFP and LBYL Coding Styles](https://mathspp.com/blog/pydonts/eafp-and-lbyl-coding-styles)

### Key Insights

1. **EAFP is Pythonic**: Python optimizes for exception handling, making try/except cheap
2. **LBYL has race conditions**: Checking before acting can fail if state changes between
3. **Context matters**: Some LBYL patterns are valid (e.g., type narrowing with isinstance)
4. **Conservative defaults**: isinstance and None checks disabled by default due to many valid uses

## Feature Vision

The LBYL linter aims to:

1. **Detect 8 LBYL anti-patterns** commonly produced by AI-generated code
2. **Provide actionable EAFP suggestions** with specific exception types
3. **Support configurable detection** to avoid false positives
4. **Integrate with CI/CD** via SARIF output
5. **Dogfood on thai-lint** to validate real-world effectiveness

## Current Application Context

### thai-lint Linter Architecture

- Linters extend `BaseLintRule` from `src/core/base.py`
- Rules are auto-discovered from `src/linters/` package
- Pattern detectors use `ast.NodeVisitor` for AST traversal
- Violations are `Violation` dataclasses from `src/core/types.py`
- Configuration uses dataclasses with `from_dict()` pattern

### Reference Implementation: stringly_typed

The stringly_typed linter provides the best reference pattern:
- `src/linters/stringly_typed/python/validation_detector.py` - AST NodeVisitor pattern
- `src/linters/stringly_typed/config.py` - Configuration with pattern toggles
- Uses dataclasses for detected patterns
- Provides suggestions for fixes

## Target Architecture

### Core Components

```
src/linters/lbyl/
├── __init__.py              # Package exports
├── config.py                # LBYLConfig dataclass
├── linter.py                # LBYLRule extending BaseLintRule
├── python_analyzer.py       # Coordinator for all detectors
├── violation_builder.py     # EAFP suggestion generator
└── pattern_detectors/
    ├── __init__.py
    ├── base.py              # BaseLBYLDetector abstract class
    ├── dict_key_detector.py
    ├── hasattr_detector.py
    ├── isinstance_detector.py
    ├── file_exists_detector.py
    ├── len_check_detector.py
    ├── none_check_detector.py
    ├── string_validator_detector.py
    └── division_check_detector.py
```

### Data Flow

```
Source Code
    ↓
ast.parse()
    ↓
PythonLBYLAnalyzer
    ↓
┌─────────────────────────────────────────┐
│ Pattern Detectors (based on config)     │
│ - DictKeyDetector                       │
│ - HasattrDetector                       │
│ - IsinstanceDetector (if enabled)       │
│ - FileExistsDetector                    │
│ - LenCheckDetector                      │
│ - NoneCheckDetector (if enabled)        │
│ - StringValidatorDetector               │
│ - DivisionCheckDetector                 │
└─────────────────────────────────────────┘
    ↓
List of LBYLPattern dataclasses
    ↓
LBYLViolationBuilder
    ↓
List of Violation objects
```

### User Journey

1. Developer runs `thailint lbyl src/`
2. Linter parses each Python file to AST
3. Enabled detectors identify LBYL patterns
4. Violations are generated with EAFP suggestions
5. Output in text/json/sarif format

### Pattern Detection Strategy

Each detector is an `ast.NodeVisitor` subclass that:
1. Visits specific node types (If, Compare, Call, etc.)
2. Checks for LBYL pattern structure
3. Validates that check and body use same variables
4. Returns dataclass representing detected pattern

## Key Decisions Made

### Decision 1: Python Only

**Choice**: Implement for Python only, not TypeScript

**Rationale**:
- EAFP is a Python-specific idiom
- TypeScript has different error handling patterns
- Keeps scope manageable for initial implementation

### Decision 2: Conservative Defaults

**Choice**: isinstance and None checks disabled by default

**Rationale**:
- isinstance is often used for valid type narrowing
- None checks are often intentional guard clauses
- Users can enable if they want stricter checking

### Decision 3: Separate Rule IDs

**Choice**: Use `lbyl.{pattern-type}` for each pattern

**Rationale**:
- Allows ignoring specific patterns
- Provides granular configuration
- Matches existing thai-lint conventions

### Decision 4: BaseLintRule (not MultiLanguageLintRule)

**Choice**: Extend BaseLintRule directly

**Rationale**:
- Python-only linter doesn't need multi-language dispatch
- Simpler implementation
- Still supports all required features

## Integration Points

### With Existing Features

1. **Output Formatting**: Uses existing text/json/sarif formatters
2. **Configuration**: Follows .thailint.yaml pattern
3. **Ignore Directives**: Supports `# thaiLint: ignore[lbyl]`
4. **CLI**: Registered as `thailint lbyl` command

### With Core Infrastructure

- `src/core/base.py`: BaseLintRule, BaseLintContext
- `src/core/types.py`: Violation dataclass
- `src/core/ignore_directive.py`: Ignore directive parsing

## Success Metrics

### Technical Metrics
- 150+ tests passing
- Pylint 10.00/10
- All code A-grade complexity
- Valid SARIF v2.1.0 output

### Feature Metrics
- All 8 LBYL patterns detected
- EAFP suggestions for each pattern
- Configurable pattern toggles
- Dogfooded on thai-lint codebase

## Technical Constraints

### AST Limitations
- Cannot detect runtime-only patterns
- F-string key matching requires AST comparison
- Import alias tracking needed for file_exists

### Performance Requirements
- Analysis time < 100ms per file
- Memory proportional to file size

### Quality Requirements
- Pylint 10.00/10
- Xenon A-grade complexity
- MyPy clean

## AI Agent Guidance

### When Implementing Detectors

1. **Start with tests** (TDD approach)
2. **Use stringly_typed as reference** for NodeVisitor pattern
3. **Return dataclasses** for detected patterns
4. **Include all context** needed for violation building

Example detector structure:
```python
class DictKeyDetector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.patterns: list[DictKeyPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[DictKeyPattern]:
        self.patterns = []
        self.visit(tree)
        return self.patterns

    def visit_If(self, node: ast.If) -> None:
        # Check for pattern
        # Add to self.patterns if found
        self.generic_visit(node)
```

### When Building Violations

1. **Use rule_id format**: `lbyl.{pattern-type}`
2. **Include actionable suggestion**: Specific try/except pattern
3. **Preserve context**: dict/key names, file path, line/column

Example:
```python
Violation(
    rule_id="lbyl.dict-key-check",
    message="LBYL pattern: checking 'key in data' before access",
    suggestion="Use try/except KeyError: try: value = data[key] except KeyError: ...",
    file_path=str(file_path),
    line=node.lineno,
    column=node.col_offset,
)
```

### Common Patterns

**AST Variable Matching**:
```python
def _get_name(node: ast.AST) -> str | None:
    """Extract variable name from AST node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_get_name(node.value)}.{node.attr}"
    return None
```

**Checking if Two Expressions Match**:
```python
def _expressions_match(expr1: ast.AST, expr2: ast.AST) -> bool:
    """Check if two AST expressions represent the same value."""
    return ast.dump(expr1) == ast.dump(expr2)
```

## Risk Mitigation

### False Positive Prevention

1. **Validate same variable**: Check and body must use same dict/key/obj/attr
2. **Exclude walrus operator**: `if (x := d.get(k))` is not LBYL
3. **Conservative defaults**: isinstance/None disabled by default
4. **Allow ignore directives**: Let users suppress specific violations

### Complexity Management

1. **Separate detectors**: Each pattern in its own class
2. **Common base class**: Share logic via BaseLBYLDetector
3. **ViolationBuilder**: Centralize message generation
4. **Config-driven**: Toggle patterns via configuration

## Future Enhancements

### Potential Additional Patterns
- `try`/`except` with bare except
- Empty except blocks
- Overly broad exception catching

### Potential Features
- Auto-fix capability (rewrite LBYL to EAFP)
- Cross-file pattern detection
- Custom pattern definitions

### TypeScript Support
If demand exists, could add detection for similar patterns:
- Type guards before operations
- Optional chaining alternatives
