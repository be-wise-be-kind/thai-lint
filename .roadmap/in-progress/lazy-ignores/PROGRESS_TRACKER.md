# Lazy Ignores Linter - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for the lazy-ignores linter feature

**Scope**: Detect unjustified linting ignores and test skips in AI-generated code. Enforces header-based suppression declarations with human approval requirements.

**Overview**: This document tracks implementation progress for a new `thailint lazy-ignores` command that detects when AI agents add linting suppressions (`# noqa`, `# type: ignore`, etc.) without proper justification. Uses a header-based declaration model where suppressions must be documented in the file header's `Suppressions:` section. Includes TDD approach, dogfooding on thai-lint itself, and documentation for PyPI publishing.

**Dependencies**: Existing file-header linter infrastructure (`src/linters/file_header/`), CLI patterns (`src/cli/linters/`)

**Exports**: Progress tracking, implementation guidance, AI agent coordination

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: TDD-driven development with systematic validation and 8-PR breakdown

---

## Document Purpose

This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the lazy-ignores linter. When starting work:
1. **Read this document FIRST** to understand current progress
2. **Check "Next PR to Implement"** for what to do
3. **Reference PR_BREAKDOWN.md** for detailed instructions
4. **Update this document** after completing each PR

---

## Current Status

**Current PR**: PR2 - Python Ignore Detection - READY TO START
**Infrastructure State**: PR1 complete - PythonIgnoreDetector and SuppressionsParser implemented
**Feature Target**: Production-ready linter with full test coverage, integrated into thai-lint quality gates

---

## Required Documents Location

```
.roadmap/in-progress/lazy-ignores/
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
└── AI_CONTEXT.md          # Feature architecture and design decisions
```

---

## Next PR to Implement

### PR1 - Core Infrastructure & Python Tests (TDD) - COMPLETE

**Quick Summary**: Created failing tests, then implemented PythonIgnoreDetector and SuppressionsParser.

**Completed**:
- [x] Created test files with @pytest.mark.skip for TDD approach
- [x] Created `src/linters/lazy_ignores/types.py` with IgnoreType enum, IgnoreDirective dataclass
- [x] Created `src/linters/lazy_ignores/config.py` with LazyIgnoresConfig
- [x] Created test files: test_python_ignore_detection.py, test_thailint_ignore_detection.py, test_typescript_detection.py, test_header_parser.py, test_orphaned_detection.py, test_violation_messages.py
- [x] Implemented `src/linters/lazy_ignores/python_analyzer.py` - PythonIgnoreDetector
- [x] Implemented `src/linters/lazy_ignores/header_parser.py` - SuppressionsParser
- [x] All quality gates pass (ruff, pylint, flake8, mypy, xenon)
- [x] 26 tests passing, 44 skipped (TDD for future PRs)

---

### START HERE: PR6 - CLI Integration & LazyIgnoresRule

**Quick Summary**: Wire up the LazyIgnoresRule class with CLI integration.

**Prerequisites**:
- [x] PythonIgnoreDetector implemented
- [x] SuppressionsParser implemented

**Remaining**:
- [ ] Create `src/linters/lazy_ignores/linter.py` with LazyIgnoresRule class
- [ ] Create `src/linters/lazy_ignores/violation_builder.py` for agent guidance messages
- [ ] Register CLI command in `src/cli/linters/code_patterns.py`
- [ ] Update tests: test_orphaned_detection.py, test_violation_messages.py
- [ ] Remove skip markers from passing tests

**Detailed Steps**: See PR_BREAKDOWN.md → PR6 section

---

## Overall Progress

**Total Completion**: 38% (PR1-3 complete, 3/8 PRs fully completed)

```
[████░░░░░░] 38% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Core Infrastructure & Python Tests (TDD) | 🟢 Complete | 100% | Medium | P0 | TDD tests + types + config done |
| PR2 | Python Ignore Detection | 🟢 Complete | 100% | Medium | P0 | PythonIgnoreDetector implemented |
| PR3 | Header Suppressions Parser | 🟢 Complete | 100% | Medium | P0 | SuppressionsParser implemented |
| PR4 | TypeScript/JavaScript Detection | 🔴 Not Started | 0% | Medium | P1 | @ts-ignore, eslint-disable patterns |
| PR5 | Test Skip Detection | 🔴 Not Started | 0% | Low | P1 | pytest.mark.skip, it.skip() |
| PR6 | CLI Integration & Output Formats | 🔴 Not Started | 0% | Medium | P0 | Wire up CLI, text/json/sarif output |
| PR7 | Dogfooding - Internal Use | 🔴 Not Started | 0% | Low | P1 | Add to just lint-full, fix own violations |
| PR8 | Documentation & PyPI Prep | 🔴 Not Started | 0% | Low | P2 | README, examples, user docs |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## Implementation Strategy

### TDD Approach
1. **PR1**: Write failing tests that define behavior
2. **PR2-5**: Implement features to make tests pass
3. **PR6**: Integration and CLI
4. **PR7**: Validate by using on ourselves
5. **PR8**: Document for users

### Quality Gates Per PR
- [ ] All tests pass
- [ ] Pylint score 10.00/10
- [ ] Xenon A-grade complexity
- [ ] No new violations introduced

---

## Success Metrics

### Technical Metrics
- [ ] 90%+ test coverage for lazy_ignores module
- [ ] All output formats work (text, json, sarif)
- [ ] Performance: < 100ms per file scanned
- [ ] Zero false positives on legitimate patterns

### Feature Metrics
- [ ] Detects all common Python ignore patterns
- [ ] Detects all common TypeScript/JavaScript patterns
- [ ] Error messages guide AI agents correctly
- [ ] Orphaned header entries detected

---

## Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Add commit hash to Notes column: "Description (commit abc1234)"
3. Fill in completion percentage (100%)
4. Update the "Next PR to Implement" section
5. Update overall progress percentage and bar
6. Commit changes to this document

---

## Notes for AI Agents

### Critical Context
- This linter enforces **header-based suppression declarations**
- All ignores must be documented in file header `Suppressions:` section
- Error messages must explicitly tell agents to **get human approval**
- Orphaned entries (declared but not used) are violations

### Common Pitfalls to Avoid
- Don't add inline comments as justification - must be in header
- Don't allow empty justifications
- Don't forget to normalize rule IDs (PLR0912 vs plr0912)
- Don't skip orphaned detection - staleness is important

### Resources
- Template linter: `src/linters/nesting/linter.py`
- Header parsing: `src/linters/file_header/python_parser.py`
- CLI patterns: `src/cli/linters/code_patterns.py`
- Violation type: `src/core/types.py`

---

## Definition of Done

The feature is complete when:
- [ ] All 8 PRs merged to main
- [ ] 90%+ test coverage
- [ ] thai-lint passes its own lazy-ignores check
- [ ] Documentation published in docs/
- [ ] Added to `just lint-full` command
- [ ] README.md updated with new linter
