# Comment Antecedents Rule - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for the `file-header.comment-antecedents` rule

**Scope**: Detect mid-file code comments whose referent is the change that produced the code rather than the code itself, as a second rule inside the existing `file_header` linter package

**Overview**: Tracks implementation progress for a rule that flags comments a reader cannot resolve without
    the diff. The pattern set was reduced from fourteen candidate phrases to two after measurement against
    192,352 mid-file comment blocks in three codebases, two of which are open source. The rule attaches to
    the package that already owns prose scanning, so no CLI, output-format, or registration work is
    required. Implementation is strictly test-first: PR1 lands the full behavioural specification as failing
    tests and PR2 makes them pass. Includes the PR dashboard, checklists, measured release gates, and the
    record of which candidate patterns were rejected and why.

**Dependencies**: `src/linters/file_header/` (host package), `src/core/base.py`, `src/linter_config/ignore.py`

**Exports**: Progress tracking, implementation guidance, AI agent coordination

**Related**: AI_CONTEXT.md for measured evidence and rejected patterns, PR_BREAKDOWN.md for the Gherkin specification, GitHub issue #253

**Implementation**: TDD-driven development in two PRs with corpus-measured release gates

---

## Document Purpose

This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on this rule. When starting work:

1. **Read this document FIRST** to understand current progress
2. **Check "Next PR to Implement"** for what to do
3. **Read AI_CONTEXT.md before adding any pattern** — several obvious ones are already measured and rejected
4. **Reference PR_BREAKDOWN.md** for the Gherkin specification and per-PR steps
5. **Update this document** after completing each PR

---

## Current Status

**Current PR**: None started — roadmap awaiting review
**Infrastructure State**: The host package `src/linters/file_header/` exists; no comment-antecedents files exist
**Feature Target**: A default-on rule with a measured 0% false positive rate, plus an opt-in strict tier

---

## Required Documents Location

```
.roadmap/planning/comment-antecedents/
├── AI_CONTEXT.md          # Measured evidence, rejected patterns, architecture findings
├── PR_BREAKDOWN.md        # Gherkin specification and per-PR instructions
└── PROGRESS_TRACKER.md    # THIS FILE
```

---

## Next PR to Implement

### START HERE: PR1 — BDD specification as failing tests

**Quick Summary**:
Transcribe every Gherkin scenario in PR_BREAKDOWN.md into pytest test functions, one per scenario, named
after the scenario. Run them. Confirm every one fails on the missing module or missing rule id. Commit the
failing suite. Write no implementation.

**Pre-flight Checklist**:
- [ ] Read AGENTS.md and `.ai/index.yaml`
- [ ] Read `.ai/howtos/how-to-write-tests.md`
- [ ] Read `.ai/docs/FILE_HEADER_STANDARDS.md` for test file headers
- [ ] Read AI_CONTEXT.md, in particular the rejected-pattern table
- [ ] Read the full Gherkin specification in PR_BREAKDOWN.md
- [ ] Read `src/linters/file_header/linter.py` and `bash_parser.py` to see the host package

**Prerequisites Complete**:
- [x] Concept measured against three corpora
- [x] Pattern set reduced to the two that survive open-source validation
- [x] Host package chosen and its CLI inheritance verified
- [ ] Roadmap reviewed and committed

---

## Overall Progress

**Total Completion**: 0% (0/2 PRs completed)

```
[                    ] 0% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | BDD specification as failing tests | 🔴 Not Started | 0% | Medium | P0 | RED only, no implementation |
| PR2 | Implementation, dogfooding, documentation | 🔴 Not Started | 0% | Medium | P0 | Pins measured corpus baselines |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## Implementation Strategy

**Test-first, without exception.** Each PR has three phases and is not reviewable unless they happened in
order:

1. **RED** — write the scenarios. Run them. Watch them fail for the stated reason. Commit the failing tests
   as the first commit.
2. **GREEN** — minimum implementation to pass. Nothing unspecified.
3. **REFACTOR** — A-grade complexity and 10.00/10 Pylint with tests staying green.

PR1 exists solely to establish the red state. A test that has never failed has never been tested, so PR2's
corpus gates get the same treatment: assert a deliberately wrong baseline once, watch it fail, then correct
it.

**Why two PRs and not seven.** The rule attaches to `src/linters/file_header/`, which already supplies the
CLI command, all three output formats, rule discovery, header-boundary parsers, and the ignore engine. The
shipping surface is one extractor, one detector, one rule class, and two config fields.

---

## Success Metrics

### Technical Metrics

- [ ] `just lint-full` exits 0 with Pylint at exactly 10.00/10
- [ ] Xenon reports no `ERROR:xenon:` lines
- [ ] `just test` exits 0
- [ ] Every Gherkin scenario maps to one passing test
- [ ] SARIF, JSON, and text output all carry `file-header.comment-antecedents`

### Feature Metrics

- [ ] Tier-1 false positive rate of 0% reproduced on the open-source corpus gate
- [ ] thai-lint self-lints clean with the rule enabled and zero added suppressions
- [ ] All five suppression scopes pinned by passing tests
- [ ] Rejected patterns proven silent by the rejected-pattern scenarios
- [ ] Existing `file-header.validation` behaviour unchanged

---

## Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Fill in completion percentage
3. Add notes or blockers
4. Update "Next PR to Implement"
5. Commit the updated tracker

---

## Notes for AI Agents

### Critical Context

**The pattern set is small on purpose.** Fourteen candidate phrases were measured; two shipped. The
reduction is the work product, not a compromise. Read the rejected-pattern table in AI_CONTEXT.md before
proposing an addition.

**Two rejected patterns scored well on one codebase.** `this <change>` measured 91% on a private repository
and 29% on open source. `previously` measured 70–100% private and 46% open source. Single-codebase
validation is how both nearly shipped. **Any new pattern requires an open-source corpus measurement.**

**Severity is ERROR-only.** `src/core/types.py:28`. Issue #253 asks for warning severity; it does not
exist. This is why the strict tier is opt-in rather than a lower severity.

**Reporting is per comment block.** Not per line. Line-level inflates findings by roughly 60% and fires
repeatedly inside one prose paragraph.

### Common Pitfalls to Avoid

1. **Do not share `AtemporalDetector`.** Its `STATE_CHANGE` list contains `replaces?`, `formerly`,
   `old implementation`, and `new implementation`. Three of those are measured and rejected here. Same
   package, separate detector module.

2. **Do not widen `enforce_atemporal`.** It is an established default-on setting meaning header-scoped
   temporal checking. The body scan gets its own config field and its own rule id so it is independently
   configurable and suppressible.

3. **Do not modify `EXTENSION_MAP`.** `src/orchestrator/language_detector.py:31` maps `.tf`, `.yaml`, and
   `.hcl` to `unknown`, but the walk in `src/orchestrator/core.py:133` collects them anyway and
   `_get_rules_for_file` at line 530 hands every rule every file. Self-gate on suffix. Changing the map
   changes what every other registered rule sees.

4. **Do not re-derive the header boundary.** The package's parsers already know where each language's
   header ends. That knowledge is the reason this rule lives here.

5. **Do not skip a suppression scenario.** Issue #253 reports a `dry` suppression that stopped being
   honoured once its file joined an indexed duplicate group. If any suppression scope fails, stop and
   report rather than marking it xfail.

6. **Do not add a suppression comment to make the build pass.** Ask first, per issue, per file, per phase.

### Resources

- `src/linters/file_header/linter.py` — host package rule, and the header-scoping precedent at line 243
- `src/linters/file_header/bash_parser.py` — hash-comment extraction to build on
- `src/linters/print_statements/` — a package hosting two rules under one namespace
- `src/cli/linters/documentation.py` — the command that inherits the new rule via id filtering
- `.ai/docs/SARIF_STANDARDS.md` — SARIF v2.1.0 mapping
- `.ai/howtos/how-to-add-linter.md` — linter development lifecycle
- `.roadmap/complete/lazy-ignores/` — a comparable completed roadmap

---

## Definition of Done

The feature is complete when:

- [ ] Both PRs are merged
- [ ] Every Gherkin scenario in PR_BREAKDOWN.md maps to one passing test
- [ ] Tier 1 reproduces 0% false positives on the open-source corpus gate
- [ ] The rule is enabled in this repository's `.thailint.yaml` and the build is clean
- [ ] `docs/file-header-linter.md` documents both tiers, configuration, suppression, and out-of-scope
- [ ] The CHANGELOG records the default-on behaviour change
- [ ] `just lint-full` and `just test` both exit 0
- [ ] The roadmap has moved to `.roadmap/complete/comment-antecedents/`
