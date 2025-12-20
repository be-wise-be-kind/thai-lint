# Performance Optimization Plan

**Purpose**: Detailed implementation plan for thai-lint performance improvements

**Scope**: 4-phase optimization from quick wins to native extensions

**Overview**: Step-by-step implementation guide to achieve <30s worst case, <10s ideal linting times
    across large codebases. Based on profiling analysis showing YAML parsing as primary bottleneck.

**Dependencies**: PERFORMANCE_ANALYSIS.md for benchmark data

**Related**: PROGRESS_TRACKER.md for status, PR_BREAKDOWN.md for PR structure

---

## Phase 1: Quick Wins (1-2 days)

**Expected Impact**: 70% reduction in overhead, ~40% total improvement

### 1.1 Singleton IgnoreDirectiveParser with Cached YAML

**Problem**: YAML config parsed 9x per run (once per linter rule)

**File**: `src/linter_config/ignore.py`

**Implementation**:
```python
# Add at module level
_CACHED_PARSER: IgnoreDirectiveParser | None = None
_CACHED_PROJECT_ROOT: Path | None = None

def get_ignore_parser(project_root: Path | None = None) -> IgnoreDirectiveParser:
    """Get cached ignore parser instance for project root."""
    global _CACHED_PARSER, _CACHED_PROJECT_ROOT

    effective_root = project_root or Path.cwd()
    if _CACHED_PARSER is None or _CACHED_PROJECT_ROOT != effective_root:
        _CACHED_PARSER = IgnoreDirectiveParser(effective_root)
        _CACHED_PROJECT_ROOT = effective_root
    return _CACHED_PARSER

def clear_ignore_parser_cache() -> None:
    """Clear the cached parser (for testing)."""
    global _CACHED_PARSER, _CACHED_PROJECT_ROOT
    _CACHED_PARSER = None
    _CACHED_PROJECT_ROOT = None
```

**Files to update** (replace `IgnoreDirectiveParser()` with `get_ignore_parser()`):
- `src/linters/nesting/linter.py:40`
- `src/linters/srp/linter.py:37`
- `src/linters/magic_numbers/linter.py:48`
- `src/linters/dry/linter.py:49`
- `src/linters/print_statements/linter.py`
- `src/linters/method_property/linter.py`
- `src/linters/stateless_class/linter.py`
- `src/linters/file_header/linter.py`
- `src/linters/pipeline/linter.py`

**Expected Impact**: 1.09s → ~0.12s (90% reduction in YAML overhead)

### 1.2 Pass Project Root Through Context

**Problem**: Each linter resolves project root independently

**File**: `src/orchestrator/core.py`

**Change**: Ensure `metadata["_project_root"]` is set in `FileLintContext`

```python
# In Orchestrator.lint_file()
context = FileLintContext(
    path=file_path,
    lang=language,
    metadata={
        "_project_root": self.project_root,
        # ... other metadata
    }
)
```

**Linter updates**: Pass `context.metadata.get("_project_root")` to `get_ignore_parser()`

---

## Phase 2: Core Caching (3-5 days)

**Expected Impact**: 50% reduction in per-file processing time

### 2.1 Per-File AST Cache

**New File**: `src/core/ast_cache.py`

```python
"""
Purpose: Centralized AST caching to avoid repeated parsing
Scope: Python AST and TypeScript tree-sitter parse results
"""
import ast
from typing import Any

class ASTCache:
    """Per-file AST cache to avoid repeated parsing."""

    def __init__(self) -> None:
        self._python_ast: dict[int, ast.Module | None] = {}
        self._typescript_ast: dict[int, Any] = {}

    def get_python_ast(self, content: str) -> ast.Module | None:
        """Get cached Python AST or parse and cache."""
        content_hash = hash(content)
        if content_hash not in self._python_ast:
            try:
                self._python_ast[content_hash] = ast.parse(content)
            except SyntaxError:
                self._python_ast[content_hash] = None
        return self._python_ast[content_hash]

    def get_typescript_ast(self, content: str) -> Any:
        """Get cached TypeScript AST or parse and cache."""
        from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

        content_hash = hash(content)
        if content_hash not in self._typescript_ast:
            analyzer = TypeScriptBaseAnalyzer()
            self._typescript_ast[content_hash] = analyzer.parse_typescript(content)
        return self._typescript_ast[content_hash]

    def clear(self) -> None:
        """Clear caches."""
        self._python_ast.clear()
        self._typescript_ast.clear()
```

**Update FileLintContext** in `src/orchestrator/core.py`:
```python
class FileLintContext(BaseLintContext):
    def __init__(self, ...):
        # ... existing code ...
        self._ast_cache = ASTCache()

    @property
    def ast_cache(self) -> ASTCache:
        return self._ast_cache
```

**Files to update** (use `context.ast_cache.get_python_ast(content)`):
- `src/linters/dry/python_analyzer.py:148, 279`
- `src/linters/dry/block_filter.py:113`
- `src/linters/nesting/linter.py:107`
- `src/linters/srp/class_analyzer.py:94`

### 2.2 Line Split Caching

**Update FileLintContext** in `src/orchestrator/core.py`:
```python
class FileLintContext(BaseLintContext):
    def __init__(self, ...):
        # ... existing code ...
        self._lines: list[str] | None = None

    @property
    def file_lines(self) -> list[str]:
        """Get file content as cached list of lines."""
        if self._lines is None and self._content is not None:
            self._lines = self._content.split("\n")
        return self._lines or []
```

**Files to update** (use `context.file_lines` instead of `content.split("\n")`):
- `src/linters/dry/block_filter.py:95, 183, 229, 271`
- Other locations using `content.split("\n")`

---

## Phase 3: Parallelism (5-7 days)

**Expected Impact**: Near-linear scaling with CPU cores (4-8x speedup)

### 3.1 Parallel File Processing

**File**: `src/orchestrator/core.py`

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

class Orchestrator:
    def lint_files_parallel(
        self,
        file_paths: list[Path],
        max_workers: int | None = None
    ) -> list[Violation]:
        """Lint files in parallel using process pool."""
        max_workers = max_workers or min(8, multiprocessing.cpu_count())
        violations: list[Violation] = []

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._lint_file_isolated, fp): fp
                for fp in file_paths
            }
            for future in as_completed(futures):
                try:
                    violations.extend(future.result())
                except Exception as e:
                    # Log error but continue
                    pass

        # Finalize after parallel processing (for cross-file rules)
        for rule in self.registry.list_all():
            violations.extend(rule.finalize())

        return violations

    def _lint_file_isolated(self, file_path: Path) -> list[Violation]:
        """Lint a single file in isolation (for subprocess use)."""
        # Recreate minimal state needed for linting
        return self.lint_file(file_path)
```

### 3.2 CLI Flag

**File**: `src/cli/linters/shared.py`

Add `--parallel` / `-p` flag to linter commands:
```python
parallel_option = click.option(
    "--parallel", "-p",
    is_flag=True,
    default=False,
    help="Enable parallel file processing"
)
```

**Note**: DRY linter requires special handling due to stateful SQLite cache

---

## Phase 4: Native Extensions (Optional, 2-4 weeks)

### 4.1 Rust Rolling Hash

**Only if Phase 1-3 don't meet targets**

**New Directory**: `src/rust_ext/`

Setup with Maturin/PyO3:
```toml
# Cargo.toml
[package]
name = "thailint_native"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
```

### 4.2 Persistent File Cache

**New File**: `src/core/persistent_cache.py`

SQLite-based cache with mtime tracking to skip unchanged files.

---

## Validation Checklist

After each phase, verify:

- [ ] All existing tests pass (`just test`)
- [ ] Lint passes (`just lint-full`)
- [ ] Benchmark shows improvement
- [ ] No memory leaks (caches bounded or cleared)

---

## Files Summary

### New Files
| File | Phase | Purpose |
|------|-------|---------|
| `src/core/ast_cache.py` | 2 | AST caching |
| `src/core/persistent_cache.py` | 4 | File mtime cache |
| `src/rust_ext/` | 4 | Native extensions |

### Modified Files
| File | Phase | Change |
|------|-------|--------|
| `src/linter_config/ignore.py` | 1 | Add singleton pattern |
| `src/orchestrator/core.py` | 1,2,3 | Caching, parallelism |
| `src/linters/*/linter.py` | 1 | Use cached ignore parser |
| `src/linters/dry/python_analyzer.py` | 2 | Use AST cache |
| `src/linters/dry/block_filter.py` | 2 | Use line cache |
| `src/linters/nesting/linter.py` | 2 | Use AST cache |
| `src/cli/linters/shared.py` | 3 | Add --parallel flag |

---

*Plan created: December 2024*
*Based on: PERFORMANCE_ANALYSIS.md profiling data*
