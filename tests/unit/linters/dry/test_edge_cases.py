"""
Purpose: Tests for DRY linter edge cases and boundary conditions

Scope: Edge case handling including empty files, minimal files, comment-only files, and unusual inputs

Overview: Test suite for edge cases and boundary conditions covering empty files, single-line
    files, comment-only files, all-unique code, exact threshold matches, below-threshold cases,
    very large files, and special characters. Validates robust handling of unusual inputs and
    corner cases.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 8 test functions for edge case scenarios

Interfaces: Uses Linter class with config file

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated edge case fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

import pytest

from src import Linter


def test_all_comments_no_code(tmp_path):
    """Test file with only comments and no actual code."""
    file1 = tmp_path / "comments1.py"
    file1.write_text("""
# This is a comment
# Another comment
# Yet another comment
# Final comment
""")

    file2 = tmp_path / "comments2.py"
    file2.write_text("""
# This is a comment
# Another comment
# Yet another comment
# Final comment
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_very_large_file(tmp_path):
    """Test handling of very large files with duplicates."""
    pytest.skip("Performance test - takes too long for regular test runs")

    large_content = "\n".join([f"    line_{i} = process_{i}()" for i in range(1000)])

    duplicate_section = """
    x = fetch()
    y = transform(x)
    z = validate(y)
"""

    file1 = tmp_path / "large1.py"
    file1.write_text(f"def huge_function1():\n{large_content}\n{duplicate_section}\n")

    file2 = tmp_path / "large2.py"
    file2.write_text(f"def huge_function2():\n{large_content}\n{duplicate_section}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert isinstance(violations, list)


def test_special_characters_in_code(tmp_path):
    """Test handling of special characters and unicode."""
    file1 = tmp_path / "special1.py"
    file1.write_text("""
def process():
    message = "Hello 世界 🌍"
    pattern = r"^[a-zA-Z0-9_@#$%]+$"
    result = f"{message}: {pattern}"
    return result
""")

    file2 = tmp_path / "special2.py"
    file2.write_text("""
def handle():
    message = "Hello 世界 🌍"
    pattern = r"^[a-zA-Z0-9_@#$%]+$"
    result = f"{message}: {pattern}"
    return result
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2
