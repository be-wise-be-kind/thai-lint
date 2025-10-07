# Nesting Depth Violations - Dogfooding Discovery (PR4)

**Purpose**: Catalog all nesting depth violations found in thai-lint codebase at max_nesting_depth=3

**Scope**: Discovery phase for PR4 - identifying violations, categorizing by complexity, and planning refactoring strategy for PR5/PR6

**Date**: 2025-10-07
**Configuration**: max_nesting_depth = 3 (updated from default 4)
**Total Violations**: 18 functions with depth=4

---

## Executive Summary

**Status**: ✅ All violations cataloged and categorized
**Current State**: 18 functions at nesting depth 4 (violating max=3)
**Severity**: Low - all violations are at depth 4 (just 1 level over limit)
**Refactoring Strategy**: Split evenly across PR5 (9 functions) and PR6 (9 functions)

**Key Findings**:
- All violations are depth 4 (no extreme cases at depth 5+)
- Most violations are in CLI/config formatting code (easy refactors)
- Some violations in core orchestrator logic (moderate refactors)
- Common pattern: nested if-elif-else chains (simple to flatten)

---

## Violation Categories

### Easy Refactors (Depth 4, Simple Pattern) - 9 violations
**Characteristics**: If-elif-else chains, simple nested loops, minimal business logic
**Refactoring Strategy**: Guard clauses, early returns, extract helper functions
**Estimated Effort**: 15-30 min per function
**Target**: PR5

| File | Line | Function | Current Depth | Pattern | Refactoring Approach |
|------|------|----------|---------------|---------|---------------------|
| src/cli.py | 162 | `config_show` | 4 | if-elif-else chain (format selection) | Extract format handlers to separate functions |
| src/cli.py | 432 | `_write_layout_config` | 4 | if-elif nested with try-except | Early return on format check, flatten try-except |
| src/cli.py | 525 | `_output_text` | 4 | nested if-elif-else (format + data check) | Extract formatters, use guard clauses |
| src/config.py | 187 | `_write_config_file` | 4 | if-elif-else chain (format selection) | Extract format writers, use strategy pattern |
| src/config.py | 198 | `save_config` | 4 | nested if checks with file operations | Extract file writer, use guard clauses |
| src/orchestrator/core.py | 67 | `file_content` (property) | 4 | if-and-and with try-except | Early return pattern, simplify conditions |
| src/orchestrator/language_detector.py | 40 | `_detect_from_shebang` | 4 | nested with + for + if | Extract shebang parsing, use early returns |
| src/linters/nesting/linter.py | 119 | `_check_functions` | 4 | for + if + for + if | Extract violation checking to helper |
| src/linters/file_placement/linter.py | 558 | `_load_layout_config` | 4 | nested if with file checks | Guard clauses, extract config loader |

### Moderate Refactors (Depth 4, Complex Logic) - 9 violations
**Characteristics**: Core business logic, error handling, orchestration code
**Refactoring Strategy**: Extract complex blocks to helper methods, use early returns
**Estimated Effort**: 30-45 min per function
**Target**: PR6

| File | Line | Function | Current Depth | Pattern | Refactoring Approach |
|------|------|----------|---------------|---------|---------------------|
| src/cli.py | 345 | `file_placement` | 4 | Complex CLI with try-except + conditions | Extract linting logic, simplify error handling |
| src/cli.py | 458 | `_load_config_file` | 4 | Nested file ops with try-except | Extract config loading, use early returns |
| src/cli.py | 585 | `nesting` | 4 | Complex CLI with try-except + conditions | Extract linting logic (mirror file_placement) |
| src/config.py | 98 | `_load_from_default_locations` | 4 | for loop with nested if-elif-else | Extract location checker, use early returns |
| src/config.py | 153 | `_load_config_file` | 4 | if-elif-else with file parsing | Extract parsers, use strategy pattern |
| src/orchestrator/core.py | 110 | `lint_file` | 4 | Core linting with try-except loop | Extract rule executor, simplify error handling |
| src/core/registry.py | 84 | `discover_rules` | 4 | try-except with for + try-except | Extract module iterator, improve error handling |
| src/core/registry.py | 121 | `_discover_from_module` | 4 | try-except with for + if checks | Extract rule registration, use guard clauses |
| src/linters/file_placement/linter.py | 491 | `lint_directory` | 4 | for loop with nested if + try-except | Extract file processor, simplify error handling |

---

## Detailed Violation Analysis

### 1. src/cli.py:162 - `config_show` (EASY)

**Current Depth**: 4
**Location**: CLI config display command
**Pattern**: if-elif-else format selection chain

```python
def config_show(ctx, format: str):
    cfg = ctx.obj["config"]

    if format == "json":      # Depth 2
        import json
        click.echo(json.dumps(cfg, indent=2))
    elif format == "yaml":    # Depth 2
        import yaml
        click.echo(yaml.dump(cfg, default_flow_style=False, sort_keys=False))
    else:                      # Depth 2
        click.echo("Current Configuration:")
        click.echo("-" * 40)
        for key, value in cfg.items():  # Depth 3
            click.echo(f"{key:20} : {value}")  # Depth 4
```

**Refactoring Strategy**:
- Extract format handlers: `_format_json()`, `_format_yaml()`, `_format_text()`
- Use dictionary dispatch or separate functions
- Eliminate nested loop by extracting text formatter

**Estimated Effort**: 15 minutes

---

### 2. src/cli.py:345 - `file_placement` (MODERATE)

**Current Depth**: 4
**Location**: CLI file-placement command
**Pattern**: Complex CLI with orchestration + error handling

**Refactoring Strategy**:
- Extract `_execute_file_placement_lint()` helper
- Simplify error handling with guard clauses
- Move output formatting to separate function

**Estimated Effort**: 35 minutes

---

### 3. src/cli.py:432 - `_write_layout_config` (EASY)

**Current Depth**: 4
**Location**: CLI helper for writing layout config
**Pattern**: if-elif with nested try-except

**Refactoring Strategy**:
- Extract format writers: `_write_json()`, `_write_yaml()`
- Use early return on format validation
- Flatten try-except blocks

**Estimated Effort**: 20 minutes

---

### 4. src/cli.py:458 - `_load_config_file` (MODERATE)

**Current Depth**: 4
**Location**: CLI helper for loading config
**Pattern**: Nested file operations with error handling

**Refactoring Strategy**:
- Extract config loading to `_read_and_parse_config()`
- Use early returns for validation
- Simplify error handling

**Estimated Effort**: 30 minutes

---

### 5. src/cli.py:525 - `_output_text` (EASY)

**Current Depth**: 4
**Location**: CLI output formatting helper
**Pattern**: Nested if-elif-else with data checks

**Refactoring Strategy**:
- Extract `_format_violation()` helper
- Use guard clauses for data validation
- Flatten conditional chains

**Estimated Effort**: 20 minutes

---

### 6. src/cli.py:585 - `nesting` (MODERATE)

**Current Depth**: 4
**Location**: CLI nesting command
**Pattern**: Complex CLI with orchestration (mirrors file_placement)

**Refactoring Strategy**:
- Extract `_execute_nesting_lint()` helper (mirror file_placement approach)
- Simplify error handling
- Consistent with file_placement refactoring

**Estimated Effort**: 35 minutes

---

### 7. src/config.py:98 - `_load_from_default_locations` (MODERATE)

**Current Depth**: 4
**Location**: Config loader helper
**Pattern**: for loop with nested if-elif-else

**Refactoring Strategy**:
- Extract `_try_load_location()` helper
- Use early returns in loop
- Simplify format detection

**Estimated Effort**: 30 minutes

---

### 8. src/config.py:153 - `_load_config_file` (MODERATE)

**Current Depth**: 4
**Location**: Config file parser
**Pattern**: if-elif-else with file parsing logic

**Refactoring Strategy**:
- Extract parsers: `_parse_json()`, `_parse_yaml()`
- Use strategy pattern or dispatch table
- Simplify error handling

**Estimated Effort**: 35 minutes

---

### 9. src/config.py:187 - `_write_config_file` (EASY)

**Current Depth**: 4
**Location**: Config file writer
**Pattern**: if-elif-else format selection (mirrors _load_config_file)

**Refactoring Strategy**:
- Extract writers: `_write_json_config()`, `_write_yaml_config()`
- Use dispatch pattern
- Consistent with _load_config_file approach

**Estimated Effort**: 20 minutes

---

### 10. src/config.py:198 - `save_config` (EASY)

**Current Depth**: 4
**Location**: Config save helper
**Pattern**: Nested if checks with file operations

**Refactoring Strategy**:
- Use guard clauses for validation
- Extract file writing to helper
- Simplify error handling

**Estimated Effort**: 15 minutes

---

### 11. src/orchestrator/core.py:67 - `file_content` (EASY)

**Current Depth**: 4
**Location**: FileLintContext property
**Pattern**: if-and-and with nested try-except

**Refactoring Strategy**:
- Use early returns (if not condition: return)
- Simplify compound conditions
- Flatten try-except

**Estimated Effort**: 15 minutes

---

### 12. src/orchestrator/core.py:110 - `lint_file` (MODERATE)

**Current Depth**: 4
**Location**: Core orchestrator file linting
**Pattern**: Core logic with try-except in loop

**Refactoring Strategy**:
- Extract `_execute_rule()` helper
- Simplify error handling
- Early returns for ignored files

**Estimated Effort**: 40 minutes

---

### 13. src/orchestrator/language_detector.py:40 - `_detect_from_shebang` (EASY)

**Current Depth**: 4
**Location**: Language detection helper
**Pattern**: nested with + for + if

**Refactoring Strategy**:
- Extract shebang parsing to helper
- Use early returns
- Simplify file reading logic

**Estimated Effort**: 20 minutes

---

### 14. src/core/registry.py:84 - `discover_rules` (MODERATE)

**Current Depth**: 4
**Location**: Rule discovery orchestration
**Pattern**: try-except with for + nested try-except

**Refactoring Strategy**:
- Extract `_iter_package_modules()` helper
- Simplify nested error handling
- Use guard clauses

**Estimated Effort**: 35 minutes

---

### 15. src/core/registry.py:121 - `_discover_from_module` (MODERATE)

**Current Depth**: 4
**Location**: Module rule discovery
**Pattern**: try-except with for + if checks

**Refactoring Strategy**:
- Extract `_register_rule_if_valid()` helper
- Use guard clauses for validation
- Simplify error handling

**Estimated Effort**: 30 minutes

---

### 16. src/linters/nesting/linter.py:119 - `_check_functions` (EASY)

**Current Depth**: 4
**Location**: Nesting linter function checker
**Pattern**: for + if + for + if

**Refactoring Strategy**:
- Extract `_create_violation_if_needed()` helper
- Use guard clauses in loops
- Flatten nested loops

**Estimated Effort**: 20 minutes

---

### 17. src/linters/file_placement/linter.py:491 - `lint_directory` (MODERATE)

**Current Depth**: 4
**Location**: File placement directory linter
**Pattern**: for loop with nested if + try-except

**Refactoring Strategy**:
- Extract `_process_file()` helper
- Simplify error handling
- Use early continue in loop

**Estimated Effort**: 30 minutes

---

### 18. src/linters/file_placement/linter.py:558 - `_load_layout_config` (EASY)

**Current Depth**: 4
**Location**: Layout config loader
**Pattern**: Nested if with file checks

**Refactoring Strategy**:
- Use guard clauses for file validation
- Extract config parsing to helper
- Simplify error handling

**Estimated Effort**: 15 minutes

---

## Refactoring Patterns Summary

### Pattern 1: If-Elif-Else Chains (Format Selection)
**Occurrences**: 5 functions
**Examples**: config_show, _write_layout_config, _write_config_file, _load_config_file, _output_text

**Approach**:
```python
# Before (depth 4)
if format == "json":
    for item in data:
        print(json.dumps(item))

# After (depth 2)
def _format_json(data):
    for item in data:
        print(json.dumps(item))

# Dispatch
formatters = {"json": _format_json, "yaml": _format_yaml}
formatters[format](data)
```

### Pattern 2: Nested Error Handling
**Occurrences**: 6 functions
**Examples**: lint_file, discover_rules, lint_directory, _load_config_file

**Approach**:
```python
# Before (depth 4)
for item in items:
    if condition:
        try:
            result = process(item)
        except Error:
            continue

# After (depth 2)
def _safe_process(item):
    try:
        return process(item)
    except Error:
        return None

for item in items:
    if not condition:
        continue
    _safe_process(item)
```

### Pattern 3: Guard Clauses
**Occurrences**: 7 functions
**Examples**: file_content, save_config, _load_layout_config

**Approach**:
```python
# Before (depth 4)
if self._content is None:
    if self._path:
        if self._path.exists():
            try:
                self._content = self._path.read_text()

# After (depth 2)
if self._content is not None:
    return self._content
if not self._path or not self._path.exists():
    return None
try:
    self._content = self._path.read_text()
```

---

## PR5/PR6 Split Strategy

### PR5: Easy Refactors (9 functions, ~2.5 hours)
**Focus**: Quick wins with simple pattern refactoring
**Functions**:
1. src/cli.py:162 - config_show
2. src/cli.py:432 - _write_layout_config
3. src/cli.py:525 - _output_text
4. src/config.py:187 - _write_config_file
5. src/config.py:198 - save_config
6. src/orchestrator/core.py:67 - file_content
7. src/orchestrator/language_detector.py:40 - _detect_from_shebang
8. src/linters/nesting/linter.py:119 - _check_functions
9. src/linters/file_placement/linter.py:558 - _load_layout_config

**Expected Outcome**: ~50% reduction in violations (18 → 9)

### PR6: Moderate Refactors + Documentation (9 functions, ~3.5 hours)
**Focus**: Complex business logic refactoring + comprehensive docs
**Functions**:
1. src/cli.py:345 - file_placement
2. src/cli.py:458 - _load_config_file
3. src/cli.py:585 - nesting
4. src/config.py:98 - _load_from_default_locations
5. src/config.py:153 - _load_config_file
6. src/orchestrator/core.py:110 - lint_file
7. src/core/registry.py:84 - discover_rules
8. src/core/registry.py:121 - _discover_from_module
9. src/linters/file_placement/linter.py:491 - lint_directory

**Expected Outcome**: Zero violations, complete documentation

---

## Success Metrics

### PR5 Completion Criteria
- ✅ 9 functions refactored from depth 4 → depth 3
- ✅ All tests pass (make test exits with code 0)
- ✅ make lint-full exits with code 0
- ✅ make lint-nesting shows 9 violations (down from 18)
- ✅ No functionality broken (integration tests pass)

### PR6 Completion Criteria
- ✅ All 18 functions at depth ≤ 3
- ✅ make lint-nesting exits with code 0 (zero violations)
- ✅ All tests pass
- ✅ Documentation complete (README.md, docs/nesting-linter.md)
- ✅ Refactoring patterns documented
- ✅ CHANGELOG.md updated

---

## Risk Assessment

**Overall Risk**: LOW

**Risks Identified**:
1. **Breaking tests during refactoring**: MEDIUM
   - Mitigation: Run tests after each function refactoring

2. **Introducing bugs in core logic**: MEDIUM
   - Mitigation: Focus on extracting logic, not changing it

3. **Scope creep (over-refactoring)**: LOW
   - Mitigation: Only refactor to depth 3, don't optimize further

4. **Time estimation**: LOW
   - Mitigation: Split into two PRs with buffer time

**Dependencies**:
- No blocking dependencies
- Can start immediately after PR4 completion

---

## Appendix: Raw Violation Output

```
=== Running nesting depth linter (dogfooding) ===
Found 18 violation(s):

  src/cli.py:162
    [ERROR] nesting.excessive-depth: Function 'config_show' has excessive nesting depth (4)

  src/cli.py:345
    [ERROR] nesting.excessive-depth: Function 'file_placement' has excessive nesting depth (4)

  src/cli.py:432
    [ERROR] nesting.excessive-depth: Function '_write_layout_config' has excessive nesting depth (4)

  src/cli.py:458
    [ERROR] nesting.excessive-depth: Function '_load_config_file' has excessive nesting depth (4)

  src/cli.py:525
    [ERROR] nesting.excessive-depth: Function '_output_text' has excessive nesting depth (4)

  src/cli.py:585
    [ERROR] nesting.excessive-depth: Function 'nesting' has excessive nesting depth (4)

  src/config.py:98
    [ERROR] nesting.excessive-depth: Function '_load_from_default_locations' has excessive nesting depth (4)

  src/config.py:153
    [ERROR] nesting.excessive-depth: Function '_load_config_file' has excessive nesting depth (4)

  src/config.py:187
    [ERROR] nesting.excessive-depth: Function '_write_config_file' has excessive nesting depth (4)

  src/config.py:198
    [ERROR] nesting.excessive-depth: Function 'save_config' has excessive nesting depth (4)

  src/orchestrator/core.py:67:4
    [ERROR] nesting.excessive-depth: Function 'file_content' has excessive nesting depth (4)

  src/orchestrator/core.py:110:4
    [ERROR] nesting.excessive-depth: Function 'lint_file' has excessive nesting depth (4)

  src/orchestrator/language_detector.py:40
    [ERROR] nesting.excessive-depth: Function '_detect_from_shebang' has excessive nesting depth (4)

  src/core/registry.py:84:4
    [ERROR] nesting.excessive-depth: Function 'discover_rules' has excessive nesting depth (4)

  src/core/registry.py:121:4
    [ERROR] nesting.excessive-depth: Function '_discover_from_module' has excessive nesting depth (4)

  src/linters/nesting/linter.py:119:4
    [ERROR] nesting.excessive-depth: Function '_check_functions' has excessive nesting depth (4)

  src/linters/file_placement/linter.py:491:4
    [ERROR] nesting.excessive-depth: Function 'lint_directory' has excessive nesting depth (4)

  src/linters/file_placement/linter.py:558:4
    [ERROR] nesting.excessive-depth: Function '_load_layout_config' has excessive nesting depth (4)
```

---

**Document Status**: ✅ Complete - Ready for PR5 implementation
**Last Updated**: 2025-10-07
**Next Action**: Begin PR5 refactoring with easy wins (9 functions)
