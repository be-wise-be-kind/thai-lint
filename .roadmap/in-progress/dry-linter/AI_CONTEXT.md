# DRY Linter - AI Context & Architecture Document

**Purpose**: Comprehensive architectural overview and design rationale for the DRY Linter feature

**Scope**: Technical architecture, algorithm design, integration patterns, and implementation decisions

**Overview**: Provides deep technical context for AI agents and developers implementing the DRY Linter.
    Explains the reasoning behind key architectural decisions, algorithm choices, storage strategies,
    and integration patterns. Essential for understanding the "why" behind the implementation approach
    and making informed decisions during development. Covers token-based hash detection, SQLite caching,
    single-pass processing, and scalability considerations for enterprise codebases.

**Dependencies**: Nesting and SRP linter patterns, Python stdlib (sqlite3), core orchestrator framework

**Related**: PROGRESS_TRACKER.md for status, PR_BREAKDOWN.md for implementation steps

---

## Feature Overview

### What is the DRY Linter?

The DRY (Don't Repeat Yourself) Linter detects duplicate code across an entire project, helping teams:
- **Identify code duplication** (3+ lines minimum)
- **Reduce technical debt** through systematic refactoring
- **Improve maintainability** by eliminating redundant code
- **Scale to large projects** (10K+ files) with intelligent caching

### Target Use Cases

1. **CI/CD Integration**: Fast incremental scans on every commit
2. **Pre-release audits**: Comprehensive duplicate detection before major releases
3. **Technical debt tracking**: Monitor duplication metrics over time
4. **Refactoring guidance**: Identify highest-impact refactoring opportunities

### Key Requirements

**Functional**:
- Detect exact duplicates (3+ lines)
- Work across entire project (not just single files)
- Support Python, TypeScript, JavaScript
- Provide helpful violation messages with all duplicate locations

**Non-Functional**:
- Scale to 10,000+ files (8 min first run, <30s cached)
- Memory efficient (<500MB for 10K files)
- CI/CD friendly (JSON output, proper exit codes)
- Opt-in performance (excluded from `lint-full`)

---

## Architectural Decisions

### Decision 1: Token-Based vs AST-Based Detection

**Options Considered**:

**A) Token-Based (Chosen)**:
- Strip comments, normalize whitespace
- Hash raw token sequences
- Detect exact and near-exact duplicates

**B) AST-Based**:
- Parse to Abstract Syntax Tree
- Normalize variable names
- Detect structural duplicates

**C) Semantic (ML-based)**:
- Use embeddings or similarity metrics
- Detect functionally similar code
- Highest false positive rate

**Decision: Token-Based (Option A)**

**Rationale**:
1. **Simplicity**: Token-based is straightforward to implement and test
2. **Language Agnostic**: Works for Python, TypeScript, JavaScript without language-specific AST parsers
3. **Performance**: Fast tokenization (~10K lines/second)
4. **Sufficient Coverage**: Catches ~80% of real duplicates
5. **Low False Positives**: Only reports near-identical code
6. **Extensibility**: Can add AST-based detection later as enhancement

**Tradeoffs**:
- ❌ Misses duplicates with different variable names
- ❌ Doesn't detect structural similarity
- ✅ Fast and reliable
- ✅ Easy to understand and debug

---

### Decision 2: SQLite Cache vs In-Memory vs No Cache

**Options Considered**:

**A) In-Memory Only**:
- Hash table rebuilt on every run
- No persistence between runs
- Simple, no cache management

**B) Filesystem Cache (JSON/Pickle)**:
- Serialize hash table to disk
- Complex cache invalidation
- Human-readable (JSON)

**C) SQLite Cache (Chosen)**:
- Structured database with indexes
- mtime-based invalidation
- Fast queries, efficient storage

**Decision: SQLite Cache (Option C)**

**Rationale**:
1. **Scalability**: Required for 10K+ file projects
2. **Performance**: 10-50x speedup for incremental scans
3. **Standard Library**: sqlite3 ships with Python (no dependencies)
4. **Reliability**: ACID transactions, proven database engine
5. **Efficiency**: Indexed queries, minimal memory footprint
6. **CI/CD Friendly**: Fast cached runs make DRY practical in pipelines

**CRITICAL DESIGN POINT**: The SQLite database is **project-wide**, not per-file:
- Contains code blocks from ALL files in the project
- Acts as both cache (avoid re-hashing) AND hash table (query duplicates)
- Persistent across multiple lint runs
- Single database per project: `.thailint-cache/dry.db`

**Performance Impact**:
```
10K files, typical commit (50 changed files):
- No cache: ~8 minutes (hash all 10K files)
- With cache: ~15 seconds (hash 50, query 9950 from DB)
- 32x speedup!
```

**Implementation Details**:
- **Schema**: Two tables (files, code_blocks) with hash indexes
- **Scope**: Project-wide (not per-file) - all code blocks stored together
- **Invalidation**: Compare file mtime (modification time)
- **Storage**: `.thailint-cache/dry.db` (gitignored)
- **Cleanup**: Automatic removal of stale entries
- **Querying**: `SELECT * FROM code_blocks WHERE hash_value = ?` finds duplicates

---

### Decision 3: Single-Pass vs Two-Pass Algorithm

**Options Considered**:

**A) Two-Pass**:
- Pass 1: Collect all files, buffer contents
- Pass 2: Hash all files, build hash table, find duplicates

**B) Single-Pass (Chosen)**:
- For each file: hash immediately, add to hash table
- Find duplicates incrementally as files are processed

**Decision: Single-Pass (Option B)**

**Rationale**:
1. **Memory Efficient**: Don't buffer all file contents
2. **Streaming Friendly**: Can process files as they arrive
3. **Simpler State**: No "collection phase" vs "processing phase"
4. **Cache Integration**: Natural fit with cache-load-or-hash pattern

**Algorithm**:
```
For each file (orchestrator calls check() per file):
  1. Check cache: is file unchanged? (compare mtime)
     YES → blocks already in DB (skip to step 3)
     NO  → hash file + insert blocks into DB
  2. Query DB for duplicates for THIS file's blocks
     - For each block: SELECT * FROM code_blocks WHERE hash_value = ?
     - If 2+ results: duplicate found
  3. Build and return violations for THIS file only
```

**Key Insight**: SQLite DB **IS** the hash table
- No separate in-memory hash table needed
- Blocks inserted into DB immediately (become queryable)
- Each file queries DB for its duplicates
- DB persists across files (project-wide context)
- Report duplicates **per-file** (not all at once)
- Each file reports its own violations
- Violations reference OTHER file locations
- Deduplication happens naturally (same violation from each file)

---

### Decision 4: Multi-File Context Integration

**Challenge**: Existing linters (nesting, SRP) analyze files independently via `Orchestrator.lint_file()`. DRY needs ALL files to find cross-project duplicates.

**Options Considered**:

**A) Modify Orchestrator**:
- Add multi-file context support to BaseLintContext
- Pass all files to DRYRule at once
- Requires framework changes

**B) File Buffering in Rule (Chosen)**:
- DRYRule maintains global hash_table across check() calls
- Each check() call adds file to hash_table
- Report violations incrementally

**C) Post-Processing Hook**:
- Orchestrator collects all violations
- DRY rule runs once after all files processed
- Complex integration

**Decision: File Buffering (Option B)**

**Rationale**:
1. **No Framework Changes**: Works with existing orchestrator
2. **Simple Integration**: Just maintain state in rule instance
3. **Cache Friendly**: Can load/save per file
4. **Proven Pattern**: Works with existing architecture

**Implementation**:
```python
class DRYRule(BaseLintRule):
    def __init__(self):
        # Global state shared across ALL check() calls
        self._cache: DRYCache | None = None  # SQLite cache IS the hash table
        self._initialized: bool = False

    def check(self, context: BaseLintContext) -> list[Violation]:
        # Lazy initialization on first check() call
        if not self._initialized:
            self._init_cache(context.project_root)
            self._initialized = True

        # Single-pass streaming algorithm:
        # 1. Analyze THIS file (or load from cache if fresh)
        blocks = self._analyze_or_load(context.file_path)

        # 2. For each block, query cache (DB) for duplicates
        violations = []
        for block in blocks:
            duplicates = self._cache.find_duplicates_by_hash(block.hash_value)
            if len(duplicates) >= 2:  # Including current block
                violations.append(self._build_violation(block, duplicates))

        # 3. Insert blocks into cache (DB) for future queries
        self._cache.add_blocks(blocks)

        return violations
```

**Key Design Points**:
1. **Cache IS Hash Table**: SQLite database serves as both cache AND hash table
2. **Stateful Rule**: DRYRule instance persists across all check() calls in a lint run
3. **Lazy Init**: Cache initialized once on first file, reused for all subsequent files
4. **Query-Per-Block**: Each block queries DB for existing duplicates immediately
5. **Streaming**: No need to buffer all files - process one at a time

---

### Decision 5: Excluded from lint-full

**Decision**: DRY linter is **opt-in** (not in `make lint-full`)

**Rationale**:
1. **Performance**: ~8 min for large projects (too slow for fast iteration)
2. **Use Case**: DRY is for audits, not every commit
3. **CI/CD**: Run on schedule (nightly) or pre-release, not every push
4. **Developer Experience**: Don't slow down development flow

**Configuration**:
```yaml
dry:
  enabled: false  # Must be explicitly enabled
```

**Makefile Targets**:
```makefile
lint-full: lint lint-complexity lint-security  # Fast linters only
lint-dry: # Separate target for DRY
lint-all: lint-full lint-dry  # Everything including slow linters
```

---

## Algorithm Design

### Token-Based Rolling Hash (Rabin-Karp)

**Core Idea**: Slide a fixed-size window over code, hash each window, find collisions.

**Steps**:

1. **Tokenization**:
   ```python
   lines = []
   for line in code.split('\n'):
       line = strip_comments(line)  # Remove # and //
       line = normalize_whitespace(line)  # Collapse spaces
       if line:  # Skip empty lines
           lines.append(line)
   ```

2. **Rolling Hash**:
   ```python
   window_size = min_duplicate_lines  # Default: 3
   for i in range(len(lines) - window_size + 1):
       window = lines[i:i+window_size]
       snippet = '\n'.join(window)
       hash_val = hash(snippet)  # Python's built-in hash
       store(hash_val, file, start_line, end_line, snippet)
   ```

3. **Duplicate Detection**:
   ```python
   hash_table: dict[int, list[CodeBlock]]
   for hash_val, blocks in hash_table.items():
       if len(blocks) >= 2:  # 2+ occurrences
           report_duplicate(blocks)
   ```

**Complexity**:
- Tokenization: O(n) where n = lines of code
- Rolling hash: O(n) where n = lines of code
- Lookup: O(1) hash table access
- **Total: O(n) per file**

**Example**:

**Input Code**:
```python
def process_items(items):
    for item in items:        # Line 2
        if item.is_valid():   # Line 3
            item.save()       # Line 4
    return True
```

**After Tokenization**:
```
Line 1: "def process_items(items):"
Line 2: "for item in items:"
Line 3: "if item.is_valid():"
Line 4: "item.save()"
Line 5: "return True"
```

**Rolling Hash Windows** (window_size=3):
```
Window 1 (lines 1-3): hash("def process_items...\nfor item...\nif item...")
Window 2 (lines 2-4): hash("for item...\nif item...\nitem.save()")  ← Match!
Window 3 (lines 3-5): hash("if item...\nitem.save()\nreturn True")
```

If another file has the same Window 2, it's a duplicate!

---

## Cache Architecture

### SQLite Schema

**Files Table** (metadata):
```sql
CREATE TABLE files (
    file_path TEXT PRIMARY KEY,
    mtime REAL NOT NULL,           -- Modification time (for invalidation)
    hash_count INTEGER,            -- Number of code blocks
    last_scanned TIMESTAMP         -- Last scan time
);
```

**Code Blocks Table** (hashes):
```sql
CREATE TABLE code_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value INTEGER NOT NULL,   -- Hash of code block
    start_line INTEGER NOT NULL,   -- Start line number
    end_line INTEGER NOT NULL,     -- End line number
    snippet TEXT NOT NULL,         -- Actual code (for reporting)
    FOREIGN KEY (file_path) REFERENCES files(file_path)
);
```

**Critical Indexes**:
```sql
-- Fast lookup by hash (most common query)
CREATE INDEX idx_hash_value ON code_blocks(hash_value);

-- Fast lookup by file (for cache loading)
CREATE INDEX idx_file_path ON code_blocks(file_path);
```

### Cache Operations

**IMPORTANT**: The SQLite database serves dual purpose:
1. **Cache**: Avoid re-analyzing unchanged files (mtime-based)
2. **Hash Table**: Query for duplicates across entire project

**1. File Already in Cache (Unchanged)**:
```python
def _analyze_or_load(file_path: Path):
    mtime = file_path.stat().st_mtime

    # Check if blocks already in DB
    if cache.is_fresh(file_path, mtime):
        # Blocks already in DB, nothing to do
        # (They're queryable via find_duplicates_by_hash)
        return []  # No new blocks to add

    # File changed or new → analyze it
    blocks = analyzer.analyze(file_path)
    return blocks
```

**2. New or Modified File**:
```python
def _analyze_or_load(file_path: Path):
    mtime = file_path.stat().st_mtime

    # File not in cache or mtime changed
    if not cache.is_fresh(file_path, mtime):
        # Analyze file to generate blocks
        blocks = analyzer.analyze(file_path)

        # Insert blocks into DB immediately
        # (Makes them queryable for subsequent files)
        cache.add_blocks(blocks, mtime)

        return blocks
```

**3. Querying for Duplicates**:
```python
def find_duplicates_for_file(file_path: Path):
    violations = []

    # Get all blocks for this file from DB
    file_blocks = cache.get_blocks_for_file(file_path)

    # For each block, query DB for duplicates
    for block in file_blocks:
        all_blocks = cache.find_duplicates_by_hash(block.hash_value)

        # If 2+ blocks with same hash → duplicate!
        if len(all_blocks) >= 2:
            other_blocks = [b for b in all_blocks if b.file_path != file_path]
            violations.append(build_violation(block, other_blocks))

    return violations
```

**4. Cache Invalidation (Automatic)**:
```python
# Automatic via mtime comparison
mtime_cached = 1728380400.123
mtime_current = 1728380500.456  # File was modified

if mtime_cached != mtime_current:
    # Cache is stale → delete old blocks and rehash
```

**4. Cache Cleanup (Remove Stale Entries)**:
```python
# Remove entries older than 30 days
cache.cleanup_stale(max_age_days=30)

# Vacuum to reclaim disk space
db.execute("VACUUM")
```

### Cache Performance Model

**Scenario**: 10,000 files, 50 changed in commit

**Without Cache**:
- Hash 10,000 files: 10,000 × 0.05s = 500s (~8 minutes)

**With Cache**:
- Load 9,950 cached: 9,950 × 0.001s = 10s
- Hash 50 changed: 50 × 0.05s = 2.5s
- Total: ~12.5 seconds
- **Speedup: 40x**

**Storage**:
- 10K files × 500 blocks/file × 200 bytes/block = ~1GB worst case
- Typical: 10K files × 100 blocks × 200 bytes = ~200MB
- SQLite file size: ~100-300MB

---

## Integration Patterns

### Pattern 1: Single-Pass with Global State

**Challenge**: `BaseLintRule.check()` called per-file, but DRY needs all files.

**Solution**: Maintain global hash table in rule instance:

```python
class DRYRule(BaseLintRule):
    def __init__(self):
        # Shared across ALL check() calls
        self._hash_table: dict = defaultdict(list)

    def check(self, context: BaseLintContext):
        # Add to global state
        self._add_to_hash_table(context.file_path, context.file_content)

        # Report violations for THIS file
        return self._find_duplicates_for_file(context.file_path)
```

**Key Insight**: Each file contributes to global hash table, then queries it for its own duplicates.

---

### Pattern 2: Per-File Violation Reporting

**Challenge**: If file A and file B both have the same duplicate, should we report 1 or 2 violations?

**Solution**: Report 2 violations (one per file), each referencing the other.

**Example**:
```
file1.py:10 - Duplicate code (3 lines, 2 occurrences). Also found in: file2.py:15
file2.py:15 - Duplicate code (3 lines, 2 occurrences). Also found in: file1.py:10
```

**Rationale**:
1. **User Experience**: Developer sees violation in their file
2. **CI/CD**: Violation appears in file-specific reports
3. **Filtering**: Can filter violations by file path
4. **Consistency**: Matches nesting/SRP pattern (per-file reporting)

---

### Pattern 3: Cache-Aware Hash Loading

**Challenge**: Don't rehash unchanged files, but need them in hash table.

**Solution**: Load cached blocks directly into memory:

```python
def _hash_file_smart(file_path, content):
    if cache.is_fresh(file_path, mtime):
        # Load from cache (no hashing!)
        blocks = cache.load(file_path)
        for block in blocks:
            self._hash_table[block.hash_value].append(block)
    else:
        # Hash fresh (cache miss or stale)
        blocks = self._hash_fresh(file_path, content)
        cache.save(file_path, mtime, blocks)
        for block in blocks:
            self._hash_table[block.hash_value].append(block)
```

---

## Scalability Considerations

### Memory Management

**Memory Usage Calculation**:
```
Hash Table:
- dict[int, list[CodeBlock]]
- Each CodeBlock: ~200 bytes (path, lines, snippet, hash)

10K files × 500 blocks/file × 200 bytes/block = ~1GB worst case
Typical: 10K files × 100 blocks × 200 bytes = ~200MB
```

**Optimization Strategies**:
1. **Don't Store File Contents**: Only store code blocks
2. **Truncate Snippets**: Limit snippet length to 500 chars
3. **Interning**: Reuse file path strings
4. **Lazy Loading**: Only load blocks when needed (not implemented yet)

---

### Performance Targets

**Small Projects** (100 files, 5K LOC):
- First run: <1s
- Cached run: <0.1s
- Memory: <50MB

**Medium Projects** (1,000 files, 500K LOC):
- First run: <5s
- Cached run: <1s
- Memory: <200MB

**Large Projects** (10,000 files, 5M LOC):
- First run: <8 minutes (480s)
- Cached run: <30s
- Memory: <500MB

**CI/CD Typical Commit** (10K files, 50 changed):
- Cached + Incremental: <15s
- Speedup: 32x vs full scan

---

## Testing Strategy

### Test Categories (80-100 tests)

**1. Exact Duplicates** (15 tests):
- 3, 5, 10, 20+ line duplicates
- Across 2, 3, 5+ files
- Python and TypeScript

**2. Near-Duplicates** (15 tests):
- Whitespace variations
- Comment differences
- Should match (tokenization normalizes)

**3. Cross-File Detection** (12 tests):
- Multi-file scenarios
- Subdirectories
- Large file counts

**4. Within-File Detection** (10 tests):
- Same file, different functions
- Multiple duplicates in one file

**5. Cache Operations** (12 tests):
- Cache hit/miss
- mtime invalidation
- Corruption recovery
- Cleanup

**6. Config Loading** (10 tests):
- Thresholds
- Cache settings
- Ignore patterns

**7. Violation Messages** (8 tests):
- Format
- Cross-references
- Line numbers

**8. Ignore Directives** (8 tests):
- Inline ignores
- File/directory patterns

**9. CLI Interface** (4 tests):
- Commands
- Options
- Exit codes

**10. Edge Cases** (8 tests):
- Empty files
- Single lines
- No duplicates
- Special characters

---

## Common Pitfalls to Avoid

### Pitfall 1: Buffering All File Contents

**Wrong**:
```python
self._file_buffer = {}  # Store all file contents
for each file:
    self._file_buffer[path] = content  # Memory explosion!
```

**Right**:
```python
self._hash_table = {}  # Store only hashes + metadata
for each file:
    blocks = hash_file(content)  # Process immediately
    self._hash_table.update(blocks)  # Much smaller
```

---

### Pitfall 2: Ignoring mtime for Cache Invalidation

**Wrong**:
```python
if path in cache:
    return cache.load(path)  # Stale data!
```

**Right**:
```python
if cache.is_fresh(path, current_mtime):
    return cache.load(path)  # Safe!
else:
    return rehash(path)  # Invalidate stale cache
```

---

### Pitfall 3: Reporting All Violations at Once

**Wrong**:
```python
# Wait until all files processed
if self._is_last_file():
    return self._find_all_duplicates()  # How to know it's last file?
```

**Right**:
```python
# Report per-file immediately
return self._find_duplicates_for_file(current_file)
```

---

### Pitfall 4: Including in lint-full

**Wrong**:
```yaml
# .thailint.yaml
dry:
  enabled: true  # Always runs in lint-full (too slow!)
```

**Right**:
```yaml
dry:
  enabled: false  # Opt-in only (run via lint-dry)
```

---

## Extension Points

### Future Enhancements

**1. AST-Based Detection**:
- Add `ASTDuplicateDetector` alongside `TokenDuplicateDetector`
- Normalize variable names
- Detect structural duplicates

**2. Configurable Similarity Threshold**:
- Allow 80% similarity (not just exact matches)
- Use edit distance or diff algorithms

**3. Duplicate Clustering**:
- Group related duplicates
- Suggest single refactoring for cluster

**4. Historical Tracking**:
- Track duplication metrics over time
- Graph duplication trends

**5. Auto-Fix Suggestions**:
- Generate refactoring code
- Suggest extract method/class

---

## Success Criteria

**Technical**:
- ✅ Scales to 10K+ files
- ✅ Cache provides 10-50x speedup
- ✅ Memory efficient (<500MB)
- ✅ Token-based hash detection
- ✅ SQLite cache with mtime invalidation

**Functional**:
- ✅ Detects 3+ line duplicates
- ✅ Cross-project detection
- ✅ Helpful violation messages
- ✅ Python + TypeScript support

**Integration**:
- ✅ CLI command with cache options
- ✅ Library API seamless
- ✅ Excluded from lint-full
- ✅ CI/CD friendly

**Quality**:
- ✅ 80-100 tests (100% passing)
- ✅ Pylint 10.00/10
- ✅ Xenon A-grade
- ✅ Zero violations in thai-lint

---

## References

**Algorithm**:
- Rabin-Karp: https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm
- Rolling hash: https://en.wikipedia.org/wiki/Rolling_hash

**SQLite**:
- Python sqlite3 module: https://docs.python.org/3/library/sqlite3.html
- SQLite indexes: https://www.sqlite.org/queryplanner.html

**Patterns**:
- Nesting linter: `.roadmap/complete/nesting-linter/`
- SRP linter: `.roadmap/in-progress/srp-linter/`
- Enterprise linter framework: `.roadmap/complete/enterprise-linter/`

---

## Glossary

**Token**: Normalized code unit (line with comments stripped, whitespace collapsed)

**Rolling Hash**: Hash computed over sliding window of tokens

**Code Block**: Sequence of N lines (where N = min_duplicate_lines)

**Cache Hit**: File unchanged, load blocks from SQLite

**Cache Miss**: File changed or not in cache, rehash

**mtime**: File modification time (used for cache invalidation)

**Hash Table**: In-memory dict mapping hash → list of code blocks

**Duplicate**: 2+ code blocks with same hash

**Violation**: Report of duplicate code at specific location
