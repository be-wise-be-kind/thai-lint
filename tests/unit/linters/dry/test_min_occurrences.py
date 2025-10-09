"""
Purpose: Tests for DRY linter minimum occurrences configuration

Scope: Language-specific minimum occurrence thresholds for duplicate code detection

Overview: Test suite for configurable minimum occurrences of duplicate code blocks.
    By default, DRY linter reports duplicates when code appears 2+ times. The min_occurrences
    setting allows requiring code to appear N times before reporting (e.g., 3 occurrences
    means code must appear in 3 different locations). This is useful for reducing noise
    from pairs of duplicates that may be acceptable. Supports language-specific thresholds
    (python, typescript, javascript) to account for different code patterns and team preferences.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for min_occurrences configuration

Interfaces: Uses Linter class with config file

Implementation: TDD approach - tests written before implementation. Tests use cache_enabled: false
    for isolation. Validates that duplicates are only reported when occurrence count meets
    or exceeds the configured threshold.
"""

from src import Linter


def test_min_occurrences_default_behavior_two_occurrences(tmp_path):
    """Test default behavior: duplicates reported with 2 occurrences."""
    # Create two files with identical 3-line blocks
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
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

    # Should report violations with 2 occurrences (default behavior)
    assert len(violations) == 2


def test_min_occurrences_python_requires_three(tmp_path):
    """Test min_occurrences: 3 for Python - no violation with only 2 occurrences."""
    # Create two files with identical 3-line blocks
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  python:
    min_occurrences: 3
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should NOT report violations - only 2 occurrences but need 3
    assert len(violations) == 0


def test_min_occurrences_python_reports_three_occurrences(tmp_path):
    """Test min_occurrences: 3 for Python - violation reported with 3 occurrences."""
    # Create three files with identical 3-line blocks
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    file3 = tmp_path / "file3.py"
    file3.write_text("""
def baz():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  python:
    min_occurrences: 3
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should report violations - 3 occurrences meets threshold
    assert len(violations) == 3


def test_min_occurrences_typescript_different_threshold(tmp_path):
    """Test min_occurrences can be different for TypeScript."""
    # Create two TypeScript files with identical blocks
    file1 = tmp_path / "file1.ts"
    file1.write_text("""
function foo() {
    const x = compute();
    const y = transform(x);
    const z = validate(y);
    return z;
}
""")

    file2 = tmp_path / "file2.ts"
    file2.write_text("""
function bar() {
    const x = compute();
    const y = transform(x);
    const z = validate(y);
    return z;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  typescript:
    min_occurrences: 2
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should report violations - TypeScript threshold is 2
    assert len(violations) == 2


def test_min_occurrences_fallback_to_default(tmp_path):
    """Test that languages without specific min_occurrences use default (2)."""
    # Create two JavaScript files
    file1 = tmp_path / "file1.js"
    file1.write_text("""
function foo() {
    const x = compute();
    const y = transform(x);
    const z = validate(y);
    return z;
}
""")

    file2 = tmp_path / "file2.js"
    file2.write_text("""
function bar() {
    const x = compute();
    const y = transform(x);
    const z = validate(y);
    return z;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  python:
    min_occurrences: 3
  # No JavaScript config - should use default
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should report violations - default threshold is 2
    assert len(violations) == 2


def test_min_occurrences_global_override(tmp_path):
    """Test global min_occurrences as fallback for all languages."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = compute()
    y = transform(x)
    z = validate(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  min_occurrences: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should NOT report violations - global threshold is 3
    assert len(violations) == 0
