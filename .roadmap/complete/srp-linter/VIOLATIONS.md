# SRP Linter Violations Catalog

**Purpose**: Catalog of all SRP violations found in thai-lint codebase during dogfooding

**Scope**: Documents violations discovered in PR4 to be systematically fixed in PR5

**Overview**: Comprehensive catalog of Single Responsibility Principle violations found by running
    the SRP linter on the thai-lint codebase. Each violation includes file location, class name,
    specific metrics that failed, and analysis of refactoring difficulty. Violations are categorized
    by severity and complexity to guide systematic refactoring in PR5.

---

## Summary

**Total Violations**: 6
**Date Discovered**: 2025-10-08
**Command Used**: `make lint-srp`

### Violation Distribution by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical (LOC + Methods) | 1 | 17% |
| High (Methods 10+) | 4 | 67% |
| Medium (Methods 8-9) | 1 | 17% |

### Violation Distribution by File Type

| Category | Count |
|----------|-------|
| Core Infrastructure | 1 |
| Linter Implementations | 5 |

---

## Violation Details

### 1. FilePlacementLinter (CRITICAL)

**File**: `src/linters/file_placement/linter.py:57`
**Class**: `FilePlacementLinter`
**Metrics**:
- Methods: 33 (max: 7) - **470% over limit**
- Lines of Code: 382 (max: 200) - **91% over limit**

**Analysis**:
This is the most severe violation. The FilePlacementLinter class has accumulated too many responsibilities:
1. Configuration loading and validation
2. Pattern matching logic
3. Directory-specific rule checking
4. Global pattern checking
5. Violation message generation
6. Path resolution and normalization

**Refactoring Complexity**: HIGH
**Estimated Effort**: 4-6 hours
**Priority**: P0 - Must fix

**Suggested Refactoring**:
1. Extract `ConfigLoader` class (config file loading, validation)
2. Extract `PatternValidator` class (regex pattern validation)
3. Extract `RuleChecker` class (directory/global rule checking)
4. Extract `PathResolver` class (path normalization, resolution)
5. Keep `FilePlacementLinter` as orchestrator (composition)

**Impact**: Medium - requires updating all tests and usage points

---

### 2. NestingDepthRule (HIGH)

**File**: `src/linters/nesting/linter.py:35`
**Class**: `NestingDepthRule`
**Metrics**:
- Methods: 12 (max: 7) - **71% over limit**

**Analysis**:
The NestingDepthRule class handles multiple concerns:
1. AST parsing for Python/TypeScript
2. Depth calculation logic
3. Violation detection
4. Configuration management
5. Ignore directive parsing
6. Multiple helper methods for different node types

**Refactoring Complexity**: MEDIUM
**Estimated Effort**: 2-3 hours
**Priority**: P1

**Suggested Refactoring**:
1. Extract `NestingCalculator` class (depth calculation logic)
2. Extract `NodeAnalyzer` class (AST node type handling)
3. Keep `NestingDepthRule` focused on orchestration and configuration

**Impact**: Low - tests are well-isolated

---

### 3. SRPRule (HIGH)

**File**: `src/linters/srp/linter.py:36`
**Class**: `SRPRule`
**Metrics**:
- Methods: 16 (max: 7) - **129% over limit**

**Analysis**:
Ironic that the SRP linter violates SRP! The SRPRule class handles:
1. Configuration loading
2. Python AST parsing and analysis
3. TypeScript parsing and analysis
4. Class metric extraction
5. Violation creation and message generation
6. Ignore directive handling
7. Multiple suggestion generation methods

**Refactoring Complexity**: MEDIUM-HIGH
**Estimated Effort**: 3-4 hours
**Priority**: P0 - High visibility (dogfooding failure)

**Suggested Refactoring**:
1. Extract `ClassAnalyzer` class (handles both Python and TypeScript)
2. Extract `ViolationBuilder` class (creates violations, generates messages/suggestions)
3. Extract `MetricsEvaluator` class (evaluates metrics against thresholds)
4. Keep `SRPRule` as orchestrator

**Impact**: Medium - needs careful testing

---

### 4. RuleRegistry (HIGH)

**File**: `src/core/registry.py:38`
**Class**: `RuleRegistry`
**Metrics**:
- Methods: 11 (max: 7) - **57% over limit**

**Analysis**:
The RuleRegistry combines:
1. Basic registry operations (register, get, list)
2. Auto-discovery logic (package scanning, module iteration)
3. Class introspection (finding BaseLintRule subclasses)
4. Module loading and import handling

**Refactoring Complexity**: MEDIUM
**Estimated Effort**: 2-3 hours
**Priority**: P1

**Suggested Refactoring**:
1. Extract `RuleDiscovery` class (auto-discovery, module scanning, introspection)
2. Keep `RuleRegistry` focused on registry operations (register, get, list)

**Impact**: Low - interface remains the same

---

### 5. TypeScriptNestingAnalyzer (HIGH)

**File**: `src/linters/nesting/typescript_analyzer.py:36`
**Class**: `TypeScriptNestingAnalyzer`
**Metrics**:
- Methods: 12 (max: 7) - **71% over limit**

**Analysis**:
Handles TypeScript-specific nesting analysis with multiple node type handlers:
1. Tree-sitter parsing
2. Node traversal
3. Depth tracking
4. Multiple `_is_*_statement` helper methods (if, for, while, switch, etc.)

**Refactoring Complexity**: MEDIUM
**Estimated Effort**: 2-3 hours
**Priority**: P2

**Suggested Refactoring**:
1. Extract `NodeTypeDetector` class (all `_is_*_statement` methods)
2. Extract `DepthTracker` class (depth calculation logic)
3. Keep analyzer focused on tree traversal

**Impact**: Low - implementation detail

---

### 6. TypeScriptSRPAnalyzer (MEDIUM)

**File**: `src/linters/srp/typescript_analyzer.py:39`
**Class**: `TypeScriptSRPAnalyzer`
**Metrics**:
- Methods: 8 (max: 7) - **14% over limit**

**Analysis**:
Just slightly over the threshold. Handles:
1. Tree-sitter parsing
2. Class finding
3. Method counting
4. LOC counting
5. Property detection

**Refactoring Complexity**: LOW
**Estimated Effort**: 1 hour
**Priority**: P2

**Suggested Refactoring**:
1. Extract `MetricsCalculator` class (count_methods, count_loc, has_property_decorator)
2. Keep analyzer focused on tree traversal and class finding

**Impact**: Very Low - minor change

---

## Refactoring Strategy

### Phase 1: Critical Violations (P0)
1. **FilePlacementLinter** (33 methods, 382 LOC)
   - Highest priority due to severity
   - Extract 4-5 focused classes
   - Estimated: 4-6 hours

2. **SRPRule** (16 methods)
   - High visibility (dogfooding)
   - Extract 3 focused classes
   - Estimated: 3-4 hours

### Phase 2: High Priority (P1)
3. **NestingDepthRule** (12 methods)
   - Extract 2 focused classes
   - Estimated: 2-3 hours

4. **RuleRegistry** (11 methods)
   - Extract 1 focused class
   - Estimated: 2-3 hours

### Phase 3: Medium Priority (P2)
5. **TypeScriptNestingAnalyzer** (12 methods)
   - Extract 2 focused classes
   - Estimated: 2-3 hours

6. **TypeScriptSRPAnalyzer** (8 methods)
   - Extract 1 focused class
   - Estimated: 1 hour

**Total Estimated Effort**: 14-22 hours

---

## Common Refactoring Patterns

### Pattern 1: Extract Helper Methods into Utility Classes
**Problem**: Many `_helper_method` functions cluttering the main class
**Solution**: Group related helpers into focused utility classes

### Pattern 2: Extract Configuration Management
**Problem**: Classes handling both business logic and config loading
**Solution**: Create dedicated `*Config` or `*Loader` classes

### Pattern 3: Extract Language-Specific Logic
**Problem**: Single class handling Python and TypeScript differently
**Solution**: Create separate analyzer classes or use strategy pattern

### Pattern 4: Extract Violation Building
**Problem**: Classes mixing detection logic with message generation
**Solution**: Create dedicated `ViolationBuilder` or `MessageFormatter` classes

---

## Success Criteria for PR5

- [ ] All 6 violations resolved
- [ ] `make lint-srp` exits with code 0 (zero violations)
- [ ] `make test` exits with code 0 (no broken functionality)
- [ ] `make lint-full` exits with code 0 (all quality gates pass)
- [ ] Test coverage maintained or improved (>85%)
- [ ] No new complexity violations introduced

---

## Notes

**Key Insight**: The violations cluster around linter implementations and core infrastructure,
suggesting that these areas accumulated responsibilities during rapid development. The refactoring
will improve maintainability and make it easier to add future linters.

**Risk**: FilePlacementLinter refactoring is complex and touches many parts of the codebase.
Recommend tackling this first with comprehensive testing.

**Opportunity**: This refactoring will establish patterns for future linters to follow,
preventing similar violations in new code.
