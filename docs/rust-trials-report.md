# Rust Linter Validation Trials Report

**Purpose**: Documents validation trial results for Rust linters against popular, well-maintained repositories

**Scope**: False positive assessment and rule tuning for all 6 Rust-aware linter rules

**Overview**: Validation results from running all Rust linters against 6 popular Rust repositories
(ripgrep, tokio, serde, clap, reqwest, actix-web) totaling 1,774 Rust source files. Initial trials
identified three false positive patterns which were fixed through rule tuning. Post-tuning results
show zero false positives for blocking-async and significantly reduced noise for unwrap-abuse.

---

## Target Repositories

| Repository | Tag | .rs Files | Description |
|------------|-----|-----------|-------------|
| ripgrep | 15.1.0 | 100 | Gold standard Rust code |
| tokio | tokio-1.49.0 | 758 | Async runtime |
| serde | v1.0.228 | 208 | Macro-heavy serialization |
| clap | v4.5.57 | 328 | CLI library |
| reqwest | v0.13.1 | 74 | HTTP client |
| actix-web | web-v4.12.1 | 306 | Web framework |

**Total**: 1,774 Rust source files across 6 repositories.

## Summary (Post-Tuning)

| Rule | Violations | FP Pattern Found | Tuning Applied | Status |
|------|-----------|-----------------|----------------|--------|
| blocking-async | 1 | asyncify/spawn_blocking wrappers, test dirs | Wrapper detection + tests/ ignore | PASS |
| clone-abuse | 159 | Test dirs | tests/ ignore | PASS |
| unwrap-abuse | 479 | .expect() flagged, test dirs | allow_expect=True + tests/ ignore | PASS |
| srp | 194 | None | None needed | PASS |
| nesting | 248 | None | None needed | PASS |
| magic-numbers | 1,151 | None | None needed | PASS |

## Pre-Tuning vs Post-Tuning Comparison

| Rule | Before | After | Reduction |
|------|--------|-------|-----------|
| blocking-async | 27 | 1 | 96% |
| unwrap-abuse | 1,238 | 479 | 61% |
| clone-abuse | 172 | 159 | 8% |
| srp | 194 | 194 | 0% |
| nesting | 248 | 248 | 0% |
| magic-numbers | 1,151 | 1,151 | 0% |
| **Total** | **3,030** | **2,232** | **26%** |

## False Positive Patterns Found and Fixed

### 1. Test Directory Detection Gap (Fixed)

**Problem**: Rust linters checked for `#[test]` attributes and `#[cfg(test)]` modules but did not
skip files in `tests/` directories. Test utility files (e.g., `tests/util.rs`) lack these
attributes but contain idiomatic test code with `.unwrap()`, `.clone()`, and blocking calls.

**Fix**: Added `"tests/"` to the default `ignore` list in all three Rust-specific linter configs
(unwrap-abuse, clone-abuse, blocking-async).

**Impact**: Eliminated ~580 false positives across all repos.

### 2. Blocking-Async Wrapper Functions (Fixed)

**Problem**: The blocking-async detector flagged `std::fs` calls inside async functions even when
wrapped in `asyncify()`, `spawn_blocking()`, or `block_in_place()`. These wrapper functions
correctly offload blocking work to a thread pool — flagging them is a false positive.

**Example**: tokio's `src/fs/read_to_string.rs` wraps `std::fs::read_to_string` inside
`asyncify(move || std::fs::read_to_string(path))`. This is the correct pattern.

**Fix**: Added parent-chain traversal in `RustBlockingAsyncAnalyzer._check_blocking_call()` to
detect `asyncify`, `spawn_blocking`, and `block_in_place` wrapper calls and skip violations
inside them.

**Impact**: Eliminated 26 false positives (14 in tokio src/fs/, 12 in test files).

### 3. .expect() Flagged by Default (Fixed)

**Problem**: `.expect("descriptive message")` is the Rust community recommended alternative to
bare `.unwrap()` — it provides panic context. Flagging it by default is counterproductive since
the linter suggests using `.expect()` as a fix for `.unwrap()`.

**Fix**: Changed `UnwrapAbuseConfig.allow_expect` default from `False` to `True`. Users who want
to flag `.expect()` calls can set `allow_expect: false` in their config.

**Impact**: Eliminated ~400 false positives across all repos.

## Per-Repository Results

### ripgrep (@ 15.1.0)

- Total .rs files: 100
- unwrap-abuse: 75 violations
- clone-abuse: 15 violations
- blocking-async: 0 violations
- srp: 28 violations
- nesting: 28 violations
- magic-numbers: 80 violations

### tokio (@ tokio-1.49.0)

- Total .rs files: 758
- unwrap-abuse: 136 violations
- clone-abuse: 27 violations
- blocking-async: 0 violations
- srp: 61 violations
- nesting: 83 violations
- magic-numbers: 362 violations

### serde (@ v1.0.228)

- Total .rs files: 208
- unwrap-abuse: 23 violations
- clone-abuse: 13 violations
- blocking-async: 0 violations
- srp: 11 violations
- nesting: 16 violations
- magic-numbers: 494 violations

### clap (@ v4.5.57)

- Total .rs files: 328
- unwrap-abuse: 37 violations
- clone-abuse: 53 violations
- blocking-async: 0 violations
- srp: 22 violations
- nesting: 55 violations
- magic-numbers: 13 violations

### reqwest (@ v0.13.1)

- Total .rs files: 74
- unwrap-abuse: 16 violations
- clone-abuse: 20 violations
- blocking-async: 0 violations
- srp: 30 violations
- nesting: 9 violations
- magic-numbers: 20 violations

### actix-web (@ web-v4.12.1)

- Total .rs files: 306
- unwrap-abuse: 192 violations
- clone-abuse: 31 violations
- blocking-async: 1 violations
- srp: 42 violations
- nesting: 57 violations
- magic-numbers: 182 violations

## Remaining Violations Analysis

The remaining 2,232 violations are true positives or intentional design choices in these repositories.
They represent actual patterns the linters are designed to detect:

- **unwrap-abuse (479)**: Bare `.unwrap()` calls in production code. In well-maintained repos, many
  are intentional (CLI main functions, known-valid inputs) but represent places where error handling
  could be improved. This is the core value proposition of the rule.

- **magic-numbers (1,151)**: Numeric literals that could be named constants. Expected in any
  codebase, particularly in configuration and protocol handling code. Not false positives — these
  are legitimate code style suggestions.

- **nesting (248)**: Deeply nested control flow structures. These are actual complexity hotspots
  that could benefit from refactoring.

- **srp (194)**: Structs with many impl methods. These identify potential single-responsibility
  violations — large interfaces that could be decomposed.

- **clone-abuse (159)**: Clone patterns (clone-in-loop, clone chains, unnecessary clones) that
  could affect performance. These are legitimate optimization opportunities.

- **blocking-async (1)**: Single violation in `actix-http-test` — a test utility crate with source
  in `src/` rather than `tests/`. Borderline case; the crate intentionally uses blocking network
  calls in async test setup.

## Rule Tuning Applied

1. **unwrap-abuse**: Changed `allow_expect` default to `true`, added `tests/` to default ignore
2. **clone-abuse**: Added `tests/` to default ignore
3. **blocking-async**: Added `asyncify`/`spawn_blocking`/`block_in_place` wrapper detection,
   added `tests/` to default ignore

## Conclusion

All identified false positive patterns have been addressed through rule tuning. The remaining
violations represent actual patterns the linters are designed to detect. The blocking-async
detector achieves effectively zero false positives on idiomatic async Rust code. The unwrap-abuse
and clone-abuse detectors flag legitimate code patterns that, while intentional in expert-written
code, represent common mistakes in AI-generated Rust code — the primary use case for thai-lint.
