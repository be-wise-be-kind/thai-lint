# DRY Persistent Cache: Implementation Deep Dive

**Purpose**: Explains, in full technical detail, how `storage_mode: "persistent"` works
internally - the schema, the write and read paths, freshness verification, concurrency
handling, and the historical bug it was designed not to repeat.

**Scope**: The DRY linter's on-disk, cross-run duplicate index. For day-to-day usage (config
options, CLI flags, when to reach for this mode), see [DRY Linter](dry-linter.md#persistent-cross-run-cache);
this page is the "how and why," not the "how do I turn it on."

**Audience**: Contributors modifying the DRY linter's storage layer, and anyone who wants to
understand exactly what correctness and performance guarantees this feature does and doesn't
make before relying on it in a blocking pre-commit hook.

---

## The Problem This Solves

Duplicate-code detection is inherently cross-file: whether a block is a "duplicate" depends on
every other file in the project, not just the one being analyzed. Every other thai-lint
architectural linter (`nesting`, `srp`, `magic-numbers`) can look at one file in isolation and
answer its question completely. DRY cannot - which is exactly why it's the one linter in this
codebase that can't just be pointed at a diff.

Before persistent mode, every `thai-lint dry` invocation re-derived the *entire* project's
duplicate index from scratch, in memory, every single time - `storage_mode: "memory"` and
`"tempfile"` are both wiped clean at the start of each run. That's fine for a nightly CI job
that scans everything anyway. It's fatal for a blocking pre-commit hook: a commit touching 3
files would still pay the cost of analyzing every file in the repository, because there was no
way to ask "does this changed file duplicate anything in the rest of the codebase" without
re-scanning the rest of the codebase.

`storage_mode: "persistent"` breaks that link. It keeps the duplicate index on disk between
invocations, so a run can answer "does this file duplicate anything, anywhere in the project"
while only paying the analysis cost of the files it was actually given.

## History: The #35 Regression

This is not the first time this codebase has shipped a persistent DRY cache. An earlier
version was built in `.roadmap/complete/dry-linter/` (October 2025), shipped, and then removed
four months later ([#35](https://github.com/be-wise-be-kind/thai-lint/issues/35)) after it
caused **false positives that outlived the fix**: a developer would remove a duplicate, rerun
the linter, and still see the violation reported against the code that no longer existed.

Reading the actual removed code (not just the commit message) shows a precise, narrow root
cause:

- **Freshness was mtime-only.** `is_fresh()` compared `cached_mtime == current_mtime` with no
  content check at all. Any operation that touched a file's mtime without changing its content
  (a checkout, a `touch`, certain editors) would make an unchanged file look stale, and vice
  versa in some CI checkout scenarios.
- **The fatal bug**: `save()` did `DELETE FROM files WHERE file_path=?`, then inserted a fresh
  `files` row, and relied on `ON DELETE CASCADE` on the `code_blocks` foreign key to also purge
  that file's old blocks. **SQLite only enforces `ON DELETE CASCADE` when `PRAGMA
  foreign_keys=ON` is set on the connection - and it never was, anywhere in that codebase.** So
  the `files` row got replaced, but every prior `code_blocks` row for that file stayed forever,
  orphaned. Fix a duplicate, rescan, and the pre-fix block was still sitting in the table,
  still matching against whatever it used to duplicate.
- The 12-test suite covering the old cache never tested "fix a duplicate, verify the violation
  disappears on the next run" - the exact scenario that broke. Coverage would not have caught
  this even if it had been run.

None of this points at persistence itself being unsound. It's a one-line-class bug (a missing
explicit `DELETE`, papered over by an assumption about a PRAGMA that was never set) combined
with a freshness signal (mtime) that was weaker than it needed to be. The design below fixes
both, directly, and is tested against the exact regression scenario that got the original
feature pulled.

## Design Principles

Three decisions carry the whole design, and each maps directly to a piece of the #35 postmortem:

1. **Never rely on `ON DELETE CASCADE` for correctness.** `upsert_file()` always issues an
   explicit `DELETE FROM code_blocks WHERE file_path = ?` before inserting new rows - in the
   same method, every time, regardless of whether the new block list is empty. No PRAGMA has to
   be set correctly elsewhere for this to hold.
2. **Freshness is a content hash, not a timestamp.** `files.content_hash` is a hash of the
   file's actual text. A file matches its indexed state if and only if its current content
   hashes the same - no dependency on filesystem mtime semantics, checkout behavior, or clock
   skew. This also makes the cache safe to restore from CI caching (e.g. `actions/cache`)
   across a fresh checkout, which mtime-based freshness is not.
3. **Trust nothing that wasn't scanned this run.** A duplicate match against a file outside the
   current invocation's file list is verified before being reported - rescanned if its content
   changed, purged if it no longer exists. See [Freshness Verification](#freshness-verification-and-reconciliation)
   below.

## Schema

```sql
CREATE TABLE files (
    file_path TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE code_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value INTEGER NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    snippet TEXT NOT NULL
);

CREATE INDEX idx_hash_value ON code_blocks(hash_value);
CREATE INDEX idx_file_path ON code_blocks(file_path);

CREATE TABLE schema_meta (version INTEGER NOT NULL);
```

Notably absent: any `FOREIGN KEY ... ON DELETE CASCADE` between `code_blocks` and `files`. That
relationship existed in the removed version and was the load-bearing (and silently unenforced)
assumption behind #35. This schema doesn't have it, so there's nothing to silently fail to
enforce - `upsert_file()` and `purge_file()` manage both tables explicitly, every time.

Duplicate-*constant* detection (a separate, opt-in feature: same name repeated with different
values across files) has no presence in this schema at all. It runs on a wholly separate,
in-memory, non-SQLite path (`DRYRule._constants` → `find_constant_groups()`), rebuilt from
scratch every run regardless of `storage_mode`. Persistence is v1-scoped to duplicate *code*
detection only.

Code: [`src/linters/dry/cache.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/cache.py)

## The Write Path: `upsert_file`

```python
def upsert_file(self, file_path: Path, content_hash: str, blocks: list[CodeBlock]) -> None:
    self.db.execute("DELETE FROM code_blocks WHERE file_path = ?", (str(file_path),))
    self.db.execute(
        """INSERT INTO files (file_path, content_hash, last_scanned)
           VALUES (?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(file_path) DO UPDATE SET
               content_hash = excluded.content_hash,
               last_scanned = excluded.last_scanned""",
        (str(file_path), content_hash),
    )
    if blocks:
        self.db.executemany(
            """INSERT INTO code_blocks (file_path, hash_value, start_line, end_line, snippet)
               VALUES (?, ?, ?, ?, ?)""",
            [(str(file_path), b.hash_value, b.start_line, b.end_line, b.snippet) for b in blocks],
        )
    self.db.commit()
```

Two properties matter here:

- **It runs unconditionally, even when `blocks` is empty.** If a file is edited to remove its
  last duplicated block, the run that scans it must still delete the now-stale rows - skipping
  the call when there's "nothing to add" would silently resurrect the exact #35 failure mode for
  the single-block-removed case.
- **`content_hash` is recorded even when there are zero blocks.** This lets `needs_rescan()`
  recognize the file as already up to date on a later run (it has no duplicates *and* hasn't
  changed), and lets a later edit that reintroduces a duplicate be detected as a content-hash
  change rather than silently missed.

`DRYRule._analyze_and_store()` is the only caller, and it calls `upsert_file` for every file
that reaches `check()` - which is why `self._processed_files` (a `set[str]` of everything
upserted this run) exists: it's the input to freshness verification below.

## The Read Path: Cross-Run Matching Is Free

This is the part that requires no special logic at all, which is the point. `finalize()`
generates violations by querying `duplicate_hashes` (hash values appearing 2+ times across
*all* rows currently in `code_blocks`) and then `get_blocks_for_hashes()` for the matching
blocks - both queries scan the whole table, unconditionally. Because persistent mode doesn't
wipe the table between runs, "the whole table" already includes every file indexed by every
prior invocation, not just this run's files. A file passed to `check()` and a file sitting
untouched in the index from three runs ago are indistinguishable to this query - which is
exactly the property that makes diff-scoped invocation ("just lint the changed files") produce
a complete answer instead of a partial one.

```python
def find_duplicates_by_hashes(self, hash_values: list[int]) -> dict[int, list[CodeBlock]]:
    rows = self._query_service.find_blocks_by_hashes(self.db, hash_values)
    ...
```

This is also a batched query - one `SELECT ... WHERE hash_value IN (...)` for every duplicate
hash group in a single round trip, rather than one query per group (`ViolationGenerator`
previously called `get_blocks_for_hash()` once per entry in `duplicate_hashes`, an N+1 pattern
that dominated query time on large duplicate sets independent of persistence).

**Consequence worth knowing**: because both sides of a match are always reported, a diff-scoped
run over 3 changed files can emit violations attributed to files *outside* that list - files
the persisted index already knew duplicated something in one of the 3. This is intentional and
matches what a full-tree scan would have reported; it is not a bug if a run's output mentions a
path you didn't pass in.

## Freshness Verification and Reconciliation

The one thing the read path above doesn't handle: a file sitting in the index from a prior run
might have changed on disk since then, or been deleted, without this run ever touching it
directly. Before `finalize()` trusts a match against such a file, `reconcile_stale_matches()`
checks it:

```python
def reconcile_stale_matches(storage, file_analyzer, config, processed_files):
    for file_path in _external_file_paths(storage, processed_files):
        _reconcile_file(file_path, storage, file_analyzer, config)

def _external_file_paths(storage, processed_files):
    # every file_path appearing in a duplicate-hash group, minus this run's processed_files
    ...

def _reconcile_file(file_path, storage, file_analyzer, config):
    content = _read_file(file_path)
    if content is None:
        storage.purge_file(file_path)          # deleted since indexing
        return
    content_hash = compute_content_hash(content)
    if not storage.needs_rescan(file_path, content_hash):
        return                                  # unchanged, trust it
    blocks = file_analyzer.analyze(file_path, content, detect_language(file_path), config)
    storage.upsert_file(file_path, content_hash, blocks)  # changed - rescan and re-index
```

Three outcomes, decided per externally-matched file:

| File state | Action |
|---|---|
| Content hash unchanged | Trusted as-is, no work done |
| Content hash changed | Rescanned and re-upserted before violations are built |
| No longer exists on disk | Purged from the index entirely |

This only runs when `config.storage_mode == "persistent"` (`DRYRule._reconcile_stale_matches_if_persistent`).
Ephemeral modes skip it unconditionally - every row in an ephemeral table was written by *this
run*, so nothing external to verify. This is also why the ephemeral path pays none of this
cost: reconciliation's overhead scales with the number of *distinct files* implicated in
duplicate-hash groups, not with the number of files passed to the run.

Code: [`src/linters/dry/stale_match_reconciler.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/stale_match_reconciler.py)

## Storage Modes and Path Resolution

`initialize_storage(config, project_root)` resolves the on-disk path a `DRYCache` connects to:

```python
def _resolve_db_path(config, project_root):
    if config.shared_db_path:
        return Path(config.shared_db_path)           # --parallel override, always wins
    if config.storage_mode == "persistent":
        root = project_root or Path.cwd()
        return root / ".thailint-cache" / "dry.db"    # stable, project-relative default
    return None                                        # memory / random tempfile
```

`project_root` here is `DRYRule._project_root`, resolved once (on the first file processed) from
`context.metadata["_project_root"]` - a value the orchestrator sets on every `FileLintContext`
it constructs (`Orchestrator.lint_file`). This matters more than it looks: `_project_root`
being wrong doesn't just misplace a cosmetic value, it determines the entire on-disk location
of the persistent index. A real bug of exactly this shape (`_get_project_root` reading
`context.metadata["project_root"]` - missing the orchestrator's leading underscore, silently
falling back to `Path(file_path).parent`) was found while benchmarking this feature: it was
invisible under ephemeral storage (nothing reads `_project_root` there except ignore-pattern
resolution) and would have silently scattered `.thailint-cache/` directories throughout a
project's subdirectories - one per distinct "first file processed" - instead of one at the
project root. Fixed by reading the correct key; regression-tested with a fixture where the
scanned file is nested away from the project root, which is precisely the condition that made
the bug invisible in every prior test (all of which conveniently put files directly in
`tmp_path`).

`storage_mode: "tempfile"` and `"persistent"` share the same connection code
(`DRYCache._connect_on_disk`) - the only structural difference is *who supplies the path and
who's responsible for its lifetime*. `"tempfile"` without an explicit `db_path` gets a random,
auto-deleting file; both `"tempfile"` *with* an explicit path (used internally by `--parallel`,
below) and `"persistent"` connect to a caller-specified, non-deleted file.

## Concurrency: WAL Mode and `synchronous=NORMAL`

Every on-disk connection - `"tempfile"` with an explicit path, and `"persistent"` - sets two
pragmas:

```python
db.execute("PRAGMA journal_mode=WAL")
db.execute("PRAGMA synchronous=NORMAL")
```

**WAL** lets multiple connections read/write the same file with far less lock contention than
SQLite's default rollback journal - required for `--parallel` mode, where several worker
processes and the main process all connect to the same shared file for one run, and useful in
general for a file that might get reopened by an unrelated, later CLI invocation while something
else briefly holds it.

**`synchronous=NORMAL`** (SQLite's default under WAL is safe, but not this permissive) was added
after a very concrete measurement: a cold, first-time index build over a real ~2,981-file
Python codebase, benchmarked *without* this pragma, took on the order of tens of minutes.
`upsert_file()` commits once per file, and the default synchronous setting fsyncs on every
commit - for a large tree, that's thousands of individual fsyncs, and fsync latency (tens to
low-hundreds of milliseconds, depending on the underlying storage) dominates everything else
combined. `NORMAL` defers the fsync to WAL checkpoint boundaries instead of every commit; WAL's
own crash-recovery design (the WAL file itself is replayed on reopen after an unclean shutdown)
makes this safe - the durability window that's traded away is "the last few commits before an
OS crash or power loss," not general correctness. With the pragma in place, the same
~2,981-file cold build measured at **136-152 seconds** - in line with a full ephemeral scan of
the same tree, rather than an order of magnitude slower.

## Cross-Process Correctness: Stable Hashing

`hash_value` in `code_blocks` has to mean the same thing across every process that ever writes
or reads it - which ruled out something easy to miss: **Python's built-in `hash()` salts string
hashing with a per-process random seed (`PYTHONHASHSEED`) by default.** The same code snippet
would hash differently in every new process. This has zero effect on a single ephemeral run
(one process, one hash seed, entirely self-consistent), which is exactly why it went unnoticed
for as long as DRY was ephemeral-only - and would have been silently fatal for persistence,
where the whole point is that a hash written by one process's run must match what a different
process's run queries for later.

```python
def stable_hash(snippet: str) -> int:
    digest = hashlib.blake2b(snippet.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=True)
```

`blake2b` has no such salt; the same snippet hashes identically regardless of process, machine,
or run. This replaced `hash(snippet)` at all three call sites that hash code blocks
(`token_hasher.rolling_hash`, and the duplicated inline logic in `python_analyzer.py` and
`typescript_analyzer.py`), verified by a regression test that spawns independent
`python -c '...'` subprocesses (not forked children, which inherit the parent's seed and would
mask the bug) and asserts they hash the same fixture snippet identically.

## `--parallel` Mode

DRY's `finalize()` needs to see every file's `check()` output before it can generate a single
violation - but `Orchestrator.lint_files_parallel` dispatches each file to an isolated worker
process, each running its own fresh `DRYRule` instance. Without intervention, every worker's
`DRYRule` collects blocks into its own private, in-memory store that vanishes when the worker
exits; the main process's `DRYRule.finalize()` never saw a single `check()` call, so
`self._storage` stays `None` and `finalize()` returns `[]` unconditionally. `--parallel` reused
exactly the on-disk-store infrastructure this page describes, via two `BaseLintRule` hooks:

```python
def get_parallel_shared_config(self, shared_dir: Path) -> dict[str, Any] | None:
    db_path = shared_dir / "dry_parallel.db"
    DRYCache(storage_mode="tempfile", db_path=db_path).close()  # pre-create; see note below
    return {"dry": {"storage_mode": "tempfile", "shared_db_path": str(db_path)}}

def finalize_after_parallel(self, raw_config: dict[str, Any]) -> list[Violation]:
    self._config = self._config or DRYConfig.from_dict(raw_config.get("dry", {}))
    self._ensure_storage_initialized(self._config)
    return self.finalize()
```

The orchestrator calls `get_parallel_shared_config(shared_dir)` on every registered rule before
dispatching work, merges any non-`None` result into the config every worker process receives
(`_merge_config_override`, `Orchestrator._build_parallel_worker_config`), and after collection
calls `finalize_after_parallel(worker_config)` instead of plain `finalize()`
(`Orchestrator._finalize_rules_after_parallel`). Concretely for DRY: every worker's config gets
`storage_mode: "tempfile"` and an explicit `shared_db_path` pointing at one file in a
`shared_dir` created (and cleaned up) for the duration of that one run, so all workers - and
the main process's own `finalize_after_parallel` - connect to the same on-disk store. This is
**not** the persistent cache (a fresh `shared_dir` is used per run and discarded afterward); it
reuses the *mechanism* (a real on-disk SQLite file instead of `:memory:`) to solve a
structurally identical problem: cross-process state that must outlive the process that wrote
it.

The pre-create step in `get_parallel_shared_config` exists because of a second, independent
finding from the same benchmarking pass: multiple worker processes racing to be the *first*
connection to a brand-new file - each trying `CREATE TABLE IF NOT EXISTS` and
`PRAGMA journal_mode=WAL` before the file and its schema exist yet - could raise `"database is
locked"` even under a 30-second busy timeout, because converting an empty/nonexistent database
to WAL is not itself a lock-wait-and-retry operation in the way ordinary writes are. Creating
the file, schema, and WAL mode once, synchronously, from the single main process before any
worker connects removes the race entirely.

`StringlyTypedRule` (the only other rule in the codebase with a `finalize()` that needs
cross-file state) has the exact same shape of bug and the exact same fix, for the same reason.

## Schema Versioning and Self-Healing

```python
def _ensure_schema(self) -> None:
    self.db.execute("CREATE TABLE IF NOT EXISTS schema_meta (version INTEGER NOT NULL)")
    row = self.db.execute("SELECT version FROM schema_meta").fetchone()
    if row is not None and row[0] != self.SCHEMA_VERSION:
        self._drop_app_tables()
    self._create_tables()
    self.db.execute("DELETE FROM schema_meta")
    self.db.execute("INSERT INTO schema_meta (version) VALUES (?)", (self.SCHEMA_VERSION,))
    self.db.commit()
```

Every connection checks the on-disk file's recorded schema version against
`DRYCache.SCHEMA_VERSION` (currently `2` - version `1` was the pre-persistence, mtime-keyed
shape). A mismatch drops and recreates `files` and `code_blocks` from scratch rather than
erroring or attempting a migration. This is intentionally simple: a schema-version bump is rare,
the cache is disposable derived data (never a source of truth - the worst outcome of losing it
is one slower "cold" run), and a full rebuild is trivially correct in a way a hand-written
migration path is not.

## CLI Integration

```python
def _apply_dry_config_override(orchestrator, min_lines, no_cache, verbose):
    ...
    if no_cache:
        set_config_value(dry_config, "storage_mode", "memory", verbose)
```

`--no-cache` forces `storage_mode: "memory"` for that one invocation, overriding whatever the
config file says - the persistent store isn't just "not written to," it's not connected to at
all, so a `--no-cache` run can't see cross-run matches even if one happens to exist on disk.

```python
def _clear_dry_cache(orchestrator, verbose):
    cache_path = _resolve_dry_cache_path(orchestrator)
    for path in (cache_path, cache_path.with_name(cache_path.name + "-wal"),
                 cache_path.with_name(cache_path.name + "-shm")):
        if path.exists():
            path.unlink()
```

`--clear-cache` deletes the database file *and* its WAL/SHM sidecar files before the run
proceeds - leaving a stale `-wal` file behind after deleting only the main file can confuse a
subsequent connection, so all three are removed together.

## Rebuilding the Index

There's no separate "rebuild" subcommand, and none is needed: `thai-lint dry --clear-cache`
with no path arguments does exactly that. `dry`'s path argument defaults to `.` and scans
recursively by default, so `--clear-cache` (delete the existing file) followed by a full
project walk (rebuild it from nothing) *is* a complete rebuild, expressed as the composition of
two things the CLI already does. There's nothing this "loses" relative to a hypothetical
dedicated command - a full walk with an empty starting index produces byte-for-byte the same
`code_blocks`/`files` contents as any other path to a fresh index, since `upsert_file` doesn't
care whether a row already existed.

```bash
# Full rebuild: delete the existing index, then re-derive it from every file in the project
thai-lint dry --clear-cache --config .thailint.yaml .
```

## Real-World Validation

Benchmarked against a real ~2,981-file Python monorepo (not a synthetic fixture), using a
config with only `enabled: true` and `storage_mode: "persistent"` set (defaults otherwise):

| Scenario | File count | Time | Notes |
|---|---|---|---|
| Cold index build (first run ever) | 2,981 | 136-152s | One-time cost; comparable to an ephemeral full-tree scan of the same tree |
| Diff-scoped run, real commit range | 13 (via `git diff --name-only HEAD~3 HEAD`) | ~5.5-5.9s | Correctly found matches against dozens of unchanged files not in the 13-file list |
| Diff-scoped run with a deliberately injected cross-file duplicate | 13 | 5.55s | See below - the deterministic proof, not just "these numbers look plausible" |

The middle row is a real diff from real commit history, not a constructed fixture - correctness
was checked by inspecting the actual violation output for matches against files genuinely
absent from the 13-file list (e.g. a duplicated helper in `service/serv_samples.py` correctly
reported against `service/serv_accessioning_type.py`, which was nowhere in the invocation).

The last row is the unambiguous version of that same claim: a unique, synthetic 4-line block was
written to a new file and indexed as if it already existed at `HEAD`; the identical block was
then appended to one of the 13 "changed" files (which was *not* re-indexed as unchanged - it's
genuinely part of the changed set); a diff-scoped run over just the 13 files correctly reported
the new duplicate, cross-referencing the untouched marker file by name and line number, in 5.55
seconds. `--no-cache` against the same single file, by contrast, correctly failed to find the
match (no persisted context to see), and `--clear-cache` followed by a rescan correctly left no
trace of the marker file in the index - both confirming the CLI flags do what the section above
says they do, not just that the default path works.

## Known Limitations and Edge Cases

- **Renames are delete+add, not detected as a rename.** A git rename shows up as the old path
  disappearing (purged, once something matches against it and finds it missing) and the new
  path being indexed fresh on its next scan. There's no special-cased rename detection, and none
  is planned - treating a rename as "gone" + "new" is correct, just not optimally efficient.
- **Concurrent invocations** against the same `.thailint-cache/dry.db` (two pre-commit hooks, or
  a hook racing a background CI job) are handled by WAL's own locking semantics and the 30-second
  `busy_timeout` on shared connections - contention causes waiting, not corruption, but hasn't
  been stress-tested under sustained concurrent write load.
- **CI cache portability**: because freshness is content-hash keyed rather than mtime-keyed, the
  cache is safe to restore via `actions/cache` (or equivalent) from a prior CI run onto a fresh
  checkout - a fresh checkout resets every file's mtime but not its content, so nothing looks
  spuriously stale the way the old mtime-based design would have.
- **Duplicate-constant detection is not persisted.** It's a separate, always-ephemeral,
  in-memory path; `storage_mode: "persistent"` has no effect on it.
- **A file matched against but never scanned by *any* run stays in the index until something
  matches against it.** Reconciliation (rescan-or-purge) only triggers for files that appear in
  a *current* duplicate-hash group. A file that's deleted and whose blocks no longer match
  anything else won't be actively purged - it simply stops appearing in any output, which is
  behaviorally correct (no phantom violation is ever produced), just not swept from the table
  until something else forces the query to notice it's gone. A full `--clear-cache` rebuild is
  the way to reclaim that space if it matters.

## Where the Code Lives

| File | Responsibility |
|---|---|
| [`src/linters/dry/cache.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/cache.py) | `DRYCache`: schema, connection setup, `upsert_file`/`needs_rescan`/`purge_file`, batched hash queries |
| [`src/linters/dry/cache_query.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/cache_query.py) | Raw SQL for duplicate-hash and batched block lookups |
| [`src/linters/dry/duplicate_storage.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/duplicate_storage.py) | Thin delegating wrapper `DRYRule` actually holds a reference to |
| [`src/linters/dry/storage_initializer.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/storage_initializer.py) | `initialize_storage()`: resolves the on-disk path, constructs the right `DRYCache` |
| [`src/linters/dry/stale_match_reconciler.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/stale_match_reconciler.py) | `reconcile_stale_matches()`: the rescan-or-purge freshness pass |
| [`src/linters/dry/content_hash.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/content_hash.py) | Whole-file content hashing for freshness (distinct from per-block hashing) |
| [`src/linters/dry/token_hasher.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/token_hasher.py) | `stable_hash()`: the process-stable per-block hash |
| [`src/linters/dry/linter.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/linters/dry/linter.py) | `DRYRule`: wires everything above into `check()`/`finalize()`, plus the `--parallel` hooks |
| [`src/core/base.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/core/base.py) | `get_parallel_shared_config`/`finalize_after_parallel` hook definitions on `BaseLintRule` |
| [`src/orchestrator/core.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/orchestrator/core.py) | Dispatches the `--parallel` hooks above; sets `_project_root` in file context metadata |
| [`src/cli/linters/code_smells.py`](https://github.com/be-wise-be-kind/thai-lint/blob/main/src/cli/linters/code_smells.py) | `--no-cache`/`--clear-cache` CLI flag implementation |

## Related

- [DRY Linter](dry-linter.md) - user-facing configuration and CLI usage
- [CHANGELOG](https://github.com/be-wise-be-kind/thai-lint/blob/main/CHANGELOG.md) - the PRs that introduced this (search for "persistent cross-run cache")
- Issue [#35](https://github.com/be-wise-be-kind/thai-lint/issues/35) - the original regression this design fixes
