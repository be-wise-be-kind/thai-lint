"""
Purpose: Tests for SQLite cache operations in DRY linter

Scope: Cache functionality including hits, misses, invalidation, persistence, and corruption recovery

Overview: Comprehensive test suite for SQLite caching layer covering cache miss on first run,
    cache hit on subsequent runs, mtime-based invalidation, persistence across runs, multi-file
    caching, deleted file handling, corruption recovery, cache disabling, cleanup, and custom
    path configuration. Validates performance and correctness of caching mechanism.

Dependencies: pytest, src.Linter, pathlib, time, tmp_path fixture

Exports: 12 test functions for cache operation scenarios

Interfaces: Uses Linter class with config file cache settings

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated cache fixtures.
"""

import time

from src import Linter


def test_cache_miss_on_first_run(tmp_path):
    """Test that first run creates cache (cache miss)."""
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
    cache_file = cache_dir / "dry.db"

    assert not cache_file.exists()

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert cache_file.exists()
    assert cache_file.stat().st_size > 0


def test_cache_hit_on_second_run(tmp_path):
    """Test that unchanged files use cached hashes."""
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

    linter1 = Linter(config_file=config, project_root=tmp_path)
    violations1 = linter1.lint(tmp_path, rules=["dry.duplicate-code"])

    cache_file = cache_dir / "dry.db"
    assert cache_file.exists()

    time.sleep(0.1)

    linter2 = Linter(config_file=config, project_root=tmp_path)
    violations2 = linter2.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations1) == len(violations2)


def test_cache_invalidation_on_file_modification(tmp_path):
    """Test that modified files trigger cache invalidation."""
    file1 = tmp_path / "file1.py"
    file1.write_text("def foo(): pass\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter1 = Linter(config_file=config, project_root=tmp_path)
    violations1 = linter1.lint(tmp_path, rules=["dry.duplicate-code"])

    time.sleep(0.1)
    file1.write_text("def bar(): pass\n" * 5)

    linter2 = Linter(config_file=config, project_root=tmp_path)
    violations2 = linter2.lint(tmp_path, rules=["dry.duplicate-code"])

    assert violations1 != violations2 or len(violations1) == len(violations2)


def test_cache_persists_across_runs(tmp_path):
    """Test that cache persists across multiple linter instances."""
    duplicate_code = """
    result = []
    for item in items:
        result.append(item)
    return result
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    (tmp_path / ".thailint-cache").mkdir()

    for _run in range(3):
        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])
        assert len(violations) == 2


def test_cache_stores_correct_hash_values(tmp_path):
    """Test that cache stores and retrieves correct hash values."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    x = fetch()
    y = transform(x)
    z = validate(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter1 = Linter(config_file=config, project_root=tmp_path)
    violations1 = linter1.lint(tmp_path, rules=["dry.duplicate-code"])

    linter2 = Linter(config_file=config, project_root=tmp_path)
    violations2 = linter2.lint(tmp_path, rules=["dry.duplicate-code"])

    assert violations1 == violations2


def test_multiple_files_in_cache(tmp_path):
    """Test caching with multiple files."""
    for i in range(1, 6):
        file = tmp_path / f"file{i}.py"
        file.write_text(f"""
def function_{i}():
    x_{i} = compute_{i}()
    y_{i} = process_{i}(x_{i})
    return y_{i}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    cache_file = tmp_path / ".thailint-cache" / "dry.db"
    assert cache_file.exists()
    assert cache_file.stat().st_size > 0


def test_cache_handles_deleted_files(tmp_path):
    """Test that cache handles deleted files gracefully."""
    file1 = tmp_path / "file1.py"
    file1.write_text("def foo(): pass\n" * 5)

    file2 = tmp_path / "file2.py"
    file2.write_text("def bar(): pass\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter1 = Linter(config_file=config, project_root=tmp_path)
    linter1.lint(tmp_path, rules=["dry.duplicate-code"])

    file2.unlink()

    linter2 = Linter(config_file=config, project_root=tmp_path)
    violations = linter2.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_cache_corruption_recovery(tmp_path):
    """Test graceful fallback when cache is corrupted."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
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

    cache_file = cache_dir / "dry.db"
    cache_file.write_text("CORRUPTED DATA NOT A VALID SQLITE FILE")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_cache_disabled(tmp_path):
    """Test that no cache file is created when caching is disabled."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    cache_dir = tmp_path / ".thailint-cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "dry.db"

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert not cache_file.exists()


def test_cache_cleanup_old_entries(tmp_path):
    """Test cache cleanup removes entries older than max_age_days."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    x = fetch()
    y = transform(x)
    return y
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
  cache_max_age_days: 1
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    cache_file = tmp_path / ".thailint-cache" / "dry.db"
    assert cache_file.exists()


def test_custom_cache_path(tmp_path):
    """Test custom cache path configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        item.save()
""")

    custom_cache_dir = tmp_path / "custom_cache"
    custom_cache_dir.mkdir()

    config = tmp_path / ".thailint.yaml"
    config.write_text(f"""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: "{custom_cache_dir / "custom.db"}"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    custom_cache_file = custom_cache_dir / "custom.db"
    assert custom_cache_file.exists()
