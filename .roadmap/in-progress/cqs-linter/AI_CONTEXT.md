# CQS (Command-Query Separation) Linter - AI Context

**Purpose**: AI agent context document for implementing CQS Linter

**Scope**: Detect CQS violations where functions mix INPUT (queries) and OUTPUT (commands) in Python and TypeScript

**Overview**: Comprehensive context document for AI agents working on the CQS Linter feature.
    This linter implements the first automated CQS violation detector globally, identifying functions
    that violate Command-Query Separation by mixing query operations (INPUTs that retrieve data)
    with command operations (OUTPUTs that modify state).

**Dependencies**: ast module (Python), tree-sitter (TypeScript), src.core base classes

**Exports**: CQSRule, CQSConfig, CQSPattern, InputOperation, OutputOperation

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: AST-based analysis following LBYL linter pattern with TDD methodology

---

## Overview

The CQS (Command-Query Separation) Linter detects functions that violate the Command-Query Separation principle by mixing:

- **INPUT operations** (queries): Assignments from function calls that retrieve or compute values
- **OUTPUT operations** (commands): Statement-level function calls that modify state

A function that contains both INPUTs and OUTPUTs violates CQS and should be refactored into separate query and command functions.

## Project Background

### What is Command-Query Separation?

CQS is a design principle stating that every method should either:
1. **Query** - Return data without side effects, OR
2. **Command** - Modify state without returning data

Functions that do both are harder to reason about, test, and maintain.

### Why This Linter?

- No existing automated CQS detection tools exist globally
- Manual code review for CQS violations is error-prone
- CQS violations often indicate code that's doing too much
- Refactoring CQS violations improves testability and maintainability

## Feature Vision

1. **Automated Detection**: Identify CQS violations without manual review
2. **Actionable Feedback**: Provide line-specific details showing which operations violate CQS
3. **Configurable**: Allow teams to adjust sensitivity and ignore patterns
4. **Multi-Language**: Support both Python and TypeScript
5. **Integration**: Work with existing thai-lint CLI and output formats

## Current Application Context

### Existing Linter Pattern: LBYL

The LBYL (Look Before You Leap) linter at `src/linters/lbyl/` serves as the reference implementation:

```
src/linters/lbyl/
├── __init__.py              # Package exports
├── config.py                # LBYLConfig with from_dict()
├── linter.py                # LBYLRule(BaseLintRule)
├── python_analyzer.py       # PythonLBYLAnalyzer
├── violation_builder.py     # build_dict_key_violation()
└── pattern_detectors/
    ├── __init__.py
    ├── base.py              # BaseLBYLDetector, LBYLPattern
    └── dict_key_detector.py # DictKeyDetector
```

### Key Base Classes

- `BaseLintRule` (`src/core/base.py`): Abstract base for all linters
- `Violation` (`src/core/types.py`): Standard violation dataclass
- `load_linter_config` (`src/core/linter_utils.py`): Config loading helper

## Target Architecture

### Core Components

```
src/linters/cqs/
├── __init__.py              # Package exports: CQSRule, CQSConfig, etc.
├── types.py                 # InputOperation, OutputOperation, CQSPattern
├── config.py                # CQSConfig with from_dict()
├── linter.py                # CQSRule(BaseLintRule) - main entry point
├── python_analyzer.py       # PythonCQSAnalyzer - orchestrates Python analysis
├── typescript_analyzer.py   # TypeScriptCQSAnalyzer - orchestrates TS analysis
├── input_detector.py        # InputDetector(ast.NodeVisitor)
├── output_detector.py       # OutputDetector(ast.NodeVisitor)
├── function_analyzer.py     # FunctionAnalyzer - finds functions to analyze
└── violation_builder.py     # build_cqs_violation()
```

### Data Flow

```
File Content
    ↓
CQSRule.check(context)
    ↓
PythonCQSAnalyzer.analyze() or TypeScriptCQSAnalyzer.analyze()
    ↓
FunctionAnalyzer.find_functions()
    ↓
For each function:
    InputDetector.find_inputs()
    OutputDetector.find_outputs()
    ↓
    If both inputs AND outputs exist:
        Create CQSPattern
    ↓
violation_builder.build_cqs_violation()
    ↓
List[Violation]
```

### User Journey

1. User runs `thailint cqs src/`
2. CLI discovers Python and TypeScript files
3. CQSRule.check() analyzes each file
4. Violations reported with function name, line numbers, and suggestion
5. User refactors functions to separate queries from commands

## Key Decisions Made

### INPUT Operation Definition

An INPUT is an **assignment from a function call**:

```python
# These are INPUTs
x = fetch_data()           # Simple assignment
x, y = get_coordinates()   # Tuple unpacking
x = await fetch_async()    # Async assignment
self.data = load_config()  # Attribute assignment
```

### OUTPUT Operation Definition

An OUTPUT is a **statement-level function call** (not assigned, not in condition):

```python
# These are OUTPUTs
save_data(result)          # Statement call
await send_notification()  # Async statement
db.commit()                # Method call statement

# These are NOT OUTPUTs
return process(data)       # Return uses the value
if validate(data):         # Condition uses the value
x = compute(data)          # Assignment (this is INPUT)
```

### Default Ignores

Methods ignored by default (often legitimately mix operations):
- `__init__` - Constructors commonly fetch and store
- `__new__` - Object creation

Decorators ignored by default:
- `@property` - Properties should be pure queries
- `@cached_property` - Cached computation

### Fluent Interface Detection

Methods that `return self` are excluded from violation detection:
```python
class Builder:
    def with_name(self, name):
        self.name = validate(name)  # Would be INPUT+OUTPUT
        return self                  # Fluent pattern - exclude
```

## Integration Points

### With Existing Features

1. **CLI Framework** (`src/cli/linters/code_patterns.py`):
   - Add `cqs` command following `lbyl` pattern
   - Use `create_linter_command()` factory

2. **Config System** (`src/templates/thailint_config_template.yaml`):
   - Add CQS section with all options
   - `thailint init-config` generates CQS config

3. **Output Formatters** (`src/core/cli_utils.py`):
   - Use `format_violations()` for text/json/sarif output
   - SARIF must comply with v2.1.0

4. **Orchestrator** (`src/orchestrator/core.py`):
   - CQSRule auto-discovered via rule registry

## Success Metrics

| Metric | Target |
|--------|--------|
| Unit tests | 80+ passing |
| Integration tests | 20+ passing |
| SARIF tests | 15+ passing |
| Pylint score | 10.00/10 |
| MyPy errors | 0 |
| False positive rate | < 10% |

## Technical Constraints

1. **AST-Only Analysis**: No code execution, only static analysis
2. **Performance**: Single file < 100ms analysis time
3. **Error Handling**: Syntax errors return empty violations, no crashes
4. **Compatibility**: Python 3.10+, TypeScript via tree-sitter

## AI Agent Guidance

### When Implementing Detectors

1. Use `ast.NodeVisitor` pattern (see LBYL detectors)
2. Track line numbers from AST nodes (`node.lineno`, `node.col_offset`)
3. Use `ast.unparse()` to get expression strings (Python 3.9+)
4. Handle all assignment types: `Assign`, `AnnAssign`, `NamedExpr`

### When Building Violations

1. Use `Violation` dataclass from `src/core/types.py`
2. Rule ID format: `cqs.mixed-function`
3. Include suggestion in every violation
4. Message should explain what was detected

### Common Patterns

**Checking if a call is statement-level**:
```python
def visit_Expr(self, node: ast.Expr) -> None:
    if isinstance(node.value, (ast.Call, ast.Await)):
        # This is a statement-level call (OUTPUT candidate)
```

**Extracting function info**:
```python
def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
    name = node.name
    line = node.lineno
    is_async = isinstance(node, ast.AsyncFunctionDef)
    decorators = [self._get_decorator_name(d) for d in node.decorator_list]
```

**Detecting fluent interface**:
```python
def _is_fluent_return(self, node: ast.FunctionDef) -> bool:
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name):
            if stmt.value.id == 'self':
                return True
    return False
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| High false positive rate | Extensive external testing, configurable ignores |
| Edge cases missed | Comprehensive test suite (80+), iterative refinement |
| Constructor methods | Ignore `__init__`, `__new__` by default |
| Fluent interfaces | Detect `return self` pattern, exclude |
| Performance issues | Profile on large codebases, optimize hot paths |

## Future Enhancements

1. **Auto-fix suggestions**: Generate refactored code splitting query/command
2. **Cross-function analysis**: Detect CQS violations across call chains
3. **IDE integration**: Real-time CQS violation highlighting
4. **More languages**: Go, Rust, Java support
5. **Severity levels**: Warning for minor violations, error for severe
