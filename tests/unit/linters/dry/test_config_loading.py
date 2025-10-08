"""
Purpose: Tests for DRY linter configuration loading and validation

Scope: Configuration schema validation including defaults, custom values, and error handling

Overview: Comprehensive test suite for configuration loading covering default values,
    custom min_duplicate_lines, min_duplicate_tokens, cache settings, ignore patterns,
    invalid configurations, missing config files, and YAML vs JSON formats. Validates
    proper parsing, validation, and error handling of configuration options.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 10 test functions for configuration loading scenarios

Interfaces: Uses Linter class with config file parameter

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated config fixtures.
"""

import json

import pytest

from src import Linter


def test_default_config_values(tmp_path):
    """Test that linter uses default configuration when no custom values provided."""
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
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_custom_min_duplicate_lines_3(tmp_path):
    """Test custom min_duplicate_lines=3 configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
    z = 3
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
    z = 3
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_custom_min_duplicate_lines_5(tmp_path):
    """Test custom min_duplicate_lines=5 configuration."""
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

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 5
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_custom_min_duplicate_tokens(tmp_path):
    """Test custom min_duplicate_tokens configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    result = fetch() and transform() and validate() and store()
    return result
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    result = fetch() and transform() and validate() and store()
    return result
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 2
  min_duplicate_tokens: 10
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_cache_enabled_configuration(tmp_path):
    """Test cache_enabled configuration option."""
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

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    cache_file = tmp_path / ".thailint-cache" / "dry.db"
    assert cache_file.exists()


def test_custom_cache_path_configuration(tmp_path):
    """Test custom cache_path configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("def foo(): pass\n" * 5)

    custom_dir = tmp_path / "my_cache"
    custom_dir.mkdir()

    config = tmp_path / ".thailint.yaml"
    config.write_text(f"""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: "{custom_dir / "custom.db"}"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert (custom_dir / "custom.db").exists()


def test_cache_max_age_days_configuration(tmp_path):
    """Test cache_max_age_days configuration."""
    file1 = tmp_path / "file1.py"
    file1.write_text("def foo(): pass\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
  cache_max_age_days: 7
""")

    (tmp_path / ".thailint-cache").mkdir()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_ignore_patterns_configuration(tmp_path):
    """Test ignore patterns configuration."""
    (tmp_path / "tests").mkdir()

    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        item.save()
""")

    file2 = tmp_path / "tests" / "test_file.py"
    file2.write_text("""
def test_process():
    for item in items:
        item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "tests/"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("tests" in p for p in violation_paths)


def test_invalid_config_negative_min_lines(tmp_path):
    """Test that invalid config with negative min_lines raises error."""
    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: -1
""")

    with pytest.raises((ValueError, Exception)):
        linter = Linter(config_file=config, project_root=tmp_path)
        linter.lint(tmp_path, rules=["dry.duplicate-code"])


def test_json_config_format(tmp_path):
    """Test that JSON config format works."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        item.save()
""")

    config = tmp_path / ".thailint.json"
    config.write_text(
        json.dumps({"dry": {"enabled": True, "min_duplicate_lines": 3, "cache_enabled": False}})
    )

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)
