# DRY Linter Violations - Dogfooding Discovery (PR4)

**Date**: 2025-10-09
**Total Violations**: 212
**Linter**: DRY (duplicate code detection)
**Configuration**: min_duplicate_lines: 3, cache enabled

---

## Executive Summary

The DRY linter found **212 violations** across **35 source files** in the `src/` directory. This represents significant code duplication that should be refactored in PR5.

### Performance Metrics

**Benchmark Results** (src/ directory only):
- **First run** (cache creation): 0.751s - 0.961s
- **Second run** (cache hit): 0.764s
- **make lint-dry**: 0.961s (includes Makefile overhead)

**Decision**: ✅ **ADD TO `lint-full`** - Performance is excellent (<1s), well under the 1-second threshold.

### Top Offenders (Files with Most Violations)

1. **src/cli.py** - 23 violations (CLI command duplication)
2. **src/linters/file_placement/violation_factory.py** - 21 violations (violation builders)
3. **src/linters/srp/linter.py** - 18 violations (linter pattern duplication)
4. **src/linters/nesting/linter.py** - 16 violations (linter pattern duplication)
5. **src/linters/file_placement/rule_checker.py** - 14 violations (rule checking logic)
6. **src/linters/nesting/violation_builder.py** - 13 violations (violation message builders)
7. **src/linters/srp/typescript_analyzer.py** - 9 violations (TypeScript analysis)
8. **src/linters/dry/** - 29 violations total (ironic - DRY linter has DRY violations!)

---

## Violation Categories

### Category 1: CLI Command Patterns (23 violations)

**Pattern**: Repeated Click command boilerplate across `dry`, `srp`, `nesting`, `file-placement` commands

**Examples**:
- `src/cli.py:232` - Duplicate across 4 CLI commands (dry, srp, nesting, file-placement)
- `src/cli.py:244` - Click option parsing repeated 4 times
- `src/cli.py:254` - Output formatting repeated 4 times

**Refactoring Strategy**:
- Extract common CLI helper functions
- Create reusable Click option decorators
- Template method pattern for command structure

**Impact**: HIGH - CLI is user-facing, duplication makes maintenance harder

---

### Category 2: Violation Builder Patterns (40 violations)

**Pattern**: Violation object creation code repeated across multiple linters

**Files Affected**:
- `src/linters/file_placement/violation_factory.py` (21 violations)
- `src/linters/nesting/violation_builder.py` (13 violations)
- `src/linters/srp/violation_builder.py` (6 violations)

**Examples**:
- Violation message formatting (appears 5+ times)
- Severity mapping logic (repeated)
- File path handling (duplicated)

**Refactoring Strategy**:
- Extract base `ViolationBuilder` class in `src/core/`
- Common methods: `build_violation()`, `format_message()`, `add_location()`
- Linter-specific builders extend base class

**Impact**: MEDIUM - Not user-facing, but affects maintainability

---

### Category 3: Linter Framework Patterns (34 violations)

**Pattern**: BaseLintRule implementation patterns repeated across linters

**Files Affected**:
- `src/linters/srp/linter.py` (18 violations)
- `src/linters/nesting/linter.py` (16 violations)

**Examples**:
- Config loading logic (same across 3 linters)
- Context metadata extraction (duplicated)
- Project root handling (repeated)

**Refactoring Strategy**:
- Extract common linter utilities to `src/core/linter_utils.py`
- Base class helper methods for config loading
- Standardize context access patterns

**Impact**: MEDIUM - Internal framework, improves consistency

---

### Category 4: TypeScript Analysis Patterns (23 violations)

**Pattern**: Tree-sitter parsing boilerplate repeated across linters

**Files Affected**:
- `src/linters/srp/typescript_analyzer.py` (9 violations)
- `src/linters/nesting/typescript_analyzer.py` (7 violations)
- `src/linters/nesting/typescript_function_extractor.py` (7 violations)

**Examples**:
- Tree-sitter initialization (repeated)
- Node traversal patterns (duplicated)
- Language parsing logic (same across files)

**Refactoring Strategy**:
- Extract `src/analyzers/typescript_base.py` with common tree-sitter logic
- Shared node traversal utilities
- Reusable parsing patterns

**Impact**: MEDIUM - TypeScript support is important for multi-language linting

---

### Category 5: DRY Linter Self-Violations (29 violations!)

**Pattern**: The DRY linter itself has duplicate code! (Ironic)

**Files Affected**:
- `src/linters/dry/typescript_analyzer.py` (7 violations)
- `src/linters/dry/python_analyzer.py` (7 violations)
- `src/linters/dry/violation_generator.py` (6 violations)
- `src/linters/dry/cache.py` (5 violations)
- `src/linters/dry/linter.py` (4 violations)

**Examples**:
- Python/TypeScript analyzer duplication
- Violation generation logic repeated
- Cache query patterns

**Refactoring Strategy**:
- Extract common analyzer base class
- Shared violation generation utilities
- Consolidate cache query methods

**Impact**: HIGH - Eating our own dog food! This is embarrassing but validates the linter works.

---

### Category 6: File Placement Rule Checker (14 violations)

**Pattern**: Pattern matching and rule checking logic duplicated

**File**: `src/linters/file_placement/rule_checker.py`

**Examples**:
- Pattern validation logic (6 occurrences of same code)
- Rule checking workflow (repeated)
- Metadata access patterns

**Refactoring Strategy**:
- Extract pattern validation to separate utility
- Template method for rule checking flow
- Shared metadata access helpers

**Impact**: LOW - Internal implementation, limited user impact

---

### Category 7: Cross-File Base Class Patterns (miscellaneous)

**Pattern**: Small duplications across unrelated files

**Examples**:
- Config loading: `src/config.py` ↔ `src/linter_config/loader.py`
- Ignore patterns: `src/linter_config/ignore.py` (internal duplication)
- Base class methods: `src/core/base.py`, `src/core/rule_discovery.py`

**Refactoring Strategy**:
- Extract common config utilities
- Consolidate ignore pattern logic
- Review base class design for shared patterns

**Impact**: LOW - Small improvements, good for consistency

---

## Detailed Violation List

### src/cli.py (23 violations)

| Line | Occurrences | Pattern |
|------|-------------|---------|
| 232  | 4 | Click command setup (dry, srp, nesting, file-placement) |
| 244  | 4 | Click option parsing |
| 254  | 4 | Output formatting |
| 289  | 2 | Error handling |
| 339  | 2 | Config validation |
| 365  | 3 | Cross-linter helper (also in srp/__init__.py, nesting/__init__.py) |
| 407  | 2 | Result aggregation |
| 423  | 2 | Path resolution |
| 429  | 3 | File filtering |
| ... | ... | (14 more duplicates) |

**Priority**: HIGH - Refactor CLI command patterns

---

### src/linters/file_placement/violation_factory.py (21 violations)

| Line | Occurrences | Pattern |
|------|-------------|---------|
| 27   | 5 | Violation builder setup (also in srp/violation_builder.py) |
| 37   | 5 | Severity mapping |
| 34   | 4 | Message formatting |
| 99   | 3 | Location handling |
| ... | ... | (12 more duplicates) |

**Priority**: MEDIUM - Extract base violation builder

---

### src/linters/srp/linter.py (18 violations)

| Line | Occurrences | Pattern |
|------|-------------|---------|
| 21   | 3 | Config loading (also in nesting/linter.py, dry/linter.py) |
| 25   | 3 | Metadata access |
| 29   | 3 | Project root handling |
| 35   | 4 | Context validation (also in srp/class_analyzer.py) |
| 85   | 6 | File path normalization (across 3 linters) |
| ... | ... | (13 more duplicates) |

**Priority**: MEDIUM - Extract linter framework utilities

---

### src/linters/nesting/linter.py (16 violations)

Similar to srp/linter.py - shared linter framework patterns.

**Priority**: MEDIUM - Refactor with srp/linter.py

---

### src/linters/dry/ (29 violations across 7 files)

**Self-violations in the DRY linter itself!**

| File | Violations | Pattern |
|------|------------|---------|
| typescript_analyzer.py | 7 | Tree-sitter patterns, shared with srp/nesting |
| python_analyzer.py | 7 | AST patterns, shared with srp |
| violation_generator.py | 6 | Violation building, internal duplication |
| cache.py | 5 | Cache query methods, internal duplication |
| linter.py | 4 | Config loading (shared with srp/nesting) |
| file_analyzer.py | 4 | File analysis logic |

**Priority**: HIGH - Fix DRY linter's own violations (ironic!)

---

## Refactoring Plan for PR5

### Phase 1: Extract Common Utilities (High Impact)

1. **CLI Utilities** (`src/core/cli_utils.py`)
   - Extract common Click decorators
   - Shared option parsing
   - Output formatting helpers
   - **Estimated reduction**: 15-20 violations

2. **Base Violation Builder** (`src/core/violation_builder.py`)
   - Base class for all violation builders
   - Common message formatting
   - Severity mapping
   - **Estimated reduction**: 30-35 violations

3. **Linter Framework Utilities** (`src/core/linter_utils.py`)
   - Config loading helpers
   - Metadata access patterns
   - Project root resolution
   - **Estimated reduction**: 25-30 violations

### Phase 2: Language Analyzer Refactoring (Medium Impact)

4. **TypeScript Base Analyzer** (`src/analyzers/typescript_base.py`)
   - Shared tree-sitter setup
   - Node traversal utilities
   - Common parsing patterns
   - **Estimated reduction**: 20-25 violations

5. **Python Base Analyzer** (`src/analyzers/python_base.py`)
   - Shared AST utilities
   - Common parsing patterns
   - **Estimated reduction**: 10-15 violations

### Phase 3: DRY Linter Self-Fixes (High Priority)

6. **DRY Linter Internal Refactoring**
   - Consolidate python/typescript analyzers
   - Extract violation generation utilities
   - Refactor cache query methods
   - **Estimated reduction**: 25-30 violations

### Phase 4: Remaining Smaller Patterns (Low Impact)

7. **Config/Ignore Utilities**
   - Consolidate config loading
   - Shared ignore pattern logic
   - **Estimated reduction**: 5-10 violations

8. **File Placement Rule Checker**
   - Extract pattern validation
   - Template method for checks
   - **Estimated reduction**: 10-15 violations

---

## Success Metrics

### Goals for PR5

- [ ] Zero violations: `thailint dry src/` exits with code 0
- [ ] All 533 tests still passing
- [ ] Pylint 10.00/10 maintained
- [ ] Xenon A-grade maintained
- [ ] Code quality improved (not just duplicates removed)
- [ ] New base classes documented
- [ ] Refactoring patterns documented

### Estimated Violation Reduction

- **Total violations**: 212
- **Estimated after PR5**: 0 (all refactored)
- **New code created**: ~500-800 lines (base classes, utilities)
- **Net lines removed**: ~200-400 lines (duplicate code eliminated)

---

## Configuration Notes

### Current Settings

```yaml
dry:
  enabled: true  # Enabled for dogfooding (PR4)
  min_duplicate_lines: 3  # Minimum lines for duplicate detection
  min_duplicate_tokens: 30  # Minimum tokens for duplicate detection
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
  cache_max_age_days: 30
  ignore:
    - "tests/"  # Test code often has acceptable duplication
    - "__init__.py"  # Import-only files are exempt
```

### Cache Performance

- **Cache file size**: ~180KB (after first run on src/)
- **Cache hit rate**: 100% on second run (no file changes)
- **Performance**: Sub-second on both cached and uncached runs
- **SQLite queries**: Efficient with indexed hash lookups

---

## Lessons Learned

### What Went Well

1. **DRY linter works!** - Found real, meaningful duplications
2. **Performance is excellent** - Sub-second even on first run
3. **Cache works as designed** - Fast incremental scans
4. **Eating our own dog food** - DRY linter has DRY violations (ironic but validates linter)

### Patterns Discovered

1. **CLI commands need abstraction** - Too much boilerplate
2. **Violation builders are similar** - Should share base class
3. **Linter framework has patterns** - Reusable across all linters
4. **TypeScript analyzers duplicate logic** - Need common base
5. **DRY linter itself needs DRY** - Meta but important

### Next Steps for PR5

1. Start with CLI utilities (high impact, user-facing)
2. Create base violation builder (affects all linters)
3. Extract linter framework utilities (benefits future linters)
4. Refactor DRY linter itself (eating our own dog food!)
5. Clean up remaining patterns

---

## Appendix: Full JSON Output

See `/tmp/dry-violations.json` for complete machine-readable violation list.

**Total violations by category**:
- CLI patterns: 23
- Violation builders: 40
- Linter framework: 34
- TypeScript analysis: 23
- DRY linter self-violations: 29
- File placement checker: 14
- Miscellaneous: 49

**Total**: 212 violations across 35 files
