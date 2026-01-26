# Rust Linter Support - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for Rust Linter Support with current progress tracking and implementation guidance

**Scope**: Add Rust language support to thai-lint with novel AI-focused lint rules that complement (not duplicate) existing tools like Clippy

**Overview**: Primary handoff document for AI agents working on the Rust Linter Support feature.
    Tracks current implementation progress, provides next action guidance, and coordinates AI agent work across
    multiple pull requests. Contains current status, prerequisite validation, PR dashboard, detailed checklists,
    implementation strategy, success metrics, and AI agent instructions. Essential for maintaining development
    continuity and ensuring systematic feature implementation with proper validation and testing.

**Dependencies**: tree-sitter, tree-sitter-rust (optional dependency like tree-sitter-typescript)

**Exports**: Progress tracking, implementation guidance, AI agent coordination, and feature development roadmap

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: Progress-driven coordination with systematic validation, checklist management, and AI agent handoff procedures

---

## Document Purpose
This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on the Rust Linter Support feature. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and feature requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## Current Status
**Current PR**: PR1 Complete - Ready for PR2
**Infrastructure State**: Rust language detection and tree-sitter parsing implemented
**Feature Target**: Rust language detection, tree-sitter parsing, and 3 novel AI-focused lint rules

## Required Documents Location
```
.roadmap/in-progress/rust-linter-support/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
└── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## Next PR to Implement

### START HERE: PR2 - Unwrap Abuse Detector

**Quick Summary**:
Detect `.unwrap()` and `.expect()` calls outside test code. Suggest safer alternatives like `?`, `unwrap_or`, `unwrap_or_default`.

**Pre-flight Checklist**:
- [ ] Review RustBaseAnalyzer in `src/analyzers/rust_base.py` for parsing utilities
- [ ] Review rust_context.py for test detection (`is_inside_test`)
- [ ] Study existing linter pattern in `src/linters/srp/` for directory structure

**Prerequisites Complete**:
- [x] Research completed on Rust anti-patterns and existing tooling
- [x] Scope defined: Novel rules only, no Clippy duplication
- [x] PR1 implementation complete - Rust infrastructure ready

---

## Overall Progress
**Total Completion**: 17% (1/6 PRs completed)

```
[███░░░░░░░░░░░░░░░░░] 17% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Rust Infrastructure & Language Detection | 🟢 Complete | 100% | Low | P0 | Foundation complete |
| PR2 | Unwrap Abuse Detector | 🔴 Not Started | 0% | Medium | P1 | High-value AI code smell |
| PR3 | Excessive Clone Detector | 🔴 Not Started | 0% | Medium | P1 | High-value AI code smell |
| PR4 | Blocking-in-Async Detector | 🔴 Not Started | 0% | Medium | P2 | Novel rule, async-specific |
| PR5 | Extend Universal Linters to Rust | 🔴 Not Started | 0% | Medium | P2 | SRP, nesting, magic numbers |
| PR6 | Validation Trials on Popular Repos | 🔴 Not Started | 0% | Medium | P0 | Must pass before release |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## PR1: Rust Infrastructure & Language Detection

### Scope
- Add `.rs` extension to language detector
- Create `RustBaseAnalyzer` class mirroring `TypeScriptBaseAnalyzer`
- Add `tree-sitter-rust` as optional dependency
- Add basic tests for Rust file detection and parsing

### Key Files
- `src/orchestrator/language_detector.py` - Add ".rs": "rust"
- `src/analyzers/rust_base.py` - New file, tree-sitter Rust parser
- `pyproject.toml` - Add tree-sitter-rust optional dependency
- `tests/unit/analyzers/test_rust_base.py` - New test file

### Success Criteria
- [x] `detect_language(Path("foo.rs"))` returns "rust"
- [x] `RustBaseAnalyzer().parse_rust(code)` returns AST node
- [x] Tests pass with and without tree-sitter-rust installed
- [x] `just lint-full` passes

---

## PR2: Unwrap Abuse Detector

### Scope
- Detect `.unwrap()` and `.expect()` calls outside test code
- Suggest safer alternatives (?, unwrap_or, unwrap_or_default)
- Configurable: allow in tests, examples, main.rs

### Key Files
- `src/linters/rust_unwrap/` - New linter directory
- `src/linters/rust_unwrap/linter.py` - Rule implementation
- `src/linters/rust_unwrap/config.py` - Configuration dataclass
- `src/linters/rust_unwrap/analyzer.py` - tree-sitter pattern detection
- `tests/unit/linters/rust_unwrap/` - Test suite

### Success Criteria
- [ ] Detects `.unwrap()` calls in non-test Rust code
- [ ] Detects `.expect()` calls in non-test Rust code
- [ ] Ignores calls in `#[test]` functions and test modules
- [ ] Provides actionable suggestions
- [ ] All output formats work (text, json, sarif)

---

## PR3: Excessive Clone Detector

### Scope
- Detect `.clone()` abuse patterns common in AI-generated code
- Flag: clone in loops, clone chains, clone where borrow works
- Suggest: borrowing, Rc/Arc, Cow patterns

### Key Files
- `src/linters/rust_clone/` - New linter directory
- `src/linters/rust_clone/linter.py` - Rule implementation
- `src/linters/rust_clone/config.py` - Configuration
- `src/linters/rust_clone/analyzer.py` - Pattern detection
- `tests/unit/linters/rust_clone/` - Test suite

### Success Criteria
- [ ] Detects `.clone()` inside loop bodies
- [ ] Detects chained clones (`.clone().clone()`)
- [ ] Detects clone immediately before move (often unnecessary)
- [ ] Provides suggestions based on context
- [ ] All output formats work

---

## PR4: Blocking-in-Async Detector

### Scope
- Detect blocking operations inside async functions
- Flag: std::fs, std::thread::sleep, blocking network calls
- Suggest: tokio equivalents, spawn_blocking

### Key Files
- `src/linters/rust_async/` - New linter directory
- `src/linters/rust_async/linter.py` - Rule implementation
- `src/linters/rust_async/config.py` - Configuration
- `src/linters/rust_async/analyzer.py` - Pattern detection
- `tests/unit/linters/rust_async/` - Test suite

### Success Criteria
- [ ] Detects `std::fs::*` calls in async fn
- [ ] Detects `std::thread::sleep` in async fn
- [ ] Suggests tokio/async-std alternatives
- [ ] Handles nested async blocks correctly
- [ ] All output formats work

---

## PR5: Extend Universal Linters to Rust

### Scope
- Add Rust support to existing multi-language linters
- SRP: Analyze structs + impl blocks for method count
- Nesting: Calculate nesting depth in Rust functions
- Magic Numbers: Detect magic numbers in Rust code

### Key Files
- `src/linters/srp/rust_analyzer.py` - New Rust SRP analyzer
- `src/linters/nesting/rust_analyzer.py` - New Rust nesting analyzer
- `src/linters/magic_numbers/rust_analyzer.py` - New Rust magic number analyzer
- `src/linters/*/linter.py` - Add `_check_rust()` dispatch
- `tests/unit/linters/*/test_rust_*.py` - Test files

### Success Criteria
- [ ] SRP detects structs with too many impl methods
- [ ] Nesting calculates correct depth for Rust control flow
- [ ] Magic numbers detects numeric literals
- [ ] Existing Python/TypeScript behavior unchanged
- [ ] All output formats work

---

## PR6: Validation Trials on Popular Repositories

### Scope
- Run all Rust linters against popular, well-maintained Rust repositories
- Verify zero (or near-zero) false positives on idiomatic Rust code
- Document any legitimate violations found (proves value)
- Tune rules based on findings before release

### Target Repositories
Clone and test against these popular Rust projects:

| Repository | Stars | Why Test? |
|------------|-------|-----------|
| [ripgrep](https://github.com/BurntSushi/ripgrep) | 48k+ | Exemplary Rust, BurntSushi's code is gold standard |
| [tokio](https://github.com/tokio-rs/tokio) | 26k+ | Async runtime - tests async detector |
| [serde](https://github.com/serde-rs/serde) | 9k+ | Macro-heavy, tests parser robustness |
| [clap](https://github.com/clap-rs/clap) | 14k+ | CLI library, good struct/impl patterns |
| [reqwest](https://github.com/seanmonstar/reqwest) | 10k+ | HTTP client, async code |
| [actix-web](https://github.com/actix/actix-web) | 21k+ | Web framework, async heavy |

### Test Protocol
1. Clone each repository to temporary directory
2. Run each Rust linter with default configuration
3. Capture all violations in JSON format
4. Manually review each violation:
   - **True Positive**: Legitimate issue (document as proof of value)
   - **False Positive**: Idiomatic code incorrectly flagged (must fix)
5. Calculate false positive rate per rule
6. Tune rules if false positive rate > 5%

### Key Files
- `tests/integration/rust_trials/` - Trial test scripts
- `tests/integration/rust_trials/results/` - Trial results (JSON)
- `docs/rust-trials-report.md` - Summary report of findings

### Success Criteria
- [ ] All 6 target repos tested
- [ ] False positive rate < 5% per rule
- [ ] Any true positives documented as proof of value
- [ ] Rules tuned based on findings
- [ ] Trial results committed to repo

---

## Implementation Strategy

### Phase 1: Foundation (PR1)
Establish Rust parsing infrastructure. This unblocks all subsequent PRs.

### Phase 2: Novel Rules (PR2-PR4)
Implement AI-focused rules that provide unique value beyond Clippy:
- Unwrap abuse (Clippy has but allow-by-default)
- Clone abuse (more aggressive than Clippy)
- Blocking-in-async (novel, not in Clippy)

### Phase 3: Universal Extension (PR5)
Extend existing universal linters. Lower priority since Clippy covers some of these, but provides unified experience.

### Phase 4: Validation (PR6) - MUST PASS BEFORE RELEASE
Run extensive trials against popular Rust repositories to ensure:
- Zero false positives on idiomatic, well-maintained code
- Rules provide real value (find actual issues)
- Tune thresholds based on real-world data

## Success Metrics

### Technical Metrics
- [ ] 100% test coverage for new Rust analyzers
- [ ] `just lint-full` passes on all PRs
- [ ] Pylint score 10.00/10
- [ ] All complexity A-grade (Xenon)

### Feature Metrics
- [ ] Detects top 3 AI-generated Rust code smells
- [ ] Zero false positives on idiomatic Rust code
- [ ] Provides actionable suggestions for each violation
- [ ] Works with or without tree-sitter-rust installed (graceful degradation)

## Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Fill in completion percentage
3. Add any important notes or blockers
4. Update the "Next PR to Implement" section
5. Update overall progress percentage
6. Commit changes to the progress document

## Notes for AI Agents

### Critical Context
- **Do NOT duplicate Clippy rules** - Focus on rules Clippy doesn't enforce by default or novel patterns
- **tree-sitter-rust is optional** - Must handle ImportError gracefully like TypeScriptBaseAnalyzer
- **Follow existing patterns** - Mirror TypeScriptBaseAnalyzer for consistency

### Common Pitfalls to Avoid
- Don't create rules that Clippy already enforces by default
- Don't forget to handle the case where tree-sitter-rust isn't installed
- Don't break existing Python/TypeScript linter behavior
- Don't add tree-sitter-rust as a required dependency

### Resources
- `src/analyzers/typescript_base.py` - Pattern to follow for RustBaseAnalyzer
- `src/linters/srp/typescript_analyzer.py` - Pattern for language-specific analyzer
- Rust tree-sitter node types: https://github.com/tree-sitter/tree-sitter-rust
- Clippy lints reference: https://rust-lang.github.io/rust-clippy/master/index.html

## Definition of Done

The feature is considered complete when:
- [ ] All 6 PRs merged
- [ ] Rust files detected and parsed correctly
- [ ] 3 novel AI-focused lint rules working
- [ ] Universal linters extended to Rust
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CLI help shows Rust support
- [ ] **Validation trials pass** - < 5% false positive rate on popular repos
- [ ] Trial results documented and committed
