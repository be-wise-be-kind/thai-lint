# Magic Numbers Linter - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for Magic Numbers Linter with current progress tracking and implementation guidance

**Scope**: Development of a linter to detect magic numbers in Python and TypeScript code, encouraging use of named constants

**Overview**: Primary handoff document for AI agents working on the Magic Numbers Linter feature.
    Tracks current implementation progress, provides next action guidance, and coordinates AI agent work across
    multiple pull requests. Contains current status, prerequisite validation, PR dashboard, detailed checklists,
    implementation strategy, success metrics, and AI agent instructions. Essential for maintaining development
    continuity and ensuring systematic feature implementation with proper validation and testing.

**Dependencies**: BaseLintRule interface, Python AST, Tree-sitter (TypeScript), pytest testing framework

**Exports**: Progress tracking, implementation guidance, AI agent coordination, and feature development roadmap

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: Progress-driven coordination with systematic validation, checklist management, and AI agent handoff procedures

---

## 🤖 Document Purpose
This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the Magic Numbers Linter feature. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and feature requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## 📍 Current Status
**Current PR**: PR1 Complete - Ready for PR2
**Infrastructure State**: Ready - Base linter infrastructure exists
**Feature Target**: Production-ready magic numbers linter for Python and TypeScript

## 📁 Required Documents Location
```
.roadmap/planning/magic-numbers-linter/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## 🎯 Next PR to Implement

### ➡️ START HERE: PR2 - Python Magic Numbers Implementation

**Quick Summary**:
Implement Python magic number detection to pass all PR1 tests (TDD GREEN phase). Create MagicNumberRule class implementing BaseLintRule with Python AST analysis, context detection, configuration support, and ignore directives.

**Pre-flight Checklist**:
- [ ] Read PR1 tests in `tests/unit/linters/magic_numbers/`
- [ ] Review BaseLintRule interface in `src/core/base.py`
- [ ] Study nesting linter implementation pattern in `src/linters/nesting/`
- [ ] Review reference implementation for context detection patterns

**Prerequisites Complete**:
✅ PR1 merged - 46 comprehensive failing tests
✅ Base infrastructure exists (BaseLintRule, testing framework)
✅ Example reference implementation available
✅ Project follows TDD standards

---

## Overall Progress
**Total Completion**: 17% (1/6 PRs completed)

```
[██████                                  ] 17% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Test Suite for Python Magic Numbers Detection | 🟢 Complete | 100% | Medium | P0 | 46 tests, Pylint 10/10, A-grade |
| PR2 | Python Magic Numbers Implementation | 🔴 Not Started | 0% | Medium | P0 | Implement to pass PR1 tests |
| PR3 | Test Suite for TypeScript Magic Numbers Detection | 🔴 Not Started | 0% | Medium | P0 | TDD approach - tests first |
| PR4 | TypeScript Magic Numbers Implementation | 🔴 Not Started | 0% | High | P0 | Tree-sitter integration |
| PR5 | Self-Dogfooding: Lint Own Codebase | 🔴 Not Started | 0% | Medium | P1 | Find and fix violations in thai-lint |
| PR6 | Documentation and Integration | 🔴 Not Started | 0% | Low | P1 | README, examples, orchestrator registration |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## PR1: Test Suite for Python Magic Numbers Detection ✅ COMPLETE

### Scope
Write comprehensive test suite for Python magic number detection

### Success Criteria
- ✅ Tests organized in `tests/unit/linters/magic_numbers/`
- ✅ Tests follow pytest and project conventions
- ✅ All tests fail initially (TDD red phase) - 46/46 tests fail
- ✅ Coverage includes:
  - Basic numeric literal detection (int, float)
  - Acceptable contexts (constants, test files, small integers in range())
  - Ignore directives (`# thailint: ignore[magic-numbers]`)
  - Edge cases (negative numbers, very large numbers, scientific notation)
  - Configuration loading and defaults
- ✅ Tests pass linting (Pylint 10.00/10, Xenon A-grade)

### Implementation Summary
- **Files Created**: 5 test files + conftest.py + __init__.py
- **Test Count**: 46 comprehensive tests
- **Test Quality**: Pylint 10.00/10, Xenon A-grade complexity
- **Coverage Areas**:
  - Basic detection: 5 tests
  - Acceptable contexts: 6 tests
  - Violation details: 3 tests
  - Configuration: 9 tests
  - Ignore directives: 7 tests
  - Edge cases: 16 tests

### Notes
- All tests use Mock-based context creation following nesting linter pattern
- Tests cover NUMERIC literals only (int, float) - no strings
- Ready for PR2 implementation (TDD GREEN phase)

---

## PR2: Python Magic Numbers Implementation

### Scope
Implement Python magic number detection to pass PR1 tests

### Success Criteria
- [ ] `src/linters/magic_numbers/` module created
- [ ] `MagicNumberRule` class implements `BaseLintRule`
- [ ] Python AST analysis detects numeric literals
- [ ] Configuration support for allowed numbers and max thresholds
- [ ] Ignore directive support
- [ ] All PR1 tests pass
- [ ] Linting passes (`just lint-full` exits with code 0)

### Notes
- Extract context analysis logic (range detection, constant definitions)
- Use composition pattern like nesting linter

---

## PR3: Test Suite for TypeScript Magic Numbers Detection

### Scope
Write comprehensive test suite for TypeScript magic number detection

### Success Criteria
- [ ] Tests in `tests/unit/linters/magic_numbers/test_typescript_magic_numbers.py`
- [ ] All tests fail initially (TDD red phase)
- [ ] Coverage includes TypeScript-specific contexts
- [ ] Tests pass linting

### Notes
- Can reuse test patterns from Python tests where applicable
- Consider TypeScript-specific cases (enums, const assertions)

---

## PR4: TypeScript Magic Numbers Implementation

### Scope
Implement TypeScript magic number detection using Tree-sitter

### Success Criteria
- [ ] TypeScript analyzer using Tree-sitter
- [ ] Detects numeric literals in TypeScript/JavaScript
- [ ] All PR3 tests pass
- [ ] Linting passes

### Notes
- Follow TypeScript analyzer pattern from nesting linter
- Tree-sitter node types: `number` for numeric literals

---

## PR5: Self-Dogfooding: Lint Own Codebase

### Scope
Run magic numbers linter on thai-lint codebase and fix violations

### Success Criteria
- [ ] Magic numbers linter runs on entire codebase
- [ ] All violations either fixed or documented with ignore directives
- [ ] Linting passes (`just lint-full` exits with code 0)
- [ ] Tests still pass

### Notes
- This validates the linter's usefulness
- May reveal edge cases requiring adjustments

---

## PR6: Documentation and Integration

### Scope
Complete documentation and integrate with orchestrator

### Success Criteria
- [ ] Linter registered in orchestrator
- [ ] README updated with magic numbers section
- [ ] Example usage documented
- [ ] CLI integration complete
- [ ] All tests pass
- [ ] Full linting passes

### Notes
- Follow documentation standards from `.ai/docs/FILE_HEADER_STANDARDS.md`

---

## 🚀 Implementation Strategy

**TDD Approach**:
1. Write failing tests first (red phase)
2. Implement minimal code to pass tests (green phase)
3. Refactor for quality (refactor phase)
4. Run full linting to ensure A-grade complexity
5. Dogfood the linter on own codebase

**Language Support**:
- Start with Python (simpler AST)
- Add TypeScript (requires Tree-sitter integration)
- Both languages share common patterns where possible

**Quality Focus**:
- All code must pass `just lint-full` (Pylint 10.00/10, Xenon A-grade)
- Tests must be comprehensive and maintainable
- Follow existing linter patterns for consistency

## 📊 Success Metrics

### Technical Metrics
- [ ] Test coverage ≥ 80%
- [ ] All linting passes (Pylint 10.00/10)
- [ ] All complexity A-grade (Xenon)
- [ ] No failing tests
- [ ] CI/CD pipeline green

### Feature Metrics
- [ ] Detects magic numbers in Python
- [ ] Detects magic numbers in TypeScript
- [ ] Supports ignore directives
- [ ] Configurable allowed numbers
- [ ] False positive rate < 5% (validate during dogfooding)

## 🔄 Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Fill in completion percentage
3. Add commit hash to notes: `(commit abc1234)`
4. Update the "Next PR to Implement" section
5. Update overall progress percentage
6. Commit changes to the progress document

## 📝 Notes for AI Agents

### Critical Context
- **NUMBERS ONLY**: Only detect numeric literals (int, float), NOT strings
- **TDD Mandatory**: Tests must be written and failing before implementation
- **Reference Implementation**: Use `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/literals/magic_number_rules.py` for patterns, but adapt to thai-lint architecture
- **Follow Patterns**: Study nesting linter for structure and patterns

### Common Pitfalls to Avoid
- ❌ Don't detect string literals (magic strings are out of scope)
- ❌ Don't skip TDD - tests must come first
- ❌ Don't copy example code directly - adapt to thai-lint patterns
- ❌ Don't add suppression comments without user permission
- ❌ Don't commit code that doesn't pass `just lint-full`

### Resources
- **Example**: `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/literals/magic_number_rules.py`
- **Test Guide**: `.ai/howtos/how-to-write-tests.md`
- **Linting Guide**: `.ai/howtos/how-to-fix-linting-errors.md`
- **Refactoring Guide**: `.ai/howtos/how-to-refactor-for-quality.md`
- **Pattern Reference**: `src/linters/nesting/` (similar structure)

## 🎯 Definition of Done

The feature is considered complete when:
- [ ] All 6 PRs merged to main
- [ ] Python magic number detection working
- [ ] TypeScript magic number detection working
- [ ] thai-lint codebase passes its own magic numbers linter
- [ ] Documentation complete
- [ ] All tests passing
- [ ] All linting passing (Pylint 10.00/10, Xenon A-grade)
- [ ] Feature registered in orchestrator
- [ ] CLI integration complete
