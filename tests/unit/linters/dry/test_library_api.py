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


def test_library_basic_usage(tmp_path):
    """Test basic programmatic usage of DRY linter."""
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

    assert isinstance(violations, list)
    assert len(violations) >= 2
    assert all(hasattr(v, "rule_id") for v in violations)
    assert all(hasattr(v, "file_path") for v in violations)
    assert all(hasattr(v, "line") for v in violations)
    assert all(hasattr(v, "message") for v in violations)


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


def test_library_with_project_root(tmp_path):
    """Test library usage with explicit project root."""
    (tmp_path / "src").mkdir()

    file1 = tmp_path / "src" / "file1.py"
    file1.write_text("""
def process():
    x = compute()
    y = validate(x)
    return y
""")

    file2 = tmp_path / "src" / "file2.py"
    file2.write_text("""
def handle():
    x = compute()
    y = validate(x)
    return y
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path / "src", rules=["dry.duplicate-code"])

    assert len(violations) >= 2
    assert all("src" in v.file_path for v in violations)


def test_library_violation_filtering(tmp_path):
    """Test filtering violations by rule_id."""
    duplicate_code = """
    data = load()
    processed = process(data)
    validated = validate(processed)
    return store(validated)
"""

    file1 = tmp_path / "handler1.py"
    file1.write_text(f"def execute1():\n{duplicate_code}\n")

    file2 = tmp_path / "handler2.py"
    file2.write_text(f"def execute2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    all_violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    dry_violations = [v for v in all_violations if v.rule_id == "dry.duplicate-code"]
    assert len(dry_violations) >= 2
    assert all(isinstance(v.message, str) for v in dry_violations)
    assert all(v.line > 0 for v in dry_violations)
