"""
Purpose: Tests for DRY linter violation message formatting and content

Scope: Violation message content including locations, counts, suggestions, and formatting

Overview: Comprehensive test suite for violation message quality covering line count inclusion,
    occurrence count reporting, cross-file location references, line number precision,
    refactoring suggestions, message consistency, long path handling, and many-occurrence
    scenarios. Validates helpful and actionable violation messages.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 8 test functions for violation message scenarios

Interfaces: Uses Linter class and Violation objects

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from pathlib import Path

import pytest

from src import Linter


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_includes_line_count(tmp_path):
    """Test that violation message includes duplicate line count."""
    duplicate_code = """
    for item in items:
        if item.valid:
            item.save()
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2
    for v in violations:
        assert "3" in v.message or "three" in v.message.lower()


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_includes_occurrence_count(tmp_path):
    """Test that violation message includes total occurrence count."""
    duplicate_code = """
    result = process()
    validated = validate(result)
    return validated
"""

    for i in range(1, 4):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"def func{i}():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    for v in violations:
        assert "3" in v.message or "three" in v.message.lower()


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_includes_all_locations(tmp_path):
    """Test that violation message lists all duplicate locations."""
    duplicate_code = """
    for x in items:
        if x.valid:
            x.process()
"""

    for i in range(1, 4):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"def func{i}():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    for v in violations:
        current_file = Path(v.file_path).name
        other_files = [f"module{i}.py" for i in range(1, 4) if f"module{i}.py" != current_file]

        message_lower = v.message.lower()
        assert any(f in message_lower for f in other_files), (
            f"Expected {other_files} in {v.message}"
        )
        assert "duplicate" in message_lower or "repeated" in message_lower


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_includes_line_numbers(tmp_path):
    """Test that violation message includes line numbers."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def func1():
    pass

def func2():
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def other():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2
    for v in violations:
        assert v.line is not None
        assert v.line > 0


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_includes_refactoring_suggestion(tmp_path):
    """Test that violation message includes helpful refactoring suggestion."""
    duplicate_code = """
    data = fetch()
    cleaned = clean(data)
    return store(cleaned)
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"def process1():\n{duplicate_code}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def process2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2
    for v in violations:
        message_lower = v.message.lower()
        assert any(
            keyword in message_lower
            for keyword in ["extract", "refactor", "function", "method", "duplicate"]
        )


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_format_consistency(tmp_path):
    """Test that violation messages have consistent format."""
    duplicate_code = """
    result = []
    for item in items:
        result.append(item)
    return result
"""

    for i in range(1, 4):
        file = tmp_path / f"file{i}.py"
        file.write_text(f"def func{i}():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    messages = [v.message for v in violations]

    for msg in messages:
        assert isinstance(msg, str)
        assert len(msg) > 20


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_handles_long_paths(tmp_path):
    """Test that violation messages handle long file paths gracefully."""
    (tmp_path / "very" / "long" / "nested" / "directory" / "structure").mkdir(parents=True)

    duplicate_code = """
    x = compute()
    y = validate(x)
    return y
"""

    file1 = tmp_path / "very" / "long" / "nested" / "directory" / "structure" / "file1.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2
    for v in violations:
        assert isinstance(v.message, str)
        assert len(v.message) < 500


@pytest.mark.skip(reason="100% duplicate")
def test_violation_message_handles_many_occurrences(tmp_path):
    """Test that violation message handles 10+ occurrences gracefully."""
    duplicate_code = """
    result = process()
    return validate(result)
"""

    for i in range(1, 12):
        file = tmp_path / f"handler{i}.py"
        file.write_text(f"def execute{i}():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 2\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 11

    for v in violations:
        assert isinstance(v.message, str)
        assert "11" in v.message or "eleven" in v.message.lower()
        assert len(v.message) < 1000
