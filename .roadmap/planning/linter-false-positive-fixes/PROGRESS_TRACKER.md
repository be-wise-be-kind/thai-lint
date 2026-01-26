# Linter False Positive Fixes - Progress Tracker & AI Agent Handoff Document

**Purpose**: Primary AI agent handoff document for fixing false positives identified during the codebase evaluation

**Scope**: Fix false positive patterns in stateless-class, magic-numbers, and SRP linters based on evaluation of 10 popular Python projects

**Overview**: Primary handoff document for AI agents working on reducing false positives in thai-lint. Identified during evaluation of Flask, FastAPI, Requests, Pydantic, Click, Rich, Scikit-learn, Pandas, Ansible, and HTTPie repositories.

**Dependencies**: Evaluation results at `/home/stevejackson/mnt/toshiba/thai-lint-eval/results/`

**Exports**: Progress tracking, implementation guidance, AI agent coordination

**Related**: AI_CONTEXT.md for feature overview, PR_BREAKDOWN.md for detailed tasks

**Implementation**: TDD approach - write failing tests from real false positives, then fix linters

---

## 🤖 Document Purpose
This is the **PRIMARY HANDOFF DOCUMENT** for AI agents working on false positive fixes. When starting work on any PR, the AI agent should:
1. **Read this document FIRST** to understand current progress and feature requirements
2. **Check the "Next PR to Implement" section** for what to do
3. **Reference the linked documents** for detailed instructions
4. **Update this document** after completing each PR

## 📍 Current Status
**Current PR**: PR1 - Stateless Class Test Exemptions
**Infrastructure State**: Ready - evaluation complete, false positives documented
**Feature Target**: Reduce false positive rate by >50% while maintaining true positive detection

## 📁 Required Documents Location
```
.roadmap/planning/linter-false-positive-fixes/
├── AI_CONTEXT.md          # Overall feature architecture and context
├── PR_BREAKDOWN.md        # Detailed instructions for each PR
├── PROGRESS_TRACKER.md    # THIS FILE - Current progress and handoff notes
```

## 🎯 Next PR to Implement

### ➡️ START HERE: PR1 - Stateless Class Test Exemptions

**Quick Summary**:
Add exemptions to the stateless-class linter for test classes and mixin classes. These are the highest-volume false positives (20+ instances across repos).

**Pre-flight Checklist**:
- [ ] Review false positive examples in evaluation results
- [ ] Read existing stateless-class linter implementation
- [ ] Understand current detection logic

**Prerequisites Complete**:
- [x] Evaluation complete
- [x] False positives documented in findings-report.md
- [x] UTF-8 encoding fix merged (PR #177)

---

## Overall Progress
**Total Completion**: 0% (0/5 PRs completed)

```
[░░░░░░░░░░░░░░░░░░░░] 0% Complete
```

---

## PR Status Dashboard

| PR | Title | Status | Completion | Complexity | Priority | Notes |
|----|-------|--------|------------|------------|----------|-------|
| PR1 | Stateless Class Test Exemptions | 🔴 Not Started | 0% | Medium | P0 | 20+ false positives |
| PR2 | Stateless Class Mixin Exemptions | 🔴 Not Started | 0% | Medium | P0 | 3+ false positives |
| PR3 | Magic Numbers Definition File Exemption | 🔴 Not Started | 0% | High | P1 | 67 false positives in status_codes.py |
| PR4 | Magic Numbers Standard Values Allowlist | 🔴 Not Started | 0% | Medium | P1 | Ports, exit codes |
| PR5 | Nesting Linter Elif Bug Fix | 🔴 Not Started | 0% | Medium | P0 | Elif chains counted as +1 depth each |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked
- ⚫ Cancelled

---

## PR1: Stateless Class Test Exemptions

### Scope
Add exemptions for test classes in stateless-class linter:
- Classes starting with `Test`
- Classes in files starting with `test_`
- Classes in `tests/` directories
- Classes inheriting from `unittest.TestCase`

### False Positives This Fixes
- `TestCaseInsensitiveDict` (Requests)
- `TestMorselToCookieExpires` (Requests)
- `TestHelpers` (Flask)
- `TestGenericHandlers` (Flask)
- 16+ more across evaluated repos

### Success Criteria
- [ ] Tests written for each exemption pattern
- [ ] Linter correctly exempts test classes
- [ ] No regression in true positive detection
- [ ] `just test` passes

---

## PR2: Stateless Class Mixin Exemptions

### Scope
Add exemptions for mixin classes:
- Classes with "Mixin" in name
- Classes where methods use `self` to access attributes (implying external state)

### False Positives This Fixes
- `SessionRedirectMixin` (Requests)
- `RequestEncodingMixin` (Requests)
- `RequestHooksMixin` (Requests)

### Success Criteria
- [ ] Tests written for mixin exemption patterns
- [ ] Linter correctly exempts mixin classes
- [ ] `just test` passes

---

## PR3: Magic Numbers Definition File Exemption

### Scope
Detect and exempt "constant definition files" - files that map numbers to names:
- Detect dictionary patterns mapping int keys to string values
- Exempt the entire file if it matches the pattern
- Special case for HTTP status codes

### False Positives This Fixes
- 67 false positives in `requests/status_codes.py`
- Similar patterns in other repos

### Success Criteria
- [ ] Detection logic for constant definition files
- [ ] Tests with real status_codes.py content
- [ ] `just test` passes

---

## PR4: Magic Numbers Standard Values Allowlist

### Scope
Add allowlist for universally-known values:
- Network ports: 80 (HTTP), 443 (HTTPS), 22 (SSH), 21 (FTP)
- Exit codes: 0 (success), 1 (error)
- Optional: Configurable allowlist

### False Positives This Fixes
- Port checks in session handling code
- Exit code checks

### Success Criteria
- [ ] Configurable allowlist
- [ ] Default allowlist for common values
- [ ] Tests for allowlist behavior
- [ ] `just test` passes

---

## PR5: Nesting Linter Elif Bug Fix

### Scope
Fix the nesting depth calculation to not count elif branches as additional nesting levels:
- `if/elif/elif` should be counted as depth 1, not depth 3
- Only true nesting (inside a block) should increase depth

### False Positives This Fixes
- `legacy_windows_render` reported as 18 levels when actual is 5-6
- `decode_line` reported as 13 levels when actual is ~6
- `__rich_console__` reported as 12 levels when actual is ~5
- Many more across all evaluated repos

### Root Cause
The nesting analyzer is treating each `elif` clause as +1 to nesting depth. In the windows renderer function with 14 elif branches, this incorrectly reports 4 + 14 = 18 levels.

### Success Criteria
- [ ] Tests written with elif chains verifying correct depth
- [ ] `if/elif/elif/elif` counts as depth 1, not depth 4
- [ ] True nested if statements still counted correctly
- [ ] `just test` passes

---

## 🚀 Implementation Strategy

### Approach
1. **TDD**: Write failing tests first using real false positive examples
2. **Minimal Changes**: Only modify detection logic, not output/reporting
3. **Configuration**: Add config options where appropriate
4. **Documentation**: Update linter docs with new exemptions

### PR Order
PR1 → PR2 → PR3 → PR4 (no dependencies, could parallelize)

## 📊 Success Metrics

### Technical Metrics
- [ ] All tests pass
- [ ] No regression in existing tests
- [ ] Linting passes (`just lint`)

### Feature Metrics
- [ ] >50% reduction in false positives when re-run on evaluated repos
- [ ] Zero true positives incorrectly filtered

## 🔄 Update Protocol

After completing each PR:
1. Update the PR status to 🟢 Complete
2. Fill in completion percentage
3. Add commit hash to Notes column
4. Update the "Next PR to Implement" section
5. Update overall progress percentage
6. Commit changes to the progress document

## 📝 Notes for AI Agents

### Critical Context
- Evaluation results at `/home/stevejackson/mnt/toshiba/thai-lint-eval/`
- False positive documentation at `findings-report.md` in eval directory
- Use real code examples from evaluated repos for tests

### Common Pitfalls to Avoid
- Don't over-filter - test classes in production code ARE a smell
- Mixin detection should verify `self` usage, not just naming
- Magic number detection must not exempt actual magic numbers

### Resources
- Evaluation findings: `/home/stevejackson/mnt/toshiba/thai-lint-eval/findings-report.md`
- Stateless class linter: `src/linters/stateless_class/`
- Magic numbers linter: `src/linters/magic_numbers/`

## 🎯 Definition of Done

The feature is considered complete when:
- [ ] All 5 PRs merged
- [ ] Re-run evaluation shows >50% false positive reduction
- [ ] No regression in true positive detection
- [ ] Documentation updated
