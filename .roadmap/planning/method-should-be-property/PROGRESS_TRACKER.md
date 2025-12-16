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
**Current PR**: Planning Complete - Ready for PR1
**Infrastructure State**: Roadmap created, awaiting implementation
**Feature Target**: Production-ready method-should-be-property linter for Python

## Required Documents Location
```
.roadmap/planning/method-should-be-property/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## Next PR to Implement

### START HERE: PR1 - Test Suite for Python Method Detection

**Quick Summary**:
Create comprehensive test suite for detecting Python methods that should be @property decorators. Tests should cover all detection patterns and exclusion rules defined in AI_CONTEXT.md.

**Pre-flight Checklist**:
- [ ] Read PR_BREAKDOWN.md Section PR1 for detailed instructions
- [ ] Read AI_CONTEXT.md for detection patterns and exclusions
- [ ] Review existing test patterns in `tests/unit/linters/print_statements/`
- [ ] Ensure local development environment is set up (`just install`)

**Prerequisites Complete**:
- [x] Research on best practices complete (PEP 8, Pylint discussions)
- [x] Confirmed no existing major linter implements this rule
- [x] Roadmap documents created

---

## Overall Progress
**Total Completion**: 0% (0/5 PRs completed)

```
[                                        ] 0% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Test Suite for Python Method Detection | Not Started | 0% | Medium | P0 | TDD red phase - tests must fail initially |
| PR2 | Python Implementation | Not Started | 0% | Medium | P0 | TDD green phase - make tests pass |
| PR3 | CLI Integration | Not Started | 0% | Low | P0 | Add `thailint method-property` command |
| PR4 | Self-Dogfooding: Lint Own Codebase | Not Started | 0% | Medium | P1 | Validate linter on thai-lint codebase |
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
- [ ] Tests organized in `tests/unit/linters/method_property/`
- [ ] Tests follow pytest and project conventions
- [ ] All tests fail initially (TDD red phase)
- [ ] Coverage includes all detection patterns from AI_CONTEXT.md
- [ ] Coverage includes all exclusion rules from AI_CONTEXT.md
- [ ] Tests pass linting (Pylint 10.00/10, Xenon A-grade)

### Key Test Categories
1. **Basic Detection** - Simple attribute returns, get_* prefix, computed values
2. **Exclusion Rules** - Parameters, side effects, decorators, test files
3. **Configuration** - Custom thresholds, ignore patterns
4. **Ignore Directives** - Line-level, method-level ignores
5. **Edge Cases** - Empty files, Unicode, syntax errors

---

## PR2: Python Implementation

### Scope
Implement Python method-should-be-property detection to pass PR1 tests.

### Success Criteria
- [ ] `src/linters/method_property/` module created
- [ ] `MethodPropertyRule` class implements `MultiLanguageLintRule`
- [ ] Python AST analysis detects all patterns from AI_CONTEXT.md
- [ ] All exclusion rules properly implemented
- [ ] Configuration support for thresholds and ignore patterns
- [ ] All PR1 tests pass
- [ ] Linting passes (`just lint-full` exits with code 0)

---

## PR3: CLI Integration

### Scope
Add CLI command for method-property linter.

### Success Criteria
- [ ] `thailint method-property` command registered in `src/cli.py`
- [ ] Supports `--config`, `--format`, `--recursive` options
- [ ] All three output formats work (text, json, sarif)
- [ ] Help text with examples
- [ ] Exit codes: 0 (clean), 1 (violations), 2 (error)

---

## PR4: Self-Dogfooding: Lint Own Codebase

### Scope
Run method-property linter on thai-lint codebase and address violations.

### Success Criteria
- [ ] Linter runs on entire codebase
- [ ] All violations either fixed or documented with ignore directives
- [ ] Linting passes (`just lint-full` exits with code 0)
- [ ] Tests still pass

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
