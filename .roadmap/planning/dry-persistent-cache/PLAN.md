# DRY Linter: Persistent Cross-Run Index + Per-File Incremental Linting

## Context

Right now `thai-lint dry` is the only architectural linter in this repo that can't be run
per-file the way `nesting`/`srp`/`magic-numbers` are — it has to see every file in one process
before it can report anything, because duplicate detection is inherently a cross-file
relationship, not a single-file property. This session's benchmarking against a real
~2,900-file monorepo (qbench) found and fixed five unrelated O(n²)-class performance bugs in
DRY, taking a full-tree scan from "doesn't complete in 20+ minutes" down to **143.87s**. That's
good enough for a CI/nightly gate, but nowhere near fast enough for a blocking pre-commit hook —
and it can't be, structurally, as long as every invocation re-derives the whole tree from
scratch. The only way to get pre-commit-speed DRY linting is to give it a durable memory of the
rest of the codebase, so a commit touching 50 files only pays the cost of those 50, while still
correctly catching duplicates against the other ~2,850 unchanged files.

This isn't a new idea — persistent caching for DRY was built once (`.roadmap/complete/dry-linter/`,
Oct 2025), shipped, then **removed** four months later (commit `e4f3cb6`, "#35") after causing
false positives that persisted after the underlying duplicate was fixed. This plan exists to
bring the capability back without repeating that failure — the root cause turned out to be a
narrow, well-understood, and avoidable bug (below), not evidence that the approach is unsound.

**Intended outcome**: `thai-lint dry <changed files>` gives a correct, complete answer (catching
duplicates against the *whole* indexed codebase) using only the cost of the files actually
passed in, with a durable on-disk index that survives between CLI invocations and self-heals if
something drifts out of sync.

## Prior art: what broke last time, precisely

Read the actual removed code (`git show e4f3cb6^:src/linters/dry/cache.py` and the diff at
`e4f3cb6`) rather than relying on the commit message. Findings:

- **Schema**: `files(file_path PK, mtime, hash_count, last_scanned)` +
  `code_blocks(id, file_path, hash_value, start_line, end_line, snippet, FK file_path → files.file_path ON DELETE CASCADE)`.
- **Freshness** (`is_fresh`): pure `cached_mtime == current_mtime` equality. No content hash, no
  size check — nothing but mtime.
- **The actual bug**: `save()` did `DELETE FROM files WHERE file_path=?` then inserted fresh
  rows, relying on `ON DELETE CASCADE` to also purge that file's old `code_blocks` rows. **SQLite
  only enforces `ON DELETE CASCADE` if `PRAGMA foreign_keys = ON` is set on the connection — and
  it never was, anywhere in this codebase.** So the `files` row was replaced, but every prior
  `code_blocks` row for that file stayed forever, orphaned. `load()` returned *all* rows for a
  file_path with no way to distinguish current from stale. Net effect: fix a duplicate, rescan
  (mtime changed → cache "stale" → re-analyze → **add** new rows), and the pre-fix block is still
  sitting in `code_blocks` from the previous save, still matching against whatever it used to
  duplicate. That is exactly "false positives after fixes." It's a one-line-class bug (missing
  explicit `DELETE FROM code_blocks WHERE file_path=?`), not a fundamental flaw.
- `cleanup_stale()` (age-based purge) had the identical orphaning problem and, per the actual
  code, **was never called from any production path** — dead code even before removal.
- The 12-test suite covering this (`test_cache_operations.py`, deleted in the same commit) did
  not test "fix a duplicate, verify the violation disappears on next run" — the exact scenario
  that broke. Test coverage would not have caught this.
- Today, `DRYCache` still exists but is 100% ephemeral: `storage_mode="memory"` → `sqlite3.connect(":memory:")`;
  `storage_mode="tempfile"` → `NamedTemporaryFile(delete=True)`, auto-unlinked, random name, never
  reused. Zero persistence across invocations. The CLI's `--no-cache` sets a `cache_enabled` key
  that `DRYConfig.from_dict` never reads (dead), and `--clear-cache` unlinks a
  `.thailint-cache/dry.db` path that the storage layer never actually creates (dead). The
  `files` table is still populated but nothing ever reads it back for freshness — pure vestigial
  plumbing left over from the removed feature, evidently scaffolded in anticipation of exactly
  this work.
- **Existing reusable plumbing**: `justfile`'s `just lint-full changed` already resolves
  `git diff --cached --name-only --diff-filter=ACM` and passes just those files to every linter
  including `dry` — but for DRY this is currently a false promise: passing only the changed files
  means DRY can never see, and therefore can never match against, the unchanged files that make
  up the rest of the duplicate story. This is the correctness gap this plan closes.

## Prerequisite blocker found during this planning session (must fix first)

All three block-hashing call sites (`python_analyzer.py:282`, `typescript_analyzer.py:283`,
`token_hasher.py:165`) compute `hash_value = hash(snippet)` using **Python's built-in `hash()`**,
which salts string hashing with a per-process-random seed (`PYTHONHASHSEED`) by default — a
security mitigation against hash-flooding, not a bug, but fatal for this plan as-is: the same
code block would get a **different** `hash_value` in every new process. Persist that and query
it later from a different process and nothing will ever match. This has zero effect on today's
single-process, single-run behavior (which is why it's never been noticed), but it must be
replaced with a stable, deterministic hash (e.g. `hashlib.blake2b(snippet.encode(), digest_size=8)`
truncated to an int, or `zlib.crc32`) before any cross-run persistence work, as its own small,
low-risk, behavior-preserving-within-a-run PR.

## Decisions

- **Diff-scoped invocation, not self-detecting whole-tree walk.** The caller (pre-commit hook /
  CI step) passes the changed file list — same model `nesting`/`srp` already use, and the same
  git-diff mechanism the justfile already has (`just lint-full changed`). This is the more
  deterministic of the two options considered: the file set is a pure function of git state
  (a specific ref comparison), not of filesystem mtime or of what happened to be cached from a
  prior run on this machine. It also means DRY needs no git-awareness of its own — it just needs
  to do the right thing when handed a subset of files.
- **Fix `--parallel` mode first, as its own preceding PR.** Independently of persistence, this
  session's research found `thai-lint dry --parallel` **silently returns zero violations today**:
  `Orchestrator.lint_files_parallel` runs each file in a separate worker process, each
  constructing a fresh `Orchestrator`/`DRYRule` with its own isolated in-memory store; workers
  always return `[]` for DRY (violations are deferred to `finalize()`); back in the main process,
  `finalize()` runs on a `DRYRule` instance that never had `check()` called on it (all processing
  happened in throwaway workers), so `self._storage is None` and it short-circuits to `[]`. This
  is fixable without any persistence machinery — it just needs cross-file state to be centralized
  within a single run — and doing it first de-risks the harder persistent-index work by proving
  out "shared state across the workers of one run" before tackling "shared state across separate
  runs."
- **v1 scope: duplicate code blocks only.** Duplicate-constant detection is already fast after
  this session's fix (~7.6s end-to-end on the full qbench corpus) and runs on a wholly separate,
  in-memory, non-SQLite code path (`self._constants` list → `find_constant_groups`). No urgent
  pressure to make it incremental; extend it later with the same pattern once this is proven.

## Measured viability (real numbers from this session, not a new prototype)

- Full `apps/qbench` tree (2,946 files, all languages), DRY-only, isolated from other linters,
  **after all five perf fixes**: **143.87s**, 16,090 violations.
- Component-level: pure Python analyze+store+violation-gen phase over 2,943 Python files
  (286,484 blocks, 12,641 duplicate hash groups): ~19s analyze + 0.2s violation-gen.
- A single large pathological file (40,548-line vendored JS bundle) that previously didn't
  complete in 30+ seconds: **2.17s** after the tree-sitter walk fix.
- **Extrapolated incremental win**: if a typical commit touches ~50 files out of ~2,946, and
  per-file analysis averages ~6.5ms (19s / 2,943, Python-heavy estimate), re-indexing just the
  changed set costs on the order of low hundreds of milliseconds, plus O(1)-per-block index
  lookups for cross-file matching — landing in low single-digit seconds, not 143s. This matches
  the original (removed) feature's own measured claim for the same shape of workload ("typical
  commit: 50 rehashed, 9,950 cached, ~15s" on a 10K-file corpus) and is the number this plan
  should validate for real once built (see Release Gates).

## Design

### PR1 — Fix `--parallel` mode (no persistence yet)

Problem is at the orchestrator level, not DRY-specific: any rule with a meaningful `finalize()`
(currently exactly two in the whole codebase: `DRYRule`, `StringlyTypedRule` — confirm the latter
has the same exposure while implementing, flag/fix if so) cannot correctly run its per-file
`check()` in isolated worker processes and expect `finalize()` on the main process to see
anything.

Fix: in `Orchestrator._execute_parallel_linting` (`src/orchestrator/core.py`), workers should
return their raw per-file analysis output (not violations) for rules that carry cross-file
state, and the main process aggregates that output into **one** shared rule instance before
calling `finalize()` once, centrally. Concretely for DRY: worker's `DRYRule.check()` needs a way
to hand back the `CodeBlock`s (and extracted constants) it collected for that file, rather than
having its own `DuplicateStorage` be the only place they land; the main process's own single
`DRYRule` instance ingests every worker's blocks into its one `DuplicateStorage` before
`finalize()`. This is a contained, well-scoped fix — no schema, no disk persistence, just making
one run's parallel execution semantically equal to sequential execution.

### PR2 — Stable content hashing (prerequisite)

Replace `hash(snippet)` with a deterministic hash at all three call sites
(`python_analyzer.py`, `typescript_analyzer.py`, `token_hasher.py`). Pick one stable hash
function, reuse it everywhere blocks are hashed (consistency matters more than which specific
algorithm). Behavior-preserving within a single run (same relative uniqueness/collision
properties, just a different concrete integer) — should not change any existing test's
expectations about which blocks are/aren't duplicates, only the literal `hash_value` stored.

### PR3 — Persistent cross-run index

**Storage location**: a real on-disk SQLite file, not `:memory:`/auto-delete tempfile — e.g.
`.thailint-cache/dry.db` relative to project root (the CLI's `--clear-cache` already references
this exact path; it just needs the storage layer to actually use it). Gitignored (`.gitignore`
already has an entry for `.thailint-cache/` — confirm from the #35-era removal whether it's still
present or needs restoring).

**Schema** (same shape as before, deliberately, with the two changes that fix the historical bug):

```sql
CREATE TABLE files (
    file_path TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,      -- was `mtime REAL` — content hash, not mtime
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE code_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value INTEGER NOT NULL,     -- now from the stable hash (PR2)
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    snippet TEXT NOT NULL
    -- deliberately NO reliance on FK ON DELETE CASCADE for correctness
);
CREATE INDEX idx_hash_value ON code_blocks(hash_value);
CREATE INDEX idx_file_path ON code_blocks(file_path);
CREATE TABLE schema_meta (version INTEGER NOT NULL);  -- SCHEMA_VERSION was declared, never used; use it now
```

**The direct fix for the historical bug — explicit delete-before-insert, in one transaction,
never dependent on any PRAGMA:**

```python
def upsert_file(self, file_path: Path, content_hash: str, blocks: list[CodeBlock]) -> None:
    self.db.execute("BEGIN")
    self.db.execute("DELETE FROM code_blocks WHERE file_path = ?", (str(file_path),))
    self.db.execute(
        "INSERT INTO files (file_path, content_hash) VALUES (?, ?) "
        "ON CONFLICT(file_path) DO UPDATE SET content_hash = excluded.content_hash, "
        "last_scanned = CURRENT_TIMESTAMP",
        (str(file_path), content_hash),
    )
    self.db.executemany(
        "INSERT INTO code_blocks (file_path, hash_value, start_line, end_line, snippet) "
        "VALUES (?, ?, ?, ?, ?)",
        [(str(file_path), b.hash_value, b.start_line, b.end_line, b.snippet) for b in blocks],
    )
    self.db.commit()
```

**Freshness check** (used for on-query verification of files being matched against, not as the
primary "what changed" signal — that's the caller's diff list):

```python
def needs_rescan(self, file_path: Path, current_content_hash: str) -> bool:
    row = self.db.execute(
        "SELECT content_hash FROM files WHERE file_path = ?", (str(file_path),)
    ).fetchone()
    return row is None or row[0] != current_content_hash
```

**Runtime flow for `DRYRule` in incremental mode:**
1. Caller passes the changed file list (as CLI args, exactly as today).
2. For each file handed to `check()`: compute content hash, `upsert_file(...)` unconditionally
   (it's in the caller's diff list, so we know it needs re-indexing — no freshness check needed
   for files we were explicitly told changed).
3. `finalize()` queries the **whole persisted index** (not just this run's files) for duplicate
   hashes involving any of the just-indexed files, batched (fix the existing N+1 — one query
   listing duplicate hashes, one `IN (...)`-batched query for their blocks, not N individual
   queries; this is a good time to fix that regardless of caching).
4. Before trusting a matched-against row that belongs to a file *not* in this run's file list,
   verify freshness via `needs_rescan` against the file on disk (cheap: read + hash, no
   tokenization). If stale, either (a) skip that row for this run and log a warning, or (b)
   transparently rescan it too — recommend (b) for correctness, since a stale row could hide a
   duplicate that was actually removed, or wrongly downgrade one that's still there; this is the
   self-healing path from the original design proposal.
5. CLI flags: make `--no-cache` and `--clear-cache` do something real again (skip the persistent
   store entirely for `--no-cache`; actually delete `.thailint-cache/dry.db` for `--clear-cache`,
   which already resolves this exact path today). Repair the justfile's stale `clean-cache:`
   recipe to match.

## BDD specifications (plain pytest, Given/When/Then as arrange/act/assert — matching this repo's
established style, not pytest-bdd)

```gherkin
Feature: Persistent cross-run duplicate index survives between invocations
  As a developer running DRY as a pre-commit hook
  I want a duplicate introduced by my changed file to be caught even when the
  file it duplicates was not part of this invocation
  So that incremental linting is as correct as a full-tree scan

  Scenario: A changed file duplicates an unchanged, previously-indexed file
    Given file A and file B both contain the same 5-line block
    And both were indexed in a prior invocation
    When only file A is passed to `dry` in a new invocation (file B is not passed)
    Then a duplicate-code violation is reported for file A
    And the violation message references file B

  Scenario: Fixing a duplicate makes the violation disappear on the next run (the #35 regression)
    Given file A and file B contain the same 5-line block, indexed in a prior invocation
    When file A is edited to remove the duplicated block and re-indexed
    And file A is passed to `dry` again
    Then no duplicate-code violation is reported for file A
    And the persisted index for file A contains only its current blocks, not the removed one

  Scenario: An unrelated file's stale index entry is not trusted without verification
    Given file B was indexed with content C1 in a prior invocation
    And file B's on-disk content has since changed to C2 without B being re-indexed
    When file A (which duplicates content C1, not C2) is passed to `dry`
    Then file B is transparently rescanned before being used as a match
    And the violation against file A reflects file B's current content, not C1

  Scenario: A deleted file's stale entries do not produce phantom violations
    Given file B was indexed in a prior invocation and has since been deleted from disk
    When file A (which duplicates file B's old content) is passed to `dry`
    Then file B's entries are purged from the index during reconciliation
    And no violation is reported referencing file B

  Scenario: The persisted index survives a fresh CLI process
    Given file A and file B are indexed by invocation 1 (one process)
    When invocation 2 (a distinct process) passes only file A
    Then invocation 2 still finds the cross-file duplicate against file B
    (this is the literal regression test for the hash() process-randomization prerequisite bug)

Feature: Parallel DRY linting produces correct cross-file results
  As a developer running `thai-lint dry --parallel` on many files
  I want the same violations as a sequential run
  So that parallelism is a performance choice, not a correctness trade-off

  Scenario: Parallel run finds the same duplicates as sequential
    Given a directory containing file A and file B with a shared duplicate block
    When linted once with `--parallel` and once without
    Then both runs report the same violations
```

## Build order (TDD)

1. **PR1 (parallel fix)**: write a failing test proving `--parallel` misses a cross-file
   duplicate that sequential mode catches; fix by aggregating worker output centrally before one
   `finalize()` call; verify equivalence with sequential mode on the same fixture.
2. **PR2 (stable hash)**: write a test asserting `hash_value` for the same snippet is identical
   across two separate subprocess invocations (this test would fail today, proving the
   prerequisite bug); switch to the stable hash; re-run full DRY suite for regressions.
3. **PR3 (persistent index)**:
   a. Schema + `upsert_file`/`needs_rescan` on `DRYCache`, unit-tested directly (not through the
      whole linter) for the exact "fix then rescan" regression scenario from the BDD spec.
   b. Wire `DRYRule` to use a real on-disk store when configured, batch the N+1 violation query.
   c. Wire the "verify freshness of matched-against files, rescan if stale" path.
   d. CLI: make `--no-cache`/`--clear-cache` real; add whatever flag selects the persistent
      on-disk store vs today's ephemeral default (needs a naming decision — could be
      `storage_mode: persistent` alongside the existing `memory`/`tempfile` values, reusing the
      existing config field rather than adding a new one).
   e. Full BDD scenarios from above as the acceptance suite.
4. Re-run the qbench benchmark in incremental mode (touch ~50 files, time a re-run) as the real
   viability proof this plan promises — compare against the 143.87s full-tree baseline already
   measured.

## Documentation updates

- `docs/dry-linter.md` — document the persistent index, its location, `.gitignore` expectation,
  and the diff-scoped incremental invocation pattern (with a `just`/pre-commit example reusing
  the existing `git diff --cached --name-only` plumbing).
- `CHANGELOG.md` — this feature, plus explicit note that it supersedes/fixes #35's removed
  version with a corrected invalidation protocol (the #35 removal itself was never documented in
  CHANGELOG.md; worth closing that gap retroactively in the same entry).
- `justfile` — repair the stale `clean-cache:` recipe to match the real cache path.

## Release gates (smoke tests before calling this done)

- Full qbench full-tree run still matches the already-measured 143.87s baseline (no regression
  from the new index-write path on a cold/first run).
- A simulated "typical commit" (touch ~50 files out of the qbench tree, reusing the persisted
  index from the prior full run) completes in low single-digit seconds — this is the actual
  claim this plan needs to prove true, not just assert.
- The `#35` regression scenario (fix a duplicate, rescan, violation disappears) passes as an
  automated test, not just manual verification — this is the one thing the original
  implementation never tested.
- `thai-lint dry --parallel` produces identical violations to sequential mode on a real fixture.

## Edge cases and risks

- **StringlyTypedRule** has the same `finalize()`-based cross-file-state shape as DRY — check
  during PR1 whether it has the same `--parallel` exposure; fix with the same mechanism if so,
  or explicitly scope it out with a note why not.
- **Renames**: a git rename shows up as delete+add (or a rename with 100% similarity, depending
  on git's detection) — the reconciliation/deletion-purge path should treat a renamed-away path
  as "gone" and let the new path be indexed fresh; don't try to special-case rename detection.
- **Concurrent invocations** (two pre-commit hooks or a hook + a background CI job touching the
  same `.thailint-cache/dry.db` at once) — SQLite's own locking should handle this at the
  transaction level; worth a test but not a redesign.
- **CI cache portability**: content-hash keying (unlike the old mtime keying) makes this cache
  safe to restore via `actions/cache` from any prior run without risk of the mtime-reset problem
  that made the old design hostile to ephemeral checkouts — worth calling out in docs as a
  follow-up, not required for v1.
- **Schema migration**: `SCHEMA_VERSION` existed before but was never checked; this is the point
  to actually wire it up, so a future schema change can detect+rebuild an incompatible on-disk
  cache instead of erroring or silently misbehaving.

## Critical files

- `src/linters/dry/cache.py` — schema, upsert/freshness methods (main rewrite target)
- `src/linters/dry/linter.py` — `DRYRule.check()`/`finalize()` wiring for incremental mode
- `src/linters/dry/storage_initializer.py` — pass through real storage path/mode
- `src/linters/dry/duplicate_storage.py`, `cache_query.py` — batched query fix
- `src/linters/dry/python_analyzer.py`, `typescript_analyzer.py`, `token_hasher.py` — stable hash (PR2)
- `src/orchestrator/core.py` — `_execute_parallel_linting`/`_lint_file_worker` (PR1)
- `src/cli/linters/code_smells.py` — real `--no-cache`/`--clear-cache`, new storage-mode flag
- `justfile` — `clean-cache` recipe repair
- `.gitignore` — confirm/restore `.thailint-cache/` entry
- `docs/dry-linter.md`, `CHANGELOG.md`

## Verification

- Every PR above ships with its own failing-first test per this repo's TDD convention, plus the
  full `just lint-full` (17 gates) and full test suite (`just test`) staying green throughout —
  same discipline already applied to this session's five perf fixes.
- The two release-gate benchmarks (full-tree baseline unchanged, simulated-commit incremental
  run) are run against the real qbench checkout already used throughout this session, not a
  synthetic fixture, since that's what actually validated every prior claim in this plan.

## Next step after approval

Per this repo's roadmap convention (confirmed against the two most recent real examples,
`file-header-ticket-references` and `ai-convention-linters`, both of which used this same
single-PLAN.md-first pattern): once this plan is approved, the next artifact is
`.roadmap/planning/dry-persistent-cache/PLAN.md` (this document, filed as the actual planning
deliverable), followed — when ready to actually build — by the classic three-document roadmap
(`PROGRESS_TRACKER.md`, `PR_BREAKDOWN.md`, `AI_CONTEXT.md`) that AGENTS.md mandates for multi-PR
implementation work, generated from `.ai/templates/roadmap-*.md.template`.
