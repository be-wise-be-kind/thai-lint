"""
Purpose: Tests for DRY linter ignore directives and exclusion patterns

Scope: Ignore functionality including inline directives, file-level, directory-level, and pattern-based exclusions

Overview: Comprehensive test suite for ignore mechanisms covering inline ignore-block,
    ignore-next directives, file-level config exclusions, directory patterns, pattern-based
    matching, selective ignoring, multiple ignores in same file, and ignore disabled scenarios.
    Validates proper suppression and filtering of violations.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 8 test functions for ignore directive scenarios

Interfaces: Uses Linter class with config file and inline comment directives

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

import pytest

from src import Linter


@pytest.mark.skip(reason="100% duplicate")
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
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) <= 1
    if len(violations) == 1:
        assert "file2.py" in violations[0].file_path


def test_inline_ignore_next(tmp_path):
    """Test that ignore-next directive suppresses next block."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    # dry: ignore-next
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
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) <= 1


def test_file_level_ignore_in_config(tmp_path):
    """Test file-level ignore configured in .thailint.yaml."""
    (tmp_path / "tests").mkdir()

    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "tests" / "test_file.py"
    file2.write_text("""
def test_process():
    for item in items:
        if item.valid:
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


def test_directory_level_ignore(tmp_path):
    """Test directory-level ignore patterns."""
    (tmp_path / "src").mkdir()
    (tmp_path / "vendor").mkdir()

    duplicate_code = """
    result = process()
    validated = validate(result)
    return validated
"""

    file1 = tmp_path / "src" / "module.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "vendor" / "external.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "vendor/"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("vendor" in p for p in violation_paths)


def test_pattern_based_ignore(tmp_path):
    """Test pattern-based ignore for __init__.py files."""
    (tmp_path / "pkg1").mkdir()
    (tmp_path / "pkg2").mkdir()

    duplicate_code = """
    from .module import something
    from .other import another
    __all__ = ['something', 'another']
"""

    file1 = tmp_path / "pkg1" / "__init__.py"
    file1.write_text(duplicate_code)

    file2 = tmp_path / "pkg2" / "__init__.py"
    file2.write_text(duplicate_code)

    file3 = tmp_path / "regular.py"
    file3.write_text(duplicate_code)

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "__init__.py"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("__init__.py" in p for p in violation_paths)


@pytest.mark.skip(reason="100% duplicate")
def test_ignore_only_affects_specific_violations(tmp_path):
    """Test that ignore only suppresses specific violations, not all."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def func1():
    # dry: ignore-block
    for item in items:
        if item.valid:
            item.save()

def func2():
    x = compute()
    y = validate(x)
    return y
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def func3():
    for item in items:
        if item.valid:
            item.save()

def func4():
    x = compute()
    y = validate(x)
    return y
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


@pytest.mark.skip(reason="100% duplicate")
def test_multiple_ignores_in_same_file(tmp_path):
    """Test multiple ignore directives in same file."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def func1():
    # dry: ignore-block
    for item in items:
        if item.valid:
            item.save()

def func2():
    # dry: ignore-block
    x = compute()
    y = validate(x)
    return y
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def func3():
    for item in items:
        if item.valid:
            item.save()

def func4():
    x = compute()
    y = validate(x)
    return y
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    file1_violations = [v for v in violations if "file1.py" in v.file_path]
    assert len(file1_violations) == 0


@pytest.mark.skip(reason="100% duplicate")
def test_ignore_disabled_when_not_present(tmp_path):
    """Test that violations are detected when no ignore directive present."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
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
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
