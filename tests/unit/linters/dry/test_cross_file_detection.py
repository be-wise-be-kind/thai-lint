"""
Purpose: Tests for cross-file duplicate detection in DRY linter

Scope: Multi-file duplicate detection across 2, 3, 5, and 10+ files with various patterns

Overview: Comprehensive test suite for cross-file duplicate detection covering scenarios
    with duplicates spanning multiple files, subdirectories, and nested directory structures.
    Tests circular duplicates, selective duplication, and large projects. Validates proper
    cross-referencing in violation messages.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 12 test functions for cross-file duplicate scenarios

Interfaces: Uses Linter class with config file and rules=['dry.duplicate-code']

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from pathlib import Path

from src import Linter


def test_large_project_with_only_two_duplicates(tmp_path):
    """Test large project where only 2 files have duplicates."""
    duplicate_code = """
    result = []
    for i in range(10):
        result.append(i * 2)
    return result
"""

    for i in range(1, 21):
        file = tmp_path / f"unique_{i}.py"
        file.write_text(f"""
def unique_function_{i}():
    value_{i} = compute_{i}()
    processed_{i} = transform_{i}(value_{i})
    return save_{i}(processed_{i})
""")

    dup1 = tmp_path / "duplicate1.py"
    dup1.write_text(f"def dup1():\n{duplicate_code}\n")

    dup2 = tmp_path / "duplicate2.py"
    dup2.write_text(f"def dup2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    violation_files = {Path(v.file_path).name for v in violations}
    assert "duplicate1.py" in violation_files
    assert "duplicate2.py" in violation_files
