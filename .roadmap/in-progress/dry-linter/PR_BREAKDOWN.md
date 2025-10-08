# DRY Linter - PR Breakdown & Implementation Guide

**Purpose**: Detailed step-by-step implementation guide for each pull request in the DRY Linter feature

**Scope**: Complete implementation instructions covering test creation, code development, integration, dogfooding, and documentation

**Overview**: Provides granular guidance for AI agents and developers implementing the DRY Linter across 6 pull requests.
    Each PR section includes specific steps, file contents, code patterns, success criteria, and validation procedures.
    Follows TDD methodology with comprehensive testing before implementation. Designed for systematic execution with
    clear checkpoints and quality gates.

**Dependencies**: Nesting and SRP linter patterns, core orchestrator framework, Python stdlib (sqlite3)

**Related**: PROGRESS_TRACKER.md for current status, AI_CONTEXT.md for architecture rationale

---

## PR1: Complete Test Suite (Pure TDD)

**Objective**: Write 80-100 tests covering ALL DRY linter functionality with ZERO implementation code

**Duration**: 4-6 hours

**Complexity**: High (need to design comprehensive test scenarios for multi-file duplicate detection)

---

### Step 1: Create Test Directory Structure

```bash
mkdir -p tests/unit/linters/dry
touch tests/unit/linters/dry/__init__.py
```

**Files to create**:
- `tests/unit/linters/dry/__init__.py` (empty)
- `tests/unit/linters/dry/test_python_duplicates.py`
- `tests/unit/linters/dry/test_typescript_duplicates.py`
- `tests/unit/linters/dry/test_cross_file_detection.py`
- `tests/unit/linters/dry/test_within_file_detection.py`
- `tests/unit/linters/dry/test_cache_operations.py`
- `tests/unit/linters/dry/test_config_loading.py`
- `tests/unit/linters/dry/test_violation_messages.py`
- `tests/unit/linters/dry/test_ignore_directives.py`
- `tests/unit/linters/dry/test_cli_interface.py`
- `tests/unit/linters/dry/test_library_api.py`
- `tests/unit/linters/dry/test_edge_cases.py`

---

### Step 2: Write Python Duplicate Detection Tests (15 tests)

**File**: `tests/unit/linters/dry/test_python_duplicates.py`

**Test Categories**:
1. Exact 3-line duplicate across 2 files
2. Exact 5-line duplicate across 3 files
3. Exact 10-line duplicate
4. Exact 20-line duplicate
5. Below threshold (2 lines) - no violation
6. Near-duplicate with whitespace variation
7. Near-duplicate with comment differences
8. Duplicate with different variable names (should NOT match - token-based)
9. Duplicate function definitions
10. Duplicate loop structures
11. Duplicate if-elif chains
12. Duplicate try-except blocks
13. Duplicate class methods
14. Multiple duplicates in project
15. No duplicates (all unique code)

**Example Test Pattern**:
```python
"""Tests for Python duplicate code detection."""
import pytest
from pathlib import Path
from src import Linter


def test_exact_3_line_duplicate_across_two_files(tmp_path):
    """Test detecting exact 3-line duplicate in 2 files."""
    # Create file1.py with duplicate code
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process_items(items):
    for item in items:
        if item.is_valid():
            item.save()
    return True
""")

    # Create file2.py with same 3-line duplicate
    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle_data(data):
    for item in items:
        if item.is_valid():
            item.save()
    return False
""")

    # Create minimal config
    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    # Run linter
    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find 2 violations (one per file)
    assert len(violations) == 2

    # Check first violation
    v1 = violations[0]
    assert v1.rule_id == "dry.duplicate-code"
    assert "3 lines" in v1.message or "duplicate" in v1.message.lower()
    assert "file2.py" in v1.message or "file1.py" in v1.message  # Cross-reference

    # Check second violation
    v2 = violations[1]
    assert v2.rule_id == "dry.duplicate-code"
    assert "file1.py" in v2.message or "file2.py" in v2.message  # Cross-reference


def test_below_threshold_no_violation(tmp_path):
    """Test that 2-line duplicates are ignored (threshold=3)."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find NO violations (only 2 lines)
    assert len(violations) == 0


# Add 13 more tests following similar patterns...
```

---

### Step 3: Write TypeScript Duplicate Detection Tests (15 tests)

**File**: `tests/unit/linters/dry/test_typescript_duplicates.py`

Similar structure to Python tests, but with TypeScript/JavaScript code:
- Exact duplicates in .ts files
- Exact duplicates in .js files
- Arrow functions
- Class methods
- Interface definitions (should NOT be detected as duplicates)
- React component patterns
- etc.

**Example**:
```python
def test_typescript_exact_duplicate(tmp_path):
    """Test TypeScript duplicate detection."""
    file1 = tmp_path / "file1.ts"
    file1.write_text("""
function processData(items: Item[]) {
    for (const item of items) {
        if (item.isValid()) {
            item.save();
        }
    }
}
""")

    file2 = tmp_path / "file2.ts"
    file2.write_text("""
function handleRecords(records: Record[]) {
    for (const item of items) {
        if (item.isValid()) {
            item.save();
        }
    }
}
""")

    # Similar assertion pattern...
```

---

### Step 4: Write Cross-File Detection Tests (12 tests)

**File**: `tests/unit/linters/dry/test_cross_file_detection.py`

**Test Categories**:
1. Duplicate in 2 files
2. Duplicate in 3 files
3. Duplicate in 5 files
4. Duplicate in 10 files
5. Duplicate across subdirectories
6. Duplicate across Python and... (no, language-specific)
7. Duplicate in nested directories
8. One file with duplicate, one without
9. Multiple different duplicates across files
10. Same file has 2 duplicates with different files
11. Circular duplicates (A↔B, B↔C, A↔C)
12. Large project with many files but only 2 duplicates

**Example**:
```python
def test_duplicate_across_three_files(tmp_path):
    """Test detecting duplicate in 3 different files."""
    # Create 3 files with same duplicate
    for i in range(1, 4):
        file = tmp_path / f"file{i}.py"
        file.write_text(f"""
def func{i}():
    for item in items:
        if item.valid:
            item.save()
    print("done")
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find 3 violations (one per file)
    assert len(violations) == 3

    # Each violation should reference the OTHER 2 files
    for v in violations:
        # Count how many other files are mentioned
        other_files = [f"file{i}.py" for i in range(1, 4) if f"file{i}.py" not in v.file_path]
        assert any(f in v.message for f in other_files)
```

---

### Step 5: Write Within-File Detection Tests (10 tests)

**File**: `tests/unit/linters/dry/test_within_file_detection.py`

**Test Categories**:
1. Same code appears twice in one file
2. Same code appears 3 times in one file
3. Two different duplicates in one file
4. Duplicate at start and end of file
5. Duplicate in different functions
6. Duplicate in different classes
7. Duplicate in nested scopes
8. Duplicate with one occurrence in another file
9. No within-file duplicates (each block unique)
10. Within-file + cross-file duplicates

**Example**:
```python
def test_duplicate_twice_in_same_file(tmp_path):
    """Test detecting duplicate that appears twice in same file."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def func1():
    for item in items:
        if item.valid:
            item.save()

def func2():
    # Different function, same code
    for item in items:
        if item.valid:
            item.save()

def func3():
    return "unique code"
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find 2 violations (both in same file)
    assert len(violations) == 2
    assert violations[0].file_path == violations[1].file_path
    assert violations[0].line != violations[1].line  # Different line numbers
```

---

### Step 6: Write Cache Operations Tests (12 tests)

**File**: `tests/unit/linters/dry/test_cache_operations.py`

**Test Categories**:
1. Cache miss on first run (no cache file)
2. Cache hit on second run (file unchanged)
3. Cache invalidation on file modification (mtime changed)
4. Cache persists across runs
5. Cache stores correct hash values
6. Cache loads correct code blocks
7. Multiple files in cache
8. Cache handles deleted files
9. Cache corruption recovery (graceful fallback)
10. Cache disabled (no .db file created)
11. Cache cleanup (old entries removed)
12. Cache path configuration

**Example**:
```python
def test_cache_hit_on_second_run(tmp_path):
    """Test that unchanged files use cached hashes."""
    # Create file
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    cache_dir = tmp_path / ".thailint-cache"
    cache_dir.mkdir()

    # First run: should create cache
    linter1 = Linter(config_file=config, project_root=tmp_path)
    violations1 = linter1.lint(tmp_path, rules=['dry.duplicate-code'])

    # Check cache file was created
    cache_file = cache_dir / "dry.db"
    assert cache_file.exists()
    cache_size_1 = cache_file.stat().st_size

    # Second run: should use cache (same results)
    linter2 = Linter(config_file=config, project_root=tmp_path)
    violations2 = linter2.lint(tmp_path, rules=['dry.duplicate-code'])

    # Results should be identical
    assert len(violations1) == len(violations2)

    # Cache file should still exist (not recreated)
    assert cache_file.exists()


def test_cache_invalidation_on_mtime_change(tmp_path):
    """Test that modified files trigger cache invalidation."""
    import time

    file1 = tmp_path / "file1.py"
    file1.write_text("def foo(): pass\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  cache_enabled: true\n  cache_path: '.thailint-cache/dry.db'")

    (tmp_path / ".thailint-cache").mkdir()

    # First run
    linter1 = Linter(config_file=config, project_root=tmp_path)
    linter1.lint(tmp_path, rules=['dry.duplicate-code'])

    # Modify file (change mtime)
    time.sleep(0.1)  # Ensure mtime changes
    file1.write_text("def bar(): pass\n" * 5)  # Different content

    # Second run: should detect change and rehash
    linter2 = Linter(config_file=config, project_root=tmp_path)
    linter2.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should have updated cache with new content
    # (exact assertion depends on implementation)
```

---

### Step 7: Write Config Loading Tests (10 tests)

**File**: `tests/unit/linters/dry/test_config_loading.py`

**Test Categories**:
1. Default config (enabled=false, min_lines=3)
2. Custom min_duplicate_lines
3. Custom min_duplicate_tokens
4. Cache enabled/disabled
5. Custom cache path
6. Custom cache_max_age_days
7. Ignore patterns
8. Invalid config (negative min_lines)
9. Missing config file (use defaults)
10. YAML vs JSON config

**Example**:
```python
def test_custom_min_duplicate_lines(tmp_path):
    """Test custom min_duplicate_lines configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
    z = 3
    w = 4
    return x + y
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
    z = 3
    w = 4
    return x * y
""")

    # Config with min_duplicate_lines=5
    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 5  # Require 5+ lines
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find violations (4 matching lines < 5, but close)
    # Exact result depends on implementation - test boundary
```

---

### Step 8: Write Violation Message Tests (8 tests)

**File**: `tests/unit/linters/dry/test_violation_messages.py`

**Test Categories**:
1. Message includes duplicate line count
2. Message includes occurrence count
3. Message includes all other file locations
4. Message includes line numbers
5. Suggestion includes refactoring advice
6. Message format is consistent
7. Message handles long file paths gracefully
8. Message handles many occurrences (10+ files)

**Example**:
```python
def test_violation_message_includes_all_locations(tmp_path):
    """Test that violation message lists all duplicate locations."""
    # Create 3 files with same duplicate
    for i in range(1, 4):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"""
def func{i}():
    for x in items:
        if x.valid:
            x.process()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Each violation should mention the OTHER files
    for v in violations:
        current_file = Path(v.file_path).name
        other_files = [f"module{i}.py" for i in range(1, 4) if f"module{i}.py" != current_file]

        # Message should contain references to other files
        message_lower = v.message.lower()
        assert any(f in message_lower for f in other_files), f"Expected {other_files} in {v.message}"

        # Should mention it's duplicate code
        assert "duplicate" in message_lower or "repeated" in message_lower

        # Should mention number of occurrences
        assert "3" in v.message or "three" in message_lower
```

---

### Step 9: Write Ignore Directives Tests (8 tests)

**File**: `tests/unit/linters/dry/test_ignore_directives.py`

**Test Categories**:
1. Inline ignore: `# dry: ignore-block`
2. Inline ignore next: `# dry: ignore-next`
3. File-level ignore in config (tests/)
4. Directory-level ignore in config
5. Pattern-based ignore (__init__.py)
6. Ignore only affects specific violations
7. Multiple ignores in same file
8. Ignore disabled when not present

**Example**:
```python
def test_inline_ignore_block(tmp_path):
    """Test that inline ignore directive suppresses violation."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    # dry: ignore-block
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # Should find only 1 violation (file1 ignored, file2 reported)
    assert len(violations) == 1
    assert "file2.py" in violations[0].file_path
```

---

### Step 10: Write CLI Interface Tests (4 tests)

**File**: `tests/unit/linters/dry/test_cli_interface.py`

**Test Categories**:
1. Basic command: `thailint dry <path>`
2. Custom config: `thailint dry --config <file> <path>`
3. Cache options: `thailint dry --no-cache <path>`
4. Output format: `thailint dry --format json <path>`

**Example**:
```python
def test_dry_cli_command_basic(tmp_path):
    """Test basic DRY CLI command."""
    from click.testing import CliRunner
    from src.cli import cli

    # Create files with duplicate
    file1 = tmp_path / "file1.py"
    file1.write_text("def foo():\n    x = 1\n    y = 2\n    z = 3\n")

    file2 = tmp_path / "file2.py"
    file2.write_text("def bar():\n    x = 1\n    y = 2\n    z = 3\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    runner = CliRunner()
    result = runner.invoke(cli, ['dry', str(tmp_path), '--config', str(config)])

    # Should exit with code 1 (violations found)
    assert result.exit_code == 1

    # Output should mention duplicates
    assert "duplicate" in result.output.lower() or "dry" in result.output.lower()
```

---

### Step 11: Write Library API Tests (4 tests)

**File**: `tests/unit/linters/dry/test_library_api.py`

**Test Categories**:
1. Basic usage: `linter.lint(path, rules=['dry.duplicate-code'])`
2. With config file
3. With project root
4. Violation filtering

(Already covered in previous test examples - mainly integration tests)

---

### Step 12: Write Edge Case Tests (8 tests)

**File**: `tests/unit/linters/dry/test_edge_cases.py`

**Test Categories**:
1. Empty file
2. Single line file
3. All comments (no code)
4. All unique code (no duplicates)
5. Exact match at min_duplicate_lines threshold
6. One line below threshold
7. Very large file (1000+ lines)
8. Special characters in code

---

### Step 13: Verify All Tests Fail

```bash
# Run tests - should ALL fail with ModuleNotFoundError
pytest tests/unit/linters/dry/ -v

# Expected output:
# ModuleNotFoundError: No module named 'src.linters.dry'
# 80-100 tests failed
```

**Validation**:
- ✅ 80-100 tests written
- ✅ ALL tests fail with ModuleNotFoundError
- ✅ No implementation code exists
- ✅ Test coverage is comprehensive

---

## PR1.1: Test Review & Architecture Alignment

**Objective**: Review and align PR1 tests with clarified single-pass streaming architecture

**Duration**: 2-4 hours

**Complexity**: Low (mostly test review and minor updates)

---

### Step 1: Review Test Architectural Assumptions

**Action**: Audit all 106 tests for assumptions that conflict with the new architecture

**Key Questions**:
1. Do tests assume `cache_enabled: false` works without any hash table?
2. Do tests expect violations in specific order (violates streaming architecture)?
3. Do tests assume in-memory hash table collection before reporting?
4. Are violation message expectations correct (cross-file references)?

**Command**:
```bash
# Review all test files
grep -r "cache_enabled: false" tests/unit/linters/dry/
grep -r "assert.*violations\[0\]" tests/unit/linters/dry/
```

---

### Step 2: Implement Decision 6 (In-Memory Fallback)

**Decision**: When `cache_enabled: false`, use in-memory dict as fallback

**No Code Changes Needed in PR1.1** - This is just documentation:
- PR2 will implement in-memory fallback in linter.py
- Tests can continue using `cache_enabled: false` for isolation
- Same stateful behavior, just no persistence

**Documentation Update**: Add note to test files explaining in-memory fallback

---

### Step 3: Review test_cache_operations.py

**File**: `tests/unit/linters/dry/test_cache_operations.py`

**Issue**: These tests assume SQLite cache exists even with `cache_enabled: false`

**Action**: Update tests to either:
1. Enable cache (`cache_enabled: true`) for cache operation tests
2. Mark tests as "integration tests" requiring cache
3. Add separate tests for in-memory fallback behavior

**Example Update**:
```python
def test_cache_load_fresh_file(tmp_path):
    """Test loading fresh file from cache."""
    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true  # Changed from false
""")
    # Rest of test...
```

---

### Step 4: Verify Violation Expectations

**Action**: Ensure all tests expect correct violation behavior

**Correct Expectations**:
- 2 files with duplicate → 2 violations (one per file)
- Each violation references OTHER file(s)
- Violation order is NOT guaranteed (streaming)
- Each file reports independently

**Example Correct Test**:
```python
def test_two_files_with_duplicate(tmp_path):
    # Create 2 files with same code...

    violations = linter.lint(tmp_path, rules=['dry.duplicate-code'])

    # CORRECT: Expect 2 violations (one per file)
    assert len(violations) == 2

    # CORRECT: Each violation references the OTHER file
    assert any("file2.py" in v.message for v in violations)
    assert any("file1.py" in v.message for v in violations)

    # INCORRECT: Don't assume order
    # assert violations[0].file_path == "file1.py"  # BAD!
```

---

### Step 5: Update Test Documentation

**Files to Update**:
- Each test file header: Add note about in-memory fallback
- test_cache_operations.py: Explain cache vs in-memory modes

**Example Header Update**:
```python
"""
Purpose: Tests for Python duplicate code detection in DRY linter

...

Implementation: TDD approach - tests written before implementation.
    Tests using cache_enabled: false will run with in-memory fallback (Decision 6).
    Tests using cache_enabled: true will use SQLite for persistence.
    Both modes maintain stateful behavior across files.
"""
```

---

### Step 6: Validate Test Isolation

**Action**: Ensure each test can run independently

**Validation**:
```bash
# Run each test file independently
pytest tests/unit/linters/dry/test_python_duplicates.py -v
pytest tests/unit/linters/dry/test_cross_file_detection.py -v
# etc.

# Run tests in random order
pytest tests/unit/linters/dry/ --random-order

# Run single test
pytest tests/unit/linters/dry/test_python_duplicates.py::test_exact_3_line_duplicate -v
```

---

### Completion Checklist

- [ ] All 106 tests reviewed for architectural assumptions
- [ ] Decision 6 (in-memory fallback) documented in test headers
- [ ] test_cache_operations.py updated to use cache_enabled: true
- [ ] Violation expectations verified (no order assumptions)
- [ ] Test isolation validated (can run independently)
- [ ] All tests still fail with correct ModuleNotFoundError
- [ ] Documentation updated

---

## PR2: Core Implementation + SQLite Cache + In-Memory Fallback

**Objective**: Implement all DRY linter components to pass ~80% of tests

**Duration**: 8-12 hours

**Complexity**: High (SQLite integration, single-pass algorithm, cache invalidation, in-memory fallback)

**Files to Create**:
- `src/linters/dry/__init__.py` - Module exports
- `src/linters/dry/config.py` - DRYConfig dataclass
- `src/linters/dry/cache.py` - SQLite cache manager (WITH query methods)
- `src/linters/dry/token_hasher.py` - Rolling hash implementation
- `src/linters/dry/python_analyzer.py` - Python tokenization
- `src/linters/dry/violation_builder.py` - Violation message formatting
- `src/linters/dry/linter.py` - DRYRule class (stateful, cache-backed WITH in-memory fallback)
- `src/linters/dry/typescript_analyzer.py` - TypeScript stub (PR3 full impl)

**NOTE**: NO duplicate_detector.py - cache.py has query methods instead

**NEW**: Implement Decision 6 (In-Memory Fallback):
- When `cache_enabled: false`, use `dict[int, list[CodeBlock]]` instead of SQLite
- Same stateful behavior, no persistence
- Allows tests to run with isolation

---

### Step 1: Create Module Structure

```bash
mkdir -p src/linters/dry
touch src/linters/dry/__init__.py
```

---

### Step 2: Implement Config Module

**File**: `src/linters/dry/config.py`

```python
"""Configuration schema for DRY linter with caching support."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DRYConfig:
    """Configuration for DRY linter."""

    enabled: bool = False  # Must be explicitly enabled
    min_duplicate_lines: int = 3
    min_duplicate_tokens: int = 30

    # Cache settings
    cache_enabled: bool = True  # ON by default for performance
    cache_path: str = ".thailint-cache/dry.db"
    cache_max_age_days: int = 30

    # Ignore patterns
    ignore_patterns: list[str] = field(default_factory=lambda: [
        "tests/",
        "__init__.py"
    ])

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_duplicate_lines <= 0:
            raise ValueError(f"min_duplicate_lines must be positive, got {self.min_duplicate_lines}")
        if self.min_duplicate_tokens <= 0:
            raise ValueError(f"min_duplicate_tokens must be positive, got {self.min_duplicate_tokens}")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "DRYConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values

        Returns:
            DRYConfig instance with values from dictionary
        """
        return cls(
            enabled=config.get("enabled", False),
            min_duplicate_lines=config.get("min_duplicate_lines", 3),
            min_duplicate_tokens=config.get("min_duplicate_tokens", 30),
            cache_enabled=config.get("cache_enabled", True),
            cache_path=config.get("cache_path", ".thailint-cache/dry.db"),
            cache_max_age_days=config.get("cache_max_age_days", 30),
            ignore_patterns=config.get("ignore", [])
        )
```

---

### Step 3: Implement Cache Module

**File**: `src/linters/dry/cache.py`

```python
"""SQLite cache manager for DRY linter with mtime-based invalidation."""
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeBlock:
    """Represents a code block location with hash."""

    file_path: Path
    start_line: int
    end_line: int
    snippet: str
    hash_value: int


class DRYCache:
    """SQLite-backed cache for duplicate detection."""

    SCHEMA_VERSION = 1

    def __init__(self, cache_path: Path):
        """Initialize cache with SQLite database.

        Args:
            cache_path: Path to SQLite database file
        """
        # Ensure parent directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(str(cache_path))
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables and indexes if they don't exist."""
        # Files table: tracks file metadata
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_path TEXT PRIMARY KEY,
                mtime REAL NOT NULL,
                hash_count INTEGER,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Code blocks table: stores hashes for each file
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS code_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                hash_value INTEGER NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                snippet TEXT NOT NULL,
                FOREIGN KEY (file_path) REFERENCES files(file_path) ON DELETE CASCADE
            )
        """)

        # Critical indexes for performance
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_hash_value
            ON code_blocks(hash_value)
        """)

        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_path
            ON code_blocks(file_path)
        """)

        self.db.commit()

    def is_fresh(self, file_path: Path, current_mtime: float) -> bool:
        """Check if cached data is fresh (mtime matches).

        Args:
            file_path: Path to file
            current_mtime: Current modification time

        Returns:
            True if cache is fresh, False if stale or missing
        """
        cursor = self.db.execute(
            "SELECT mtime FROM files WHERE file_path = ?",
            (str(file_path),)
        )
        row = cursor.fetchone()

        if not row:
            return False  # Not in cache

        cached_mtime = row[0]
        return cached_mtime == current_mtime

    def load(self, file_path: Path) -> list[CodeBlock]:
        """Load cached code blocks for file.

        Args:
            file_path: Path to file

        Returns:
            List of CodeBlock instances from cache
        """
        cursor = self.db.execute(
            """SELECT hash_value, start_line, end_line, snippet
               FROM code_blocks
               WHERE file_path = ?""",
            (str(file_path),)
        )

        blocks = []
        for hash_val, start, end, snippet in cursor:
            block = CodeBlock(
                file_path=file_path,
                start_line=start,
                end_line=end,
                snippet=snippet,
                hash_value=hash_val
            )
            blocks.append(block)

        return blocks

    def save(self, file_path: Path, mtime: float, blocks: list[CodeBlock]) -> None:
        """Save code blocks to cache.

        Args:
            file_path: Path to file
            mtime: File modification time
            blocks: List of CodeBlock instances to cache
        """
        # Delete old data for this file
        self.db.execute("DELETE FROM files WHERE file_path = ?", (str(file_path),))

        # Insert file metadata
        self.db.execute(
            "INSERT INTO files (file_path, mtime, hash_count) VALUES (?, ?, ?)",
            (str(file_path), mtime, len(blocks))
        )

        # Insert code blocks
        for block in blocks:
            self.db.execute(
                """INSERT INTO code_blocks
                   (file_path, hash_value, start_line, end_line, snippet)
                   VALUES (?, ?, ?, ?, ?)""",
                (str(file_path), block.hash_value, block.start_line,
                 block.end_line, block.snippet)
            )

        self.db.commit()

    def cleanup_stale(self, max_age_days: int) -> None:
        """Remove cache entries older than max_age_days.

        Args:
            max_age_days: Maximum age in days for cache entries
        """
        self.db.execute(
            """DELETE FROM files
               WHERE last_scanned < datetime('now', '-{} days')""".format(max_age_days)
        )

        # Vacuum to reclaim space
        self.db.execute("VACUUM")
        self.db.commit()

    def find_duplicates_by_hash(self, hash_value: int) -> list[CodeBlock]:
        """Find all code blocks with the given hash value.

        This is the PRIMARY method for duplicate detection - queries the DB
        for ALL blocks (across ALL files) with the same hash.

        Args:
            hash_value: Hash value to search for

        Returns:
            List of ALL CodeBlock instances with this hash (from all files)
        """
        cursor = self.db.execute(
            """SELECT file_path, hash_value, start_line, end_line, snippet
               FROM code_blocks
               WHERE hash_value = ?""",
            (hash_value,)
        )

        blocks = []
        for file_path_str, hash_val, start, end, snippet in cursor:
            block = CodeBlock(
                file_path=Path(file_path_str),
                start_line=start,
                end_line=end,
                snippet=snippet,
                hash_value=hash_val
            )
            blocks.append(block)

        return blocks

    def get_blocks_for_file(self, file_path: Path) -> list[CodeBlock]:
        """Get all code blocks for a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of CodeBlock instances for this file
        """
        return self.load(file_path)  # Same as load() method

    def add_blocks(self, file_path: Path, mtime: float, blocks: list[CodeBlock]) -> None:
        """Add code blocks to database (alias for save()).

        Args:
            file_path: Path to file
            mtime: File modification time
            blocks: List of CodeBlock instances to add
        """
        self.save(file_path, mtime, blocks)

    def close(self) -> None:
        """Close database connection."""
        self.db.close()
```

**Key Methods for Duplicate Detection**:
- `find_duplicates_by_hash(hash_value)` - Query ALL blocks with this hash (PRIMARY method)
- `get_blocks_for_file(file_path)` - Get blocks for specific file
- `add_blocks()` - Insert new blocks into DB
- `is_fresh()` - Check if file needs re-analysis

---

### Step 4: Implement Token Hasher Module

**File**: `src/linters/dry/token_hasher.py`

```python
"""Tokenization and rolling hash generation for code deduplication."""


class TokenHasher:
    """Tokenize code and create rolling hashes for duplicate detection."""

    def tokenize(self, code: str) -> list[str]:
        """Tokenize code by stripping comments and normalizing whitespace.

        Args:
            code: Source code string

        Returns:
            List of normalized code lines (non-empty, comments removed)
        """
        lines = []

        for line in code.split('\n'):
            # Remove comments (language-specific logic can be added)
            line = self._strip_comments(line)

            # Normalize whitespace (collapse to single space)
            line = ' '.join(line.split())

            # Skip empty lines
            if line:
                lines.append(line)

        return lines

    def _strip_comments(self, line: str) -> str:
        """Remove comments from line (Python # and // style).

        Args:
            line: Source code line

        Returns:
            Line with comments removed
        """
        # Python comments
        if '#' in line:
            line = line[:line.index('#')]

        # JavaScript/TypeScript comments
        if '//' in line:
            line = line[:line.index('//')]

        return line

    def rolling_hash(
        self,
        lines: list[str],
        window_size: int
    ) -> list[tuple[int, int, int, str]]:
        """Create rolling hash windows over code lines.

        Args:
            lines: List of normalized code lines
            window_size: Number of lines per window (min_duplicate_lines)

        Returns:
            List of tuples: (hash_value, start_line, end_line, code_snippet)
        """
        windows = []

        for i in range(len(lines) - window_size + 1):
            # Extract window of N lines
            window_lines = lines[i:i + window_size]

            # Create snippet (lines joined with newline)
            snippet = '\n'.join(window_lines)

            # Hash the snippet
            hash_value = hash(snippet)

            # Line numbers (1-indexed)
            start_line = i + 1
            end_line = i + window_size

            windows.append((hash_value, start_line, end_line, snippet))

        return windows
```

---

### Step 5: Implement Remaining Modules

Due to length constraints, I'll provide module signatures. Full implementation follows same pattern:

**File**: `src/linters/dry/duplicate_detector.py`
```python
class DuplicateDetector:
    def find_duplicates_for_file(
        self, file_path: Path, hash_table: dict
    ) -> list[CodeBlock]:
        """Find all duplicates for given file from hash table."""
```

**File**: `src/linters/dry/violation_builder.py`
```python
class DRYViolationBuilder:
    def build_violations(
        self, duplicates: list[CodeBlock], rule_id: str
    ) -> list[Violation]:
        """Create violation objects with helpful messages."""
```

**File**: `src/linters/dry/python_analyzer.py`
```python
class PythonAnalyzer:
    def strip_comments(self, line: str) -> str:
        """Remove Python-specific comments."""
```

**File**: `src/linters/dry/typescript_analyzer.py`
```python
class TypeScriptAnalyzer:
    def strip_comments(self, line: str) -> str:
        """Remove TypeScript/JavaScript comments (stub for PR2)."""
        return line  # Stub: implement in PR3
```

**File**: `src/linters/dry/linter.py`

**CRITICAL**: This rule is STATEFUL - maintains cache across ALL check() calls

```python
from pathlib import Path
from src.core.base import BaseLintRule, BaseLintContext
from src.core.types import Violation
from .cache import DRYCache
from .config import DRYConfig
from .python_analyzer import PythonAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .violation_builder import DRYViolationBuilder


class DRYRule(BaseLintRule):
    """Main DRY linter rule with stateful cache integration.

    IMPORTANT: This rule maintains state across ALL check() calls:
    - Cache is initialized once and reused for all files
    - Cache serves as both cache AND project-wide hash table
    - Each file queries cache for duplicates immediately
    """

    def __init__(self):
        """Initialize stateful rule."""
        self._cache: DRYCache | None = None
        self._initialized: bool = False
        self._violation_builder = DRYViolationBuilder(self.rule_id)

    @property
    def rule_id(self) -> str:
        return "dry.duplicate-code"

    @property
    def rule_name(self) -> str:
        return "Duplicate Code"

    @property
    def description(self) -> str:
        return "Detects duplicate code across files for DRY principle compliance"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Single-pass streaming algorithm with cache queries.

        Algorithm:
        1. Lazy init cache on first call
        2. Check if file is fresh in cache
        3. If stale/new: analyze file and insert blocks to DB
        4. Query DB for duplicates for THIS file
        5. Build and return violations
        """
        if context.file_content is None:
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        # Lazy initialization on first check() call
        if not self._initialized:
            self._init_cache(context, config)
            self._initialized = True

        file_path = Path(context.file_path)

        # Analyze file or skip if cached
        self._analyze_or_skip(file_path, config)

        # Query cache for duplicates
        violations = self._find_duplicates_for_file(file_path)

        return violations

    def _init_cache(self, context: BaseLintContext, config: DRYConfig) -> None:
        """Initialize cache once for entire project."""
        if not config.cache_enabled:
            return

        project_root = getattr(context, "project_root", None)
        if not project_root:
            return

        cache_path = Path(project_root) / config.cache_path
        self._cache = DRYCache(cache_path)

    def _analyze_or_skip(self, file_path: Path, config: DRYConfig) -> None:
        """Analyze file if new/stale, or skip if fresh in cache."""
        if not file_path.exists():
            return

        mtime = file_path.stat().st_mtime

        # Check if blocks already in cache
        if self._cache and self._cache.is_fresh(file_path, mtime):
            return  # Already in DB, skip analysis

        # Analyze file based on language
        if file_path.suffix == ".py":
            analyzer = PythonAnalyzer(config.min_duplicate_lines)
        elif file_path.suffix in (".ts", ".tsx", ".js", ".jsx"):
            analyzer = TypeScriptAnalyzer(config.min_duplicate_lines)
        else:
            return

        blocks = analyzer.analyze(file_path)

        # Insert blocks into cache (makes them queryable)
        if self._cache and blocks:
            self._cache.add_blocks(file_path, mtime, blocks)

    def _find_duplicates_for_file(self, file_path: Path) -> list[Violation]:
        """Query cache for duplicates for this file."""
        if not self._cache:
            return []

        violations = []

        # Get all blocks for this file
        file_blocks = self._cache.get_blocks_for_file(file_path)

        # For each block, query DB for duplicates
        for block in file_blocks:
            all_blocks = self._cache.find_duplicates_by_hash(block.hash_value)

            # If 2+ blocks with same hash → duplicate
            if len(all_blocks) >= 2:
                # Get OTHER blocks (not from this file)
                other_blocks = [b for b in all_blocks if b.file_path != file_path]
                if other_blocks:
                    violation = self._violation_builder.build_violation(
                        block, other_blocks
                    )
                    violations.append(violation)

        return violations

    def _load_config(self, context: BaseLintContext) -> DRYConfig:
        """Load configuration from context metadata."""
        metadata = getattr(context, "metadata", None)
        if metadata is None or not isinstance(metadata, dict):
            return DRYConfig()

        config_dict = metadata.get("dry", {})
        if not isinstance(config_dict, dict):
            return DRYConfig()

        return DRYConfig.from_dict(config_dict)
```

**Key Implementation Points**:
1. **Stateful**: Cache persists across all check() calls
2. **Lazy Init**: Cache initialized on first file, reused thereafter
3. **Cache IS Hash Table**: No separate in-memory dict needed
4. **Query Per File**: Each file queries DB immediately for duplicates
5. **Streaming**: Process one file at a time, no buffering

---

### Step 6: Run Tests and Iterate

```bash
# Run tests - expect ~80% to pass
pytest tests/unit/linters/dry/ -v

# Check coverage
pytest tests/unit/linters/dry/ --cov=src/linters/dry --cov-report=html
```

**Target**: 64-80 tests passing (~80%)

---

### Step 7: Validate Performance

```bash
# Create 1000-file synthetic project
python scripts/generate_test_project.py --files 1000

# Test performance
time python -m src.cli dry test_project/

# Should be <5s first run
# Should be <1s second run (cached)
```

---

## PR3: Integration (CLI + Library + Docker)

**Objective**: Complete integration and pass 95%+ tests

**Duration**: 4-6 hours

**Complexity**: Medium

---

### Step 1: Add CLI Command

**File**: `src/cli.py` (add new command)

```python
@cli.command("dry")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--config", "-c", "config_file", type=click.Path())
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
@click.option("--min-lines", type=int, help="Override min duplicate lines")
@click.option("--no-cache", is_flag=True, help="Disable cache")
@click.option("--clear-cache", is_flag=True, help="Clear cache before run")
@click.option("--recursive/--no-recursive", default=True)
@click.pass_context
def dry(ctx, path, config_file, format, min_lines, no_cache, clear_cache, recursive):
    """Check for duplicate code (DRY violations)."""
    # Implementation...
```

---

### Step 2: Complete TypeScript Analyzer

Implement tree-sitter parsing for TypeScript duplicate detection.

---

### Step 3: Update Configuration Files

Add `.thailint.yaml` configuration, update `.gitignore`, add Makefile targets.

---

### Step 4: Validate All Integration Points

Test CLI, Library API, Docker, and performance.

---

## PR4: Dogfooding Discovery

**Objective**: Find all DRY violations in thai-lint codebase

**Duration**: 2-3 hours

**Complexity**: Low

Run linter, catalog violations, configure project.

---

## PR5: Dogfooding Fixes

**Objective**: Refactor all violations

**Duration**: 6-10 hours

**Complexity**: High

Fix violations one-by-one following refactoring patterns.

---

## PR6: Documentation

**Objective**: Complete production documentation

**Duration**: 4-6 hours

**Complexity**: Medium

Write comprehensive guide, update README, CHANGELOG.

---

## Success Criteria Summary

**PR1**: 80-100 tests written, all failing
**PR2**: 64-80 tests passing, cache working
**PR3**: 76-95 tests passing, all integration working
**PR4**: Violations cataloged
**PR5**: Zero violations
**PR6**: Documentation complete
