# Collection Pipeline Linter - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for the Collection Pipeline linter feature

**Scope**: Implementation of a linter that detects imperative loop patterns with embedded filtering and suggests collection pipeline refactoring

**Overview**: Primary handoff document for AI agents working on the Collection Pipeline linter.
    This linter addresses a gap in existing Python linting tools by detecting `for` loops with
    embedded filtering logic (`if/continue` patterns) that could be refactored to use collection
    pipelines (generator expressions, `filter()`, comprehensions). Based on Martin Fowler's
    "Replace Loop with Pipeline" refactoring pattern.

**Dependencies**: Existing linter patterns in `src/linters/`, AST analysis utilities

**Exports**: Progress tracking, implementation guidance, AI agent coordination

**Related**: AI_CONTEXT.md for research findings, PR_BREAKDOWN.md for detailed implementation steps

**Implementation**: TDD-first approach with dogfooding on thai-lint codebase

---

## Document Purpose

This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the Collection Pipeline linter. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## Current Status

**Current PR**: PR1 - Core Detection Engine (In Progress)
**Infrastructure State**: Ready - all prerequisites met
**Feature Target**: Detect and report loop-with-embedded-filtering anti-patterns

## Required Documents Location

```
.roadmap/in-progress/collection-pipeline-linter/
├── AI_CONTEXT.md          # Research findings and pattern analysis
├── PR_BREAKDOWN.md        # Detailed implementation steps for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## Research Summary

### The Anti-Pattern

```python
# Anti-pattern: Embedded filtering in loop body
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    if ignore_parser.is_ignored(file_path):
        continue
    violations.extend(self.lint_path(file_path))
```

### The Refactored Pattern

```python
# Collection pipeline: Filtering separated from processing
valid_files = (
    f for f in dir_path.glob(pattern)
    if f.is_file() and not ignore_parser.is_ignored(f)
)
for file_path in valid_files:
    violations.extend(self.lint_path(file_path))
```

### Why This Matters

- Based on Martin Fowler's "Replace Loop with Pipeline" refactoring
- No existing linter catches this pattern (verified gap in Ruff, Pylint, Flake8, Sourcery)
- PERF401 only catches `if` pattern, NOT `continue` pattern
- Improves code readability by separating concerns (filtering vs processing)

---

## Next PR to Implement

### START HERE: PR1 - Core Detection Engine (TDD)

**Quick Summary**:
Write tests first for detecting the core anti-patterns, then implement the detection engine.

**Pre-flight Checklist**:
- [ ] Read `.ai/docs/FILE_HEADER_STANDARDS.md` for header templates
- [ ] Read `.ai/howtos/how-to-add-linter.md` for linter development guide
- [ ] Read `.ai/docs/SARIF_STANDARDS.md` for output format requirements
- [ ] Review existing linter patterns in `src/linters/nesting/` (similar AST analysis)

**TDD Approach**:
1. Write failing tests for pattern detection
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Repeat for each pattern variant

---

## Overall Progress

**Total Completion**: 0% (0/6 PRs completed)

```
[                    ] 0% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Core Detection Engine (TDD) | In Progress | 0% | Medium | P0 | Tests first, then implementation |
| PR2 | CLI Integration | Not Started | 0% | Low | P0 | Add `thailint pipeline` command |
| PR3 | Configuration & Ignore Support | Not Started | 0% | Medium | P1 | .thailint.yaml, inline ignores |
| PR4 | Dogfooding & Fixes | Not Started | 0% | Low | P1 | Run on thai-lint codebase, fix issues |
| PR5 | Documentation | Not Started | 0% | Medium | P1 | PyPI, ReadTheDocs, DockerHub |
| PR6 | Release | Not Started | 0% | Low | P2 | Version bump, changelog, publish |

### Status Legend
- Not Started
- In Progress
- Complete
- Blocked
- Cancelled

---

## PR Details

### PR1: Core Detection Engine (TDD)
**Goal**: Implement pattern detection with tests first
**Dependencies**: None
**Key Files**:
- Create: `tests/unit/linters/collection_pipeline/test_detector.py` (FIRST)
- Create: `tests/unit/linters/collection_pipeline/test_patterns.py` (FIRST)
- Create: `src/linters/collection_pipeline/__init__.py`
- Create: `src/linters/collection_pipeline/linter.py`
- Create: `src/linters/collection_pipeline/detector.py`
- Create: `src/linters/collection_pipeline/config.py`

### PR2: CLI Integration
**Goal**: Add `thailint pipeline` command
**Dependencies**: PR1
**Key Files**:
- Modify: `src/cli.py` (add command)
- Modify: `justfile` (add lint-pipeline recipe)
- Create: `tests/unit/linters/collection_pipeline/test_cli_interface.py`

### PR3: Configuration & Ignore Support
**Goal**: Add configuration and ignore patterns
**Dependencies**: PR2
**Key Files**:
- Modify: `.thailint.yaml`
- Create: `tests/unit/linters/collection_pipeline/test_config.py`
- Create: `tests/unit/linters/collection_pipeline/test_ignore_directives.py`

### PR4: Dogfooding & Fixes
**Goal**: Run on thai-lint codebase, fix any issues found
**Dependencies**: PR3
**Key Files**:
- Run: `thailint pipeline src/`
- Fix: Any violations found in thai-lint codebase
- Update: Tests if edge cases discovered

### PR5: Documentation
**Goal**: Comprehensive documentation for all platforms
**Dependencies**: PR4
**Key Files**:
- Create: `docs/collection-pipeline-linter.md`
- Update: `README.md` (add linter to list)
- Update: `docs/cli-reference.md`
- Update: `docs/configuration.md`
- Create: Docker usage examples

### PR6: Release
**Goal**: Publish new version with collection-pipeline linter
**Dependencies**: PR5
**Key Files**:
- Update: `pyproject.toml` (version bump)
- Update: `CHANGELOG.md`
- Run: `just publish`

---

## Implementation Strategy

### TDD Workflow

```
1. Write test for pattern → Test fails (RED)
2. Implement minimal detection → Test passes (GREEN)
3. Refactor code → Tests still pass (REFACTOR)
4. Repeat for next pattern
```

### Patterns to Detect (Priority Order)

1. **Single `if/continue`**: `for x: if not cond: continue; action(x)`
2. **Multiple `if/continue`**: `for x: if not cond1: continue; if not cond2: continue; action(x)`
3. **Nested `if` without continue**: `for x: if cond: action(x)` (already caught by PERF401, lower priority)
4. **Mixed patterns**: Combination of above

### Dogfooding Targets

Files in thai-lint with potential violations:
- `src/linters/file_placement/linter.py` (verified pattern exists)
- `src/orchestrator/orchestrator.py` (likely patterns)
- Other files with `for` loops containing `continue`

---

## Success Metrics

### Technical Metrics
- [ ] All tests pass with 90%+ coverage for new code
- [ ] Pylint 10.00/10
- [ ] Xenon A-grade complexity
- [ ] All 3 output formats work (text, JSON, SARIF)

### Feature Metrics
- [ ] Detects all pattern variants
- [ ] Provides clear, actionable suggestions
- [ ] Configuration allows fine-tuning
- [ ] Inline ignore directives work

### Documentation Metrics
- [ ] PyPI description updated
- [ ] ReadTheDocs page published
- [ ] DockerHub README updated
- [ ] Examples provided for all patterns

---

## Update Protocol

After completing each PR:
1. Update the PR status to Complete
2. Fill in completion percentage
3. Add commit hash to Notes column
4. Update the "Next PR to Implement" section
5. Update overall progress percentage
6. Commit changes to this document

---

## Notes for AI Agents

### Critical Context
- This fills a gap in Python linting ecosystem (verified: Ruff, Pylint, Flake8 don't catch this)
- Based on Martin Fowler's "Replace Loop with Pipeline" refactoring
- Use TDD: write tests BEFORE implementation
- Dogfood on thai-lint's own codebase

### Common Pitfalls to Avoid
- Don't implement before writing tests
- Don't forget SARIF output format
- Don't report on patterns already caught by PERF401 (avoid duplicate warnings)
- Don't suggest changes that alter semantics (continue with side effects)

### Resources
- Martin Fowler: https://martinfowler.com/articles/refactoring-pipelines.html
- Ruff PERF401: https://docs.astral.sh/ruff/rules/manual-list-comprehension/
- Existing linter patterns: `src/linters/nesting/`, `src/linters/srp/`

---

## Definition of Done

The feature is considered complete when:
- [ ] All 6 PRs are merged to main
- [ ] Linter detects all documented anti-patterns
- [ ] Thai-lint codebase passes (dogfooding complete)
- [ ] Documentation published on PyPI, ReadTheDocs, DockerHub
- [ ] New version released with changelog entry
