# Dead Code Linter - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for Dead Code Linter with current progress tracking and implementation guidance

**Scope**: Implement a cross-language, cross-file-type orphan detection linter that builds a reference graph and uses BFS reachability from entry points to identify orphaned files, broken references, and refactor leftovers

**Overview**: Primary handoff document for AI agents working on the Dead Code Linter feature.
    Tracks current implementation progress, provides next action guidance, and coordinates AI agent work across
    8 pull requests. Contains current status, prerequisite validation, PR dashboard, detailed checklists,
    implementation strategy, success metrics, and AI agent instructions. Essential for maintaining development
    continuity and ensuring systematic feature implementation with proper validation and testing.

**Dependencies**: ast module (Python parsing), tree-sitter (TypeScript/JavaScript parsing), PyYAML (state file), src.core base classes, DRY linter two-phase pattern

**Exports**: Progress tracking, implementation guidance, AI agent coordination, and feature development roadmap

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: TDD approach with progress-driven coordination, two-phase check()/finalize() pattern, systematic validation, checklist management, and AI agent handoff procedures

---

## Document Purpose
This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the Dead Code Linter feature. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and feature requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## Current Status
**Current PR**: PR1 - Core Types, Config, and Test Infrastructure (TDD Foundation)
**Infrastructure State**: Planning complete, implementation not started
**Feature Target**: Project-level orphan detection via reference graph + BFS reachability from entry points

## Required Documents Location
```
.roadmap/planning/dead-code-linter/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## Next PR to Implement

### START HERE: PR1 - Core Types, Config, and Test Infrastructure

**Quick Summary**:
Establish foundational types, configuration dataclass, and comprehensive failing test suite defining expected behavior. This is the TDD "red" phase -- all tests should fail with ImportError or NotImplementedError. Config tests should pass.

**Pre-flight Checklist**:
- [ ] Read AI_CONTEXT.md for architecture overview
- [ ] Read PR_BREAKDOWN.md PR1 section for detailed steps
- [ ] Review DRY linter two-phase pattern at `src/linters/dry/linter.py`
- [ ] Review `src/core/base.py` for BaseLintRule interface
- [ ] Review `src/core/types.py` for Violation dataclass

**Prerequisites Complete**:
- [x] Roadmap documents created
- [x] Architecture designed (reference graph + BFS reachability)
- [x] 8-PR breakdown finalized

---

## Overall Progress
**Total Completion**: 0% (0/8 PRs completed)

```
[░░░░░░░░░░░░░░░░░░░░] 0% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Core Types, Config & TDD Tests | 🔴 Not Started | 0% | Medium | P0 | TDD red phase, ~10 test files |
| PR2 | Reference Graph & Entry Points | 🔴 Not Started | 0% | Medium | P0 | Core graph data structure |
| PR3 | Python Import Parser | 🔴 Not Started | 0% | Medium | P0 | ast-based import extraction |
| PR4 | TS/JS & Infrastructure Parsers | 🔴 Not Started | 0% | Medium | P0 | tree-sitter + regex parsing |
| PR5 | DeadCodeRule (check + finalize) | 🔴 Not Started | 0% | High | P0 | Main linter rule integration |
| PR6 | Triage Mode & State File | 🔴 Not Started | 0% | Medium | P0 | Interactive triage + .thailint-dead-code.yaml |
| PR7 | CLI Integration & Output Formats | 🔴 Not Started | 0% | Medium | P0 | CLI command + text/json/sarif |
| PR8 | Documentation & Dogfooding | 🔴 Not Started | 0% | Low | P1 | Docs + self-validation |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## PR1: Core Types, Config & TDD Tests

### Scope
Create `src/linters/dead_code/` directory structure, configuration dataclass, and comprehensive TDD test suite with all tests failing (red phase).

### Success Criteria
- [ ] `src/linters/dead_code/` directory created with `__init__.py` and `config.py`
- [ ] `DeadCodeConfig` dataclass with `from_dict()` method
- [ ] 10+ test files created in `tests/unit/linters/dead_code/`
- [ ] Config tests pass; all other tests fail with ImportError (TDD red phase)
- [ ] `just lint-full` passes on all new files
- [ ] Proper file headers on all files

---

## PR2: Reference Graph & Entry Point Detection

### Scope
Implement the core `ReferenceGraph` data structure (nodes, edges, BFS reachability) and `EntryPointDetector` for auto-detecting project entry points.

### Success Criteria
- [ ] `ReferenceGraph` handles cycles, diamonds, empty projects
- [ ] `EntryPointDetector` auto-detects Python, TypeScript, and infrastructure entry points
- [ ] Configured entry points override auto-detection
- [ ] `test_reference_graph.py` and `test_entry_point_detection.py` pass
- [ ] `just lint-full` passes

---

## PR3: Python Import Parser

### Scope
Python import extraction using `ast` module: `import X`, `from X import Y`, relative imports, dynamic import warnings.

### Success Criteria
- [ ] Resolves absolute and relative imports to file paths
- [ ] Ignores stdlib and third-party imports
- [ ] Handles syntax errors gracefully
- [ ] `test_python_import_parsing.py` passes
- [ ] `just lint-full` passes

---

## PR4: TS/JS & Infrastructure Parsers

### Scope
TypeScript/JavaScript import extraction (tree-sitter) and infrastructure reference parsing (Terraform, Docker, CI, Makefile) via regex.

### Success Criteria
- [ ] ES6, CommonJS, and dynamic imports parsed
- [ ] Dockerfile COPY/ADD, docker-compose, GitHub Actions, Terraform module sources parsed
- [ ] `test_typescript_import_parsing.py` and `test_infrastructure_parsing.py` pass
- [ ] `just lint-full` passes

---

## PR5: DeadCodeRule (check + finalize)

### Scope
Main `DeadCodeRule(BaseLintRule)` integrating all components. `check()` builds graph, `finalize()` computes reachability and generates violations.

### Success Criteria
- [ ] Two-phase check()/finalize() pattern works correctly
- [ ] Detects orphaned files, orphaned directories, broken references, refactor leftovers
- [ ] Respects ignore patterns and triage decisions
- [ ] `test_orphan_detection.py` and `test_broken_reference_detection.py` pass
- [ ] `just lint-full` passes

---

## PR6: Triage Mode & State File

### Scope
Interactive `--triage` mode, `--audit` CI gate mode, and persistent `.thailint-dead-code.yaml` state file.

### Success Criteria
- [ ] State file load/save/merge/expire roundtrip works
- [ ] Triage interactive flow with click prompts
- [ ] Audit mode exits non-zero on untriaged orphans or expired reminders
- [ ] Standard mode respects triage decisions
- [ ] `test_triage_state_file.py` and `test_triage_mode.py` pass
- [ ] `just lint-full` passes

---

## PR7: CLI Integration & Output Formats

### Scope
Register `dead-code` CLI command with `--triage`/`--audit` modes and text/json/sarif output formats.

### Success Criteria
- [ ] `thailint dead-code .` runs without error
- [ ] All three output formats produce valid output
- [ ] SARIF v2.1.0 compliant
- [ ] `--triage` and `--audit` are mutually exclusive
- [ ] Proper exit codes (0=clean, 1=violations, 2=error)
- [ ] `test_cli_integration.py` passes
- [ ] `just lint-full` passes

---

## PR8: Documentation & Dogfooding

### Scope
User documentation, config template update, README update, and self-dogfooding on thai-lint.

### Success Criteria
- [ ] `docs/dead-code-linter.md` created
- [ ] `.ai/howtos/how-to-fix-dead-code.md` created
- [ ] Config template updated with dead-code section
- [ ] README updated with dead-code linter entry
- [ ] Zero false positives when run on thai-lint itself
- [ ] `just lint-full` passes

---

## Implementation Strategy

### TDD Workflow
1. **PR1**: Write all failing tests (red phase)
2. **PR2-PR4**: Implement core components to pass tests (green phase)
3. **PR5**: Integrate components into DeadCodeRule
4. **PR6**: Add triage system
5. **PR7**: CLI integration (feature usable)
6. **PR8**: Documentation and dogfooding (feature complete)

### Two-Phase Architecture
Follow the DRY linter's `check()`/`finalize()` pattern:
- `check()` is called once per file -- builds the reference graph incrementally
- `finalize()` is called once after all files -- computes BFS reachability and generates violations
- This is required because dead code detection is inherently cross-file analysis

### Quality Gates
- Pylint: 10.00/10 exactly
- Xenon: A-grade on every function/block
- MyPy: Zero errors
- `just lint-full` passes
- All tests pass

## Success Metrics

### Technical Metrics
- [ ] 40+ unit tests passing
- [ ] 15+ CLI integration tests passing
- [ ] Pylint 10.00/10
- [ ] MyPy zero errors
- [ ] Xenon A-grade complexity
- [ ] `just lint-full` passes

### Feature Metrics
- [ ] Detects orphaned files via reference graph + BFS
- [ ] Detects orphaned directories (all children are orphans)
- [ ] Detects broken references (imports to nonexistent files)
- [ ] Detects refactor leftovers (test files whose source was deleted)
- [ ] Three modes: standard, triage, audit
- [ ] State file committed to version control
- [ ] Python + TypeScript/JS + infrastructure file support
- [ ] text/json/sarif output formats
- [ ] False positive rate < 5% on self-dogfooding

## Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Fill in completion percentage (100%)
3. Add commit hash to notes: `(commit abc1234)`
4. Add any important notes or learners
5. Update the "Next PR to Implement" section
6. Update overall progress percentage
7. Commit changes to the progress document

## Notes for AI Agents

### Critical Context
- **Two-Phase Pattern**: This linter uses `check()`/`finalize()` like the DRY linter -- `check()` collects per-file data, `finalize()` runs cross-file analysis
- **Reference Implementation**: `src/linters/dry/linter.py` for two-phase pattern
- **No New Dependencies**: Uses `ast` (stdlib), tree-sitter (already in thai-lint), regex for infrastructure parsing
- **State File**: `.thailint-dead-code.yaml` is committed to version control for team-shared triage decisions
- **Pre-commit**: Uses `pass_filenames: false` (needs whole-project context)
- **Config Loading**: Uses `context.metadata` pattern (same as DRY and method-property linters)

### Common Pitfalls to Avoid
- Don't implement code before tests (strict TDD)
- Don't forget file headers on all files
- Don't create new external dependencies -- use ast, tree-sitter, and regex
- Don't confuse `check()` (per-file collection) with `finalize()` (cross-file analysis)
- Don't report files marked "keep" in the triage state file as violations
- Don't track stdlib/third-party imports as project references
- Dynamic imports (`importlib.import_module()`) should warn but NOT create edges
- `__init__.py` files are reachable if any file in their directory is reachable

### Resources
- **DRY linter (two-phase pattern)**: `src/linters/dry/linter.py`
- **Base classes**: `src/core/base.py`, `src/core/types.py`
- **CLI registration**: `src/cli/linters/code_smells.py` (custom-option linter pattern)
- **Orchestrator finalize()**: `src/orchestrator/core.py`
- **Config template**: `src/templates/thailint_config_template.yaml`
- **File header standards**: `.ai/docs/FILE_HEADER_STANDARDS.md`
- **SARIF standards**: `.ai/docs/SARIF_STANDARDS.md`

## Definition of Done

The feature is considered complete when:
- [ ] All 8 PRs merged
- [ ] `thailint dead-code .` passes on thai-lint codebase with zero false positives
- [ ] `just lint-full` includes dead-code check
- [ ] Three modes work: standard, triage, audit
- [ ] State file `.thailint-dead-code.yaml` roundtrip works
- [ ] All output formats (text, json, sarif) produce valid output
- [ ] Documentation in `docs/dead-code-linter.md`
- [ ] README updated with dead-code feature
- [ ] Config template includes dead-code section
