# Method Should Be Property Linter - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for Method Should Be Property Linter with current progress tracking and implementation guidance

**Scope**: Development of a linter to detect Python methods that should be converted to @property decorators, following Pythonic conventions

**Overview**: Primary handoff document for AI agents working on the Method Should Be Property Linter feature.
    Tracks current implementation progress, provides next action guidance, and coordinates AI agent work across
    multiple pull requests. Contains current status, prerequisite validation, PR dashboard, detailed checklists,
    implementation strategy, success metrics, and AI agent instructions. Essential for maintaining development
    continuity and ensuring systematic feature implementation with proper validation and testing.

**Dependencies**: BaseLintRule interface, Python AST, pytest testing framework

**Exports**: Progress tracking, implementation guidance, AI agent coordination, and feature development roadmap

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: Progress-driven coordination with systematic validation, checklist management, and AI agent handoff procedures

---

## Document Purpose
This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the Method Should Be Property Linter feature. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and feature requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## Current Status
**Current PR**: PR4 Complete - Ready for PR5
**Infrastructure State**: Linter complete and validated on own codebase, 681 tests passing
**Feature Target**: Production-ready method-should-be-property linter for Python

## Required Documents Location
```
.roadmap/in-progress/method-should-be-property/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## Next PR to Implement

### START HERE: PR5 - Documentation & Publishing

**Quick Summary**:
Create comprehensive user documentation for the method-property linter.

**Pre-flight Checklist**:
- [ ] Create `docs/method-property-linter.md`
- [ ] Update `mkdocs.yml` with nav entry
- [ ] Update `README.md` with linter in feature list
- [ ] Update `docs/cli-reference.md` with command
- [ ] Update `docs/configuration.md` with config options
- [ ] Update `docs/index.md` with linter count

**Prerequisites Complete**:
- [x] Research on best practices complete (PEP 8, Pylint discussions)
- [x] Confirmed no existing major linter implements this rule
- [x] Roadmap documents created
- [x] PR1 test suite created (111 tests)
- [x] PR2 Python implementation complete (all 111 tests pass, lint-full passes)
- [x] PR3 CLI integration complete (text/json/sarif formats work, commit db268dc)
- [x] PR4 self-dogfooding complete (5 get_* methods fixed, commit b837f3b)

---

## Overall Progress
**Total Completion**: 80% (4/5 PRs completed)

```
[################################        ] 80% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Test Suite for Python Method Detection | Complete | 100% | Medium | P0 | 111 tests created, TDD red phase verified |
| PR2 | Python Implementation | Complete | 100% | Medium | P0 | All 111 tests pass, lint-full passes |
| PR3 | CLI Integration | Complete | 100% | Low | P0 | Command works (commit db268dc) |
| PR4 | Self-Dogfooding: Lint Own Codebase | Complete | 100% | Medium | P1 | 5 violations fixed, action verbs excluded (commit b837f3b) |
| PR5 | Documentation & Publishing | Not Started | 0% | Low | P1 | Docs for ReadTheDocs and PyPI users |

### Status Legend
- Not Started
- In Progress
- Complete
- Blocked
- Cancelled

---

## PR1: Test Suite for Python Method Detection

### Scope
Write comprehensive test suite for Python method-should-be-property detection using TDD approach.

### Success Criteria
- [x] Tests organized in `tests/unit/linters/method_property/`
- [x] Tests follow pytest and project conventions
- [x] All tests fail initially (TDD red phase) - ModuleNotFoundError as expected
- [x] Coverage includes all detection patterns from AI_CONTEXT.md
- [x] Coverage includes all exclusion rules from AI_CONTEXT.md
- [x] Tests pass linting (Pylint 10.00/10 excluding import errors, Xenon A-grade)

### Key Test Categories
1. **Basic Detection** - Simple attribute returns, get_* prefix, computed values
2. **Exclusion Rules** - Parameters, side effects, decorators, test files
3. **Configuration** - Custom thresholds, ignore patterns
4. **Ignore Directives** - Line-level, method-level ignores
5. **Edge Cases** - Empty files, Unicode, syntax errors

### Files Created
```
tests/unit/linters/method_property/
├── __init__.py                    # Package marker
├── conftest.py                    # 14 shared fixtures
├── test_basic_detection.py        # 16 tests - core detection
├── test_exclusion_rules.py        # 31 tests - exclusion scenarios
├── test_configuration.py          # 14 tests - config handling
├── test_ignore_directives.py      # 11 tests - ignore directives
├── test_edge_cases.py             # 22 tests - edge cases
└── test_violation_details.py      # 17 tests - violation messages
```
**Total: 111 tests** (exceeds 40 minimum requirement)

---

## PR2: Python Implementation

### Scope
Implement Python method-should-be-property detection to pass PR1 tests.

### Success Criteria
- [x] `src/linters/method_property/` module created
- [x] `MethodPropertyRule` class implements `MultiLanguageLintRule`
- [x] Python AST analysis detects all patterns from AI_CONTEXT.md
- [x] All exclusion rules properly implemented
- [x] Configuration support for thresholds and ignore patterns
- [x] All PR1 tests pass (111/111)
- [x] Linting passes (`just lint-full` exits with code 0)

### Files Created
```
src/linters/method_property/
├── __init__.py           # Package exports (lint convenience function)
├── config.py             # MethodPropertyConfig dataclass
├── linter.py             # MethodPropertyRule class
├── python_analyzer.py    # PythonMethodAnalyzer for AST analysis
└── violation_builder.py  # ViolationBuilder for message creation
```

### Implementation Notes
- Uses composition pattern with helper classes (analyzer, violation builder)
- AST-based analysis with comprehensive exclusion checks
- Supports ignore directives (thailint: ignore, noqa)
- Test file detection (test_*.py, *_test.py patterns)
- Configurable max_body_statements threshold (default: 3)
- Added DRY ignore patterns for expected linter framework duplication

---

## PR3: CLI Integration

### Scope
Add CLI command for method-property linter.

### Success Criteria
- [x] `thailint method-property` command registered in `src/cli.py`
- [x] Supports `--config`, `--format`, `--recursive` options
- [x] All three output formats work (text, json, sarif)
- [x] Help text with examples
- [x] Exit codes: 0 (clean), 1 (violations), 2 (error)

### Implementation Notes
- Command added at `src/cli.py` lines 1781-1895
- Helper functions: `_setup_method_property_orchestrator`, `_run_method_property_lint`
- Uses existing orchestrator and format_violations infrastructure
- Commit: db268dc

---

## PR4: Self-Dogfooding: Lint Own Codebase

### Scope
Run method-property linter on thai-lint codebase and address violations.

### Success Criteria
- [x] Linter runs on entire codebase
- [x] All violations either fixed or documented with ignore directives
- [x] Linting passes (`just lint-full` exits with code 0)
- [x] Tests still pass (681 tests)

### Implementation Notes
- Found 7 violations initially, 2 were false positives
- Fixed 5 get_* methods by converting to @property:
  - `LinterConfigLoader.get_defaults()` → `defaults`
  - `BaseBlockFilter.get_name()` → `name` (abstract property)
  - `KeywordArgumentFilter.get_name()` → `name`
  - `ImportGroupFilter.get_name()` → `name`
  - `DRYCache.get_duplicate_hashes()` → `duplicate_hashes`
  - `DuplicateStorage.get_duplicate_hashes()` → `duplicate_hashes`
- Added exclusion for action verb methods (`to_*`, `finalize`, `serialize`, `validate`)
- Commit: b837f3b

---

## PR5: Documentation & Publishing

### Scope
Complete documentation for ReadTheDocs and PyPI users.

### Success Criteria
- [ ] `docs/method-property-linter.md` created (comprehensive user guide)
- [ ] `mkdocs.yml` updated with nav entry under Linters section
- [ ] `README.md` updated with linter in feature list
- [ ] `docs/cli-reference.md` updated with command documentation
- [ ] `docs/configuration.md` updated with configuration section
- [ ] `docs/index.md` updated with linter count/list
- [ ] All tests pass
- [ ] Full linting passes

---

## Implementation Strategy

**TDD Approach**:
1. Write failing tests first (red phase)
2. Implement minimal code to pass tests (green phase)
3. Refactor for quality (refactor phase)
4. Run full linting to ensure A-grade complexity
5. Dogfood the linter on own codebase

**Quality Focus**:
- All code must pass `just lint-full` (Pylint 10.00/10, Xenon A-grade)
- Tests must be comprehensive and maintainable
- Follow existing linter patterns for consistency

## Success Metrics

### Technical Metrics
- [ ] Test coverage >= 80%
- [ ] All linting passes (Pylint 10.00/10)
- [ ] All complexity A-grade (Xenon)
- [ ] No failing tests
- [ ] CI/CD pipeline green

### Feature Metrics
- [ ] Detects all patterns defined in AI_CONTEXT.md
- [ ] Respects all exclusion rules
- [ ] Supports ignore directives (line, method, file-level)
- [ ] Configurable thresholds
- [ ] False positive rate < 5%

## Update Protocol

After completing each PR:
1. Update the PR status to Complete
2. Fill in completion percentage (100%)
3. Add commit hash to notes: `(commit abc1234)`
4. Update the "Next PR to Implement" section
5. Update overall progress percentage
6. Commit changes to the progress document

## Notes for AI Agents

### Critical Context
- **Pythonic Philosophy**: Properties are preferred over getter/setter methods in Python (PEP 8)
- **No Existing Linter**: Pylint issue #7172 requests this feature but is not implemented
- **TDD Mandatory**: Tests must be written and failing before implementation
- **Follow Patterns**: Study `src/linters/print_statements/` for structure

### Common Pitfalls to Avoid
- Do not flag methods with parameters beyond `self`
- Do not flag methods with side effects (assignments, loops, try/except)
- Do not flag staticmethod/classmethod/abstractmethod
- Do not skip TDD - tests must come first
- Do not add suppression comments without user permission
- Do not commit code that doesn't pass `just lint-full`

### Resources
- **Detection Patterns**: AI_CONTEXT.md - comprehensive detection and exclusion rules
- **PR Details**: PR_BREAKDOWN.md - step-by-step implementation instructions
- **Test Guide**: `.ai/howtos/how-to-write-tests.md`
- **Linting Guide**: `.ai/howtos/how-to-fix-linting-errors.md`
- **Linter Guide**: `.ai/howtos/how-to-add-linter.md`
- **Pattern Reference**: `src/linters/print_statements/` (similar structure)

### Research Summary

**Best Practices from Web Research:**

| Source | Key Guidance |
|--------|-------------|
| PEP 8 | Expose simple attributes directly; use properties when functional behavior needed; avoid expensive operations in properties |
| Pylint #7172 | Feature request for this rule exists but is NOT implemented - needs PR |
| python-course.eu | Properties preferred; use methods only for complex validation, external API compatibility, or when extra parameters needed |

## Definition of Done

The feature is considered complete when:
- [ ] All 5 PRs merged to main
- [ ] Python method-should-be-property detection working
- [ ] thai-lint codebase passes its own method-property linter
- [ ] Documentation complete (docs/method-property-linter.md)
- [ ] All tests passing
- [ ] All linting passing (Pylint 10.00/10, Xenon A-grade)
- [ ] CLI integration complete (`thailint method-property` command functional)
- [ ] ReadTheDocs documentation updated (mkdocs.yml, index.md)
- [ ] README.md updated with feature
