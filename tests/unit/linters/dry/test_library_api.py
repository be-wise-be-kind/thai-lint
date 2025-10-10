"""
Purpose: Tests for DRY linter library/programmatic API

Scope: Programmatic usage of DRY linter via Linter class API

Overview: Test suite for library API covering basic programmatic usage, config file
    integration, project root specification, and violation filtering. Validates proper
    API behavior for embedding DRY linter in other tools and scripts.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 4 test functions for library API scenarios

Interfaces: Uses Linter class directly without CLI

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated API fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from src import Linter


def test_library_with_config_file(tmp_path):
    """Test library usage with explicit config file."""
    duplicate_code = """
    result = fetch()
    cleaned = clean(result)
    return store(cleaned)
"""

    file1 = tmp_path / "module1.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "module2.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / "custom_config.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert all(v.rule_id == "dry.duplicate-code" for v in violations)
