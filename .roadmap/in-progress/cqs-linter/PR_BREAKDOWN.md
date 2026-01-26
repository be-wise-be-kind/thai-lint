# CQS (Command-Query Separation) Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of CQS Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from core infrastructure through documentation

**Overview**: Comprehensive breakdown of the CQS Linter feature into 8 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: ast module, tree-sitter, src.core base classes, LBYL linter as reference

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD approach with atomic PR structure and comprehensive testing validation

---

## Overview
This document breaks down the CQS Linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

**Total**: 80+ unit tests, 20+ integration tests, 15+ SARIF tests

---

## PR1: Core Infrastructure & Tests (TDD)

**Priority**: P0
**Complexity**: Medium
**Tests**: 35+ unit tests

### Scope
Create test files with failing tests, type definitions, and configuration. This is TDD - tests first.

### Files to Create

```
src/linters/cqs/
├── __init__.py
├── types.py              # InputOperation, OutputOperation, CQSPattern
└── config.py             # CQSConfig with from_dict()

tests/unit/linters/cqs/
├── __init__.py
├── conftest.py
├── test_config.py
├── test_input_detection.py
├── test_output_detection.py
├── test_cqs_violation.py
├── test_edge_cases.py
└── test_violation_builder.py
```

### Implementation Steps

1. **Create source directory structure**
   ```bash
   mkdir -p src/linters/cqs
   ```

2. **Create `types.py`** with:
   - `InputOperation` dataclass (line, column, expression, target)
   - `OutputOperation` dataclass (line, column, expression)
   - `CQSPattern` dataclass (function_name, line, column, file_path, inputs, outputs, is_method, is_async, class_name)
   - `has_violation()` method on CQSPattern
   - `get_full_name()` method on CQSPattern

3. **Create `config.py`** with:
   - `CQSConfig` dataclass with fields:
     - `enabled: bool = True`
     - `min_operations: int = 1`
     - `ignore_methods: list[str] = ["__init__", "__new__"]`
     - `ignore_decorators: list[str] = ["property", "cached_property"]`
     - `ignore_patterns: list[str] = []`
     - `detect_fluent_interface: bool = True`
   - `from_dict()` class method for YAML loading

4. **Create `__init__.py`** with exports

5. **Create test directory structure**
   ```bash
   mkdir -p tests/unit/linters/cqs
   ```

6. **Create `conftest.py`** with:
   - `create_mock_context()` helper function
   - `mock_context` fixture factory
   - `default_config` fixture
   - `strict_config` fixture (no ignores)
   - Test data constants for CQS violations and valid patterns

7. **Create test files** with TDD tests (marked with `@pytest.mark.skip`):
   - `test_config.py`: Config defaults, from_dict loading
   - `test_input_detection.py`: INPUT pattern detection tests
   - `test_output_detection.py`: OUTPUT pattern detection tests
   - `test_cqs_violation.py`: Violation detection tests
   - `test_edge_cases.py`: Edge cases and error handling
   - `test_violation_builder.py`: Violation message building tests

### Testing Requirements
- All tests should be marked with `@pytest.mark.skip(reason="TDD: Not yet implemented - cqs PR1")`
- Config tests should pass (not skipped)
- Pattern tests should define expected behavior but skip execution

### Success Criteria
- [ ] All test files created with proper headers
- [ ] Tests fail with ImportError or skip (TDD)
- [ ] Config has `from_dict()` for YAML loading
- [ ] Pylint 10.00/10 on new files
- [ ] Ruff passes

---

## PR2: Python INPUT/OUTPUT Detection

**Priority**: P0
**Complexity**: High
**Tests**: 25+ unit tests

### Scope
AST-based detection of INPUT and OUTPUT operations in Python code.

### Files to Create

```
src/linters/cqs/
├── python_analyzer.py
├── input_detector.py
└── output_detector.py
```

### INPUT Patterns to Detect
- `x = func()` - Simple assignment from call
- `x, y = func()` - Tuple unpacking from call
- `x = await func()` - Async assignment
- `self.x = func()` - Attribute assignment from call
- `x[key] = func()` - Subscript assignment from call

### OUTPUT Patterns to Detect
- `func()` - Statement-level call
- `await func()` - Async statement call
- `obj.method()` - Method call as statement

### NOT OUTPUT Patterns (important exclusions)
- `return func()` - Return statement uses value
- `if func():` - Conditional uses value
- `x = func()` - Assignment (this is INPUT)
- `[func(x) for x in items]` - Comprehension

### Implementation Steps

1. **Create `input_detector.py`**:
   - Class `InputDetector(ast.NodeVisitor)`
   - Method `find_inputs(tree: ast.AST) -> list[InputOperation]`
   - Handle `ast.Assign`, `ast.AnnAssign`, `ast.NamedExpr`
   - Extract target name(s) and call expression

2. **Create `output_detector.py`**:
   - Class `OutputDetector(ast.NodeVisitor)`
   - Method `find_outputs(tree: ast.AST) -> list[OutputOperation]`
   - Handle `ast.Expr` containing `ast.Call` or `ast.Await`
   - Exclude calls in return, if, while, for conditions

3. **Create `python_analyzer.py`**:
   - Class `PythonCQSAnalyzer`
   - Coordinate InputDetector and OutputDetector
   - Parse AST with error handling
   - Method `analyze(code: str, file_path: str, config: CQSConfig) -> list[CQSPattern]`

4. **Remove skip markers** from INPUT/OUTPUT detection tests

### Success Criteria
- [ ] InputDetector identifies 10+ patterns
- [ ] OutputDetector identifies 10+ patterns
- [ ] All INPUT detection tests pass
- [ ] All OUTPUT detection tests pass
- [ ] Pylint 10.00/10

---

## PR3: Python CQS Violation Detection

**Priority**: P0
**Complexity**: High
**Tests**: 25+ unit tests

### Scope
Main CQS violation detection logic - finding functions that mix INPUTs and OUTPUTs.

### Files to Create

```
src/linters/cqs/
├── linter.py              # CQSRule (BaseLintRule)
├── function_analyzer.py
└── violation_builder.py
```

### Violation Message Format
```
cqs.mixed-function  src/service.py:45:1  ERROR
  Function 'process_and_save' violates CQS: mixes queries and commands
  INPUTS: Line 47: data = fetch_data(id)
  OUTPUTS: Line 50: save_to_db(data)
  Suggestion: Split into query and command functions
```

### Implementation Steps

1. **Create `function_analyzer.py`**:
   - Class `FunctionAnalyzer(ast.NodeVisitor)`
   - Visit `ast.FunctionDef` and `ast.AsyncFunctionDef`
   - Track class context for methods
   - Check decorators against ignore list
   - Detect fluent interface pattern (`return self`)

2. **Create `violation_builder.py`**:
   - Function `build_cqs_violation(pattern: CQSPattern) -> Violation`
   - Include function name, class name for methods
   - List INPUT operations with line numbers
   - List OUTPUT operations with line numbers
   - Provide suggestion to split

3. **Create `linter.py`**:
   - Class `CQSRule(BaseLintRule)`
   - Properties: `rule_id = "cqs"`, `rule_name`, `description`
   - Method `check(context: BaseLintContext) -> list[Violation]`
   - Load config via `load_linter_config`
   - Filter by `ignore_methods` and `ignore_decorators`
   - Respect `min_operations` threshold

4. **Update `__init__.py`** with CQSRule export

5. **Remove skip markers** from violation detection tests

### Success Criteria
- [ ] Detects simple CQS violations
- [ ] Handles class methods, nested functions, async
- [ ] Violation messages include line-specific details
- [ ] Respects configuration options
- [ ] All violation tests pass
- [ ] Pylint 10.00/10

---

## PR4: TypeScript Detection Support

**Priority**: P0
**Complexity**: Medium
**Tests**: 20+ unit tests

### Scope
Add TypeScript CQS detection using tree-sitter.

### Files to Create

```
src/linters/cqs/
└── typescript_analyzer.py
```

### TypeScript Patterns

**INPUT Patterns**:
- `const x = func()` / `let x = func()` → INPUT
- `const { a, b } = func()` → INPUT (destructuring)
- `const [a, b] = func()` → INPUT (array destructuring)

**OUTPUT Patterns**:
- `func();` → OUTPUT (expression statement)
- `await func();` → OUTPUT (await statement)

### Implementation Steps

1. **Create `typescript_analyzer.py`**:
   - Class `TypeScriptCQSAnalyzer`
   - Use tree-sitter for parsing (follow existing TS analyzer patterns)
   - Method `analyze(code: str, file_path: str, config: CQSConfig) -> list[CQSPattern]`
   - Handle `.ts` and `.tsx` files

2. **Update `linter.py`**:
   - Add TypeScript language support in `check()` method
   - Dispatch to TypeScriptCQSAnalyzer for TS/TSX files

3. **Create TypeScript test fixtures** in conftest.py

4. **Remove skip markers** from TypeScript tests

### Success Criteria
- [ ] TypeScript INPUT/OUTPUT detection works
- [ ] Handles .ts and .tsx files
- [ ] 20+ TypeScript tests pass
- [ ] Pylint 10.00/10

---

## PR5: CLI Integration & Output Formats

**Priority**: P0
**Complexity**: Medium
**Tests**: 15+ integration tests

### Scope
CLI command, output formats, and init-config update.

### Files to Modify

```
src/cli/linters/code_patterns.py           # Add cqs command
src/templates/thailint_config_template.yaml # Add CQS config section
```

### CLI Specification
```bash
thailint cqs [OPTIONS] [PATHS]...
  --format, -f [text|json|sarif]
  --config, -c PATH
  --recursive/--no-recursive
```

### Config Template Addition
```yaml
# ============================================================================
# CQS (COMMAND-QUERY SEPARATION) LINTER
# ============================================================================
cqs:
  enabled: true
  min_operations: 1
  ignore_methods:
    - "__init__"
    - "__new__"
  ignore_decorators:
    - property
    - cached_property
```

### Implementation Steps

1. **Add CLI command** in `code_patterns.py`:
   - Follow existing pattern (see `lbyl` command)
   - Create `_setup_cqs_orchestrator()`
   - Create `_run_cqs_lint()`
   - Create `_execute_cqs_lint()`
   - Register with `create_linter_command()`

2. **Update config template**:
   - Add CQS section with all options
   - Include helpful comments

3. **Create integration tests**:
   - Test CLI invocation
   - Test all output formats
   - Test config loading

4. **Verify SARIF output** complies with v2.1.0

### Success Criteria
- [ ] `thailint cqs src/` works
- [ ] All 3 output formats produce valid output
- [ ] SARIF v2.1.0 compliant
- [ ] `thailint init-config` includes CQS section
- [ ] 15+ integration tests pass

---

## PR6: Dogfooding - Internal Validation

**Priority**: P1
**Complexity**: Low
**Tests**: 5+ validation tests

### Scope
Run CQS linter on thai-lint itself.

### Files to Modify

```
justfile                    # Add cqs to lint-full
AGENTS.md                   # Update with new linter info
```

### Process

1. Run `thailint cqs src/`
2. Fix real violations or document justified ones
3. Add to `just lint-full` target

### Implementation Steps

1. **Run CQS linter** on thai-lint codebase
2. **Analyze results**:
   - True positives: Fix the code
   - False positives: Add to ignore list or fix detection
   - Edge cases: Document in AI_CONTEXT.md
3. **Update justfile** to include CQS in lint-full
4. **Update AGENTS.md** with new linter documentation

### Success Criteria
- [ ] `thailint cqs src/` passes (or violations documented)
- [ ] `just lint-full` includes CQS check
- [ ] No false positives in thai-lint codebase

---

## PR7: False Positive External Validation

**Priority**: P1
**Complexity**: Medium
**Deliverable**: Validation report

### Scope
Test against external repos for false positives.

### Target Repos (Python)
- `requests` - HTTP library
- `flask` - Web framework
- `fastapi` - Modern async framework
- `httpx` - HTTP client

### Deliverable
`.roadmap/in-progress/cqs-linter/external-validation-report.md`

### Process

1. Clone each repo to temp directory
2. Run `thailint cqs` on each
3. Sample and categorize violations:
   - True positive: Real CQS violation
   - False positive: Incorrect detection
   - Debatable: Valid detection but acceptable pattern
4. Calculate false positive rate
5. Adjust config defaults if needed

### Success Criteria
- [ ] Tested against 4+ external repos
- [ ] False positive rate < 10%
- [ ] Validation report with findings
- [ ] Config adjustments if needed

---

## PR8: Documentation & PyPI Prep

**Priority**: P2
**Complexity**: Low

### Scope
Complete user documentation.

### Files to Create/Modify

```
docs/cqs-linter.md          # User documentation
README.md                   # Add CQS to feature list
CHANGELOG.md                # Feature entry
```

### Documentation Contents

1. **What is CQS?**
   - Command-Query Separation principle explanation
   - Why it matters for code quality

2. **What it detects**
   - INPUT patterns (queries)
   - OUTPUT patterns (commands)
   - Mixed function detection

3. **Configuration options**
   - All config fields with examples
   - When to adjust defaults

4. **Before/after refactoring examples**
   - Python examples
   - TypeScript examples

### Implementation Steps

1. **Create `docs/cqs-linter.md`** with full documentation
2. **Update README.md** feature list
3. **Add CHANGELOG.md** entry

### Success Criteria
- [ ] Complete user documentation
- [ ] README updated
- [ ] CHANGELOG entry added

---

## Implementation Guidelines

### Code Standards
- Follow LBYL linter pattern exactly
- All files must have proper file headers (see `.ai/docs/FILE_HEADER_STANDARDS.md`)
- Pylint 10.00/10 required
- MyPy zero errors required

### Testing Requirements
- TDD: Write tests before implementation
- Unit tests for all detection logic
- Integration tests for CLI
- SARIF compliance tests

### Documentation Standards
- File headers on all new files
- Docstrings on all public functions/classes
- User documentation in docs/

### Security Considerations
- No code execution, AST analysis only
- Handle malformed input gracefully

### Performance Targets
- Single file analysis < 100ms
- Batch processing with parallel support

## Rollout Strategy

1. **PR1-PR3**: Core Python functionality
2. **PR4**: TypeScript support
3. **PR5**: CLI integration (feature usable)
4. **PR6-PR7**: Validation and refinement
5. **PR8**: Documentation (feature complete)

## Success Metrics

### Launch Metrics
- 80+ unit tests passing
- 20+ integration tests passing
- `thailint cqs` command functional

### Ongoing Metrics
- False positive rate < 10%
- `just lint-full` passing
- User documentation complete
