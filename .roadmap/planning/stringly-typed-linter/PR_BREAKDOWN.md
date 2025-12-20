# Stringly-Typed Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of stringly-typed linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from infrastructure through dogfooding

**Overview**: Comprehensive breakdown of the stringly-typed linter feature into 10 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: MultiLanguageLintRule, SQLite, tree-sitter, Click CLI

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the stringly-typed linter feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## PR1: Infrastructure & Test Framework

**Scope**: Create module structure, config dataclass, and test fixtures

**Complexity**: Low

**Files to Create**:
```
src/linters/stringly_typed/
├── __init__.py
├── config.py
└── config_loader.py

tests/unit/linters/stringly_typed/
├── __init__.py
├── conftest.py
└── test_config_loading.py
```

**Steps**:
1. Create `src/linters/stringly_typed/` directory
2. Create `config.py` with `StringlyTypedConfig` dataclass:
   - `enabled: bool = True`
   - `min_occurrences: int = 2`
   - `min_values_for_enum: int = 2`
   - `max_values_for_enum: int = 6`
   - `require_cross_file: bool = True`
   - `ignore: list[str] = field(default_factory=list)`
   - `allowed_string_sets: list[list[str]] = field(default_factory=list)`
   - `exclude_variables: list[str] = field(default_factory=list)`
3. Create `config_loader.py` with `load_stringly_typed_config()` function
4. Create test fixtures in `conftest.py`
5. Write tests for config loading, defaults, validation

**Testing Requirements**:
- Test default config values
- Test loading from YAML dict
- Test language-specific config overrides
- Test validation of numeric constraints

**Success Criteria**:
- [ ] Config dataclass defined with all fields
- [ ] Config loader works with YAML input
- [ ] All tests pass
- [ ] Pylint 10.00/10
- [ ] Xenon A-grade

---

## PR2: Python Pattern 1 - Membership Validation

**Scope**: Detect `x in ('a', 'b')` and `x not in (...)` patterns in Python

**Complexity**: Medium

**Files to Create**:
```
src/linters/stringly_typed/python/
├── __init__.py
├── analyzer.py
└── validation_detector.py

tests/unit/linters/stringly_typed/
└── test_python_validation_patterns.py
```

**Steps**:
1. Create `validation_detector.py` with AST visitor:
   - Detect `Compare` nodes with `In`/`NotIn` operators
   - Extract string values from `Tuple`/`Set`/`List` comparators
   - Track variable name and location
2. Create `analyzer.py` that coordinates detection
3. Write comprehensive tests (TDD first)

**AST Patterns to Match**:
```python
# Pattern: Compare(left=Name, ops=[In/NotIn], comparators=[Tuple/Set/List])
if x in ("a", "b"):          # Match
if x not in {"staging"}:     # Match
if x in ["success", "fail"]: # Match
if x in range(10):           # Don't match (not strings)
```

**Testing Requirements**:
- Test `in` with tuple
- Test `not in` with set
- Test with list
- Test complex left-hand side (`x.lower() in (...)`)
- Test false positives: non-string collections, single-element sets

**Success Criteria**:
- [ ] Detects all membership validation patterns
- [ ] Extracts string values correctly
- [ ] Ignores non-string collections
- [ ] All tests pass

---

## PR3: Python Pattern 2 - Equality Chains

**Scope**: Detect `x == 'a'` and chained comparisons

**Complexity**: Medium

**Files to Create**:
```
src/linters/stringly_typed/python/
└── conditional_detector.py

tests/unit/linters/stringly_typed/
└── test_python_conditional_patterns.py
```

**Steps**:
1. Create `conditional_detector.py` with AST visitor:
   - Detect `Compare` nodes with `Eq`/`NotEq` and string `Constant`
   - Track if/elif chains for grouped comparisons
   - Handle `match` statements (Python 3.10+)
2. Aggregate string values from related comparisons
3. Write comprehensive tests (TDD first)

**AST Patterns to Match**:
```python
# Single comparison
if status == "success":       # Start of chain

# elif chain (aggregate values)
if status == "success":
elif status == "failure":     # {"success", "failure"}
elif status == "pending":     # {"success", "failure", "pending"}

# Or-combined
if x == "a" or x == "b":      # {"a", "b"}

# Match statement (Python 3.10+)
match status:
    case "success": ...
    case "failure": ...       # {"success", "failure"}
```

**Testing Requirements**:
- Test single equality comparison
- Test elif chains (aggregate values)
- Test or-combined comparisons
- Test match statements
- Test mixed comparison types in same function

**Success Criteria**:
- [ ] Detects single string comparisons
- [ ] Aggregates elif chain values
- [ ] Handles match statements
- [ ] All tests pass

---

## PR4: TypeScript Single-File Detection

**Scope**: TypeScript patterns for membership and equality

**Complexity**: Medium

**Files to Create**:
```
src/linters/stringly_typed/typescript/
├── __init__.py
├── analyzer.py
├── validation_detector.py
└── conditional_detector.py

tests/unit/linters/stringly_typed/
└── test_typescript_patterns.py
```

**Steps**:
1. Create `validation_detector.py` using tree-sitter:
   - Detect `array.includes()` calls
   - Extract string values from array literals
2. Create `conditional_detector.py`:
   - Detect `===` comparisons with string literals
   - Detect switch statements with string cases
3. Handle type unions (should NOT flag - already typed)
4. Write comprehensive tests (TDD first)

**Tree-sitter Patterns to Match**:
```typescript
// Array.includes()
if (!["staging", "production"].includes(env)) { }

// Triple-equals
if (status === "success") { }

// Switch statement
switch (mode) {
    case "debug": ...
    case "release": ...
}

// Type union - DO NOT FLAG (already typed)
type Mode = "debug" | "release";
function process(mode: "debug" | "release") { }
```

**Testing Requirements**:
- Test Array.includes() detection
- Test === comparison detection
- Test switch statement detection
- Test type unions are NOT flagged
- Test template literals are ignored

**Success Criteria**:
- [ ] Detects TypeScript membership patterns
- [ ] Detects switch statements
- [ ] Does NOT flag type unions
- [ ] All tests pass

---

## PR5: Cross-File Storage & Detection

**Scope**: SQLite storage and finalize() for cross-file analysis

**Complexity**: High

**Files to Create**:
```
src/linters/stringly_typed/
├── storage.py
├── storage_initializer.py
├── linter.py
└── violation_generator.py

tests/unit/linters/stringly_typed/
└── test_cross_file_detection.py
```

**Steps**:
1. Create `storage.py` with SQLite schema:
   - `string_validations` table (file_path, line, variable, string_set_hash, values)
   - Query methods for finding duplicates
2. Create `storage_initializer.py` for database setup
3. Create `linter.py` implementing `MultiLanguageLintRule`:
   - `check()` collects data into storage
   - `finalize()` queries for cross-file duplicates
4. Create `violation_generator.py` to create violations from analysis

**Storage Schema**:
```sql
CREATE TABLE string_validations (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT,
    string_set_hash INTEGER NOT NULL,
    string_values TEXT NOT NULL,  -- JSON array
    pattern_type TEXT NOT NULL,
    UNIQUE(file_path, line_number)
);

CREATE INDEX idx_string_hash ON string_validations(string_set_hash);
```

**Testing Requirements**:
- Test storage insert and query
- Test same validation in 2 files
- Test same validation in 3+ files
- Test hash collision handling
- Test cache clearing between runs

**Success Criteria**:
- [ ] Storage correctly tracks string validations
- [ ] finalize() finds cross-file duplicates
- [ ] Violations generated for repeated patterns
- [ ] All tests pass

---

## PR6: Function Call Tracking (Pattern 3)

**Scope**: Track function calls to detect limited string values

**Complexity**: High

**Files to Create**:
```
src/linters/stringly_typed/python/
└── call_tracker.py

src/linters/stringly_typed/typescript/
└── call_tracker.py

tests/unit/linters/stringly_typed/
└── test_call_tracking.py
```

**Steps**:
1. Create Python `call_tracker.py`:
   - Track function calls with string arguments
   - Store: function_name, param_index, string_value
2. Create TypeScript `call_tracker.py`:
   - Same pattern using tree-sitter
3. Update `finalize()` to aggregate call tracking:
   - Group by function_name + param_index
   - Flag if unique values in [min_values, max_values] range

**Storage Addition**:
```sql
CREATE TABLE function_calls (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    function_name TEXT NOT NULL,
    param_index INTEGER NOT NULL,
    string_value TEXT NOT NULL
);

CREATE INDEX idx_function_param ON function_calls(function_name, param_index);
```

**Testing Requirements**:
- Test function called with 2 unique strings (flag)
- Test function called with 4 unique strings (flag)
- Test function called with 7 unique strings (don't flag - too many)
- Test cross-file call aggregation
- Test method calls vs function calls

**Success Criteria**:
- [ ] Tracks function calls with string args
- [ ] Aggregates unique values across files
- [ ] Respects min/max_values_for_enum config
- [ ] All tests pass

---

## PR7: CLI Integration & Output Formats

**Scope**: CLI command and SARIF/JSON/text output

**Complexity**: Medium

**Files to Create**:
```
src/linters/stringly_typed/
└── violation_builder.py

tests/unit/linters/stringly_typed/
├── test_cli_interface.py
└── test_output_formats.py
```

**Files to Modify**:
- `src/cli.py` - Add `stringly-typed` command

**Steps**:
1. Add CLI command following existing pattern:
   ```python
   @cli.command("stringly-typed")
   @click.argument("paths", nargs=-1, type=click.Path(exists=True))
   @click.option("--config-file", type=click.Path(exists=True))
   @click.option("--format", type=click.Choice(["text", "json", "sarif"]))
   @click.option("--recursive/--no-recursive", default=True)
   def stringly_typed(ctx, paths, config_file, format, recursive):
       ...
   ```
2. Create `violation_builder.py` with rule_id patterns:
   - `stringly-typed.repeated-validation`
   - `stringly-typed.equality-chain`
   - `stringly-typed.limited-values`
3. Implement SARIF output per `.ai/docs/SARIF_STANDARDS.md`

**Testing Requirements**:
- Test CLI invocation with paths
- Test `--format text` output
- Test `--format json` output
- Test `--format sarif` output validates against schema
- Test exit code 1 when violations found

**Success Criteria**:
- [ ] CLI command works
- [ ] All three output formats work
- [ ] SARIF validates against schema
- [ ] Exit codes correct
- [ ] All tests pass

---

## PR8: False Positive Filtering

**Scope**: Context-aware filtering to reduce noise

**Complexity**: Medium

**Files to Create**:
```
src/linters/stringly_typed/
└── context_filter.py

tests/unit/linters/stringly_typed/
└── test_false_positives.py
```

**Steps**:
1. Create `context_filter.py` with exclusion logic:
   - Logging context (detect logger.info, console.log)
   - Error messages (raise/throw with string)
   - Dictionary keys (dict literals, TypedDict)
   - Format strings (f-strings, template literals)
   - URL/path patterns
2. Apply filter before generating violations
3. Make filters configurable

**Exclusion Patterns**:
```python
# Logging - exclude
logger.info("Processing %s", status)

# Error messages - exclude
raise ValueError(f"Invalid status: {status}")

# Dictionary keys - exclude
config = {"staging": {...}, "production": {...}}

# Format strings - exclude
message = f"Status is {status}"
```

**Testing Requirements**:
- Test logging context exclusion
- Test error message exclusion
- Test dictionary key exclusion
- Test format string exclusion
- Test URL/path pattern exclusion
- Test that real violations still detected

**Success Criteria**:
- [ ] False positives filtered out
- [ ] True violations still detected
- [ ] Filters are configurable
- [ ] All tests pass

---

## PR9: Ignore Directives

**Scope**: Inline ignore support

**Complexity**: Low

**Files to Create**:
```
src/linters/stringly_typed/
└── ignore_checker.py

tests/unit/linters/stringly_typed/
└── test_ignore_directives.py
```

**Steps**:
1. Create `ignore_checker.py`:
   - Parse `# thailint: ignore[stringly-typed]` comments
   - Support line-level, block-level, file-level ignores
2. Apply ignore check before generating violations

**Ignore Patterns**:
```python
# Line-level
if env in ("staging", "production"):  # thailint: ignore[stringly-typed]

# Block-level (applies to next statement)
# thailint: ignore[stringly-typed]
if status == "success":
    ...

# File-level (at top of file)
# thailint: ignore-file[stringly-typed]
```

**Testing Requirements**:
- Test line-level ignore
- Test block-level ignore
- Test file-level ignore
- Test rule-specific vs generic ignore
- Test ignore with reason comment

**Success Criteria**:
- [ ] Line-level ignores work
- [ ] Block-level ignores work
- [ ] File-level ignores work
- [ ] All tests pass

---

## PR10: Dogfooding & Documentation

**Scope**: Run on real codebases and create documentation

**Complexity**: Low

**Files to Create**:
```
docs/stringly-typed.md
.roadmap/in-progress/stringly-typed-linter/DOGFOOD_REPORT.md
```

**Files to Modify**:
- `README.md` - Add linter to list

**Steps**:
1. Run on thai-lint codebase:
   ```bash
   thailint stringly-typed src/ --format text
   ```
2. Run on tb-automation-py codebase
3. Document findings in `DOGFOOD_REPORT.md`
4. Tune false positive filters based on results
5. Create user documentation in `docs/stringly-typed.md`
6. Update README.md

**Documentation Sections**:
- What it detects
- Configuration options
- Example violations
- How to fix
- Ignore directives

**Success Criteria**:
- [ ] Runs successfully on thai-lint
- [ ] Runs successfully on tb-automation-py
- [ ] False positive rate <5%
- [ ] Documentation complete
- [ ] README updated

---

## Implementation Guidelines

### Code Standards
- Follow PEP 8 (enforced by Ruff)
- Type hints required (checked by MyPy)
- Google-style docstrings
- Maximum cyclomatic complexity: A (enforced by Xenon)

### Testing Requirements
- TDD approach: write tests first
- Unit tests in `tests/unit/linters/stringly_typed/`
- Fixtures in `conftest.py`
- 87%+ code coverage target

### Documentation Standards
- File headers per `.ai/docs/FILE_HEADER_STANDARDS.md`
- Atemporal language only
- Google-style docstrings

### Security Considerations
- No secrets in test fixtures
- Sanitize file paths in output

### Performance Targets
- Single file analysis: <100ms
- Cross-file finalize: <1s for 100 files

## Rollout Strategy

### Phase 1: Planning
- Create roadmap documents
- Move to `.roadmap/in-progress/`

### Phase 2: Core Implementation (PR1-PR5)
- Foundation and basic detection
- Cross-file storage

### Phase 3: Polish (PR6-PR9)
- Advanced detection
- False positive filtering
- Ignore support

### Phase 4: Release (PR10)
- Dogfooding
- Documentation
- Move to `.roadmap/complete/`

## Success Metrics

### Launch Metrics
- All tests pass
- Pylint 10.00/10
- Xenon A-grade
- SARIF validates

### Ongoing Metrics
- False positive rate <5%
- Detection accuracy >95%
- Performance within targets
