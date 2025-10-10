"""
Purpose: Tests for within-file duplicate detection in DRY linter

Scope: Duplicate code detection within a single file with multiple occurrences

Overview: Comprehensive test suite for detecting duplicates that appear multiple times
    within the same file. Tests duplicates in different functions, classes, nested scopes,
    and combinations of within-file and cross-file duplicates. Validates proper location
    tracking and reporting for same-file duplicates.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 10 test functions for within-file duplicate scenarios

Interfaces: Uses Linter class with config file and rules=['dry.duplicate-code']

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

import pytest

from src import Linter


def test_duplicate_twice_in_same_file(tmp_path):
    """Test detecting duplicate that appears twice in same file."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def func1():
    for item in items:
        if item.valid:
            item.save()

def func2():
    for item in items:
        if item.valid:
            item.save()

def func3():
    return "unique code"
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert violations[0].file_path == violations[1].file_path
    assert violations[0].line != violations[1].line


@pytest.mark.skip(reason="100% duplicate")
def test_duplicate_three_times_in_same_file(tmp_path):
    """Test detecting duplicate that appears 3 times in same file."""
    file1 = tmp_path / "handlers.py"
    file1.write_text("""
def handler_a():
    try:
        result = execute()
        return result
    except Exception as e:
        log_error(e)

def handler_b():
    try:
        result = execute()
        return result
    except Exception as e:
        log_error(e)

def handler_c():
    try:
        result = execute()
        return result
    except Exception as e:
        log_error(e)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    assert all(v.file_path == violations[0].file_path for v in violations)


def test_two_different_duplicates_in_same_file(tmp_path):
    """Test detecting two different duplicate patterns in same file."""
    file1 = tmp_path / "utils.py"
    file1.write_text("""
def func1():
    x = fetch()
    y = transform(x)
    return y

def func2():
    x = fetch()
    y = transform(x)
    return y

def func3():
    a = load()
    b = process(a)
    c = validate(b)
    return c

def func4():
    a = load()
    b = process(a)
    c = validate(b)
    return c
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 4


def test_duplicate_at_start_and_end_of_file(tmp_path):
    """Test detecting duplicate at beginning and end of file."""
    file1 = tmp_path / "module.py"
    file1.write_text("""
def first_function():
    if not data:
        raise ValueError("No data")
    if not data.id:
        raise ValueError("No ID")
    return data

def middle_function():
    return "some unique logic here"

def last_function():
    if not data:
        raise ValueError("No data")
    if not data.id:
        raise ValueError("No ID")
    return data
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert violations[0].line < violations[1].line


@pytest.mark.skip(reason="100% duplicate")
def test_duplicate_in_different_functions(tmp_path):
    """Test detecting duplicates across different function definitions."""
    file1 = tmp_path / "processors.py"
    file1.write_text("""
def process_users(users):
    result = []
    for item in users:
        if item.active:
            result.append(transform(item))
    return result

def process_products(products):
    result = []
    for item in users:
        if item.active:
            result.append(transform(item))
    return result
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_duplicate_in_different_classes(tmp_path):
    """Test detecting duplicates across different class methods."""
    file1 = tmp_path / "services.py"
    file1.write_text("""
class UserService:
    def validate(self, data):
        if not data:
            return False
        if not data.id:
            return False
        if not data.value:
            return False
        return True

class ProductService:
    def validate(self, data):
        if not data:
            return False
        if not data.id:
            return False
        if not data.value:
            return False
        return True
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


@pytest.mark.skip(reason="100% duplicate")
def test_duplicate_in_nested_scopes(tmp_path):
    """Test detecting duplicates in nested function scopes."""
    file1 = tmp_path / "nested.py"
    file1.write_text("""
def outer1():
    def inner():
        x = compute()
        y = validate(x)
        z = store(y)
        return z
    return inner()

def outer2():
    def another_inner():
        x = compute()
        y = validate(x)
        z = store(y)
        return z
    return another_inner()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


@pytest.mark.skip(reason="100% duplicate")
def test_within_file_and_cross_file_duplicates(tmp_path):
    """Test combined within-file and cross-file duplicates."""
    duplicate_code = """
    data = fetch()
    cleaned = clean(data)
    return store(cleaned)
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"""
def func1():
{duplicate_code}

def func2():
{duplicate_code}
""")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"""
def func3():
{duplicate_code}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    file1_violations = [v for v in violations if "file1.py" in v.file_path]
    file2_violations = [v for v in violations if "file2.py" in v.file_path]
    assert len(file1_violations) == 2
    assert len(file2_violations) == 1


@pytest.mark.skip(reason="100% duplicate")
def test_no_within_file_duplicates(tmp_path):
    """Test that file with unique code blocks produces no violations."""
    file1 = tmp_path / "unique.py"
    file1.write_text("""
def func1():
    x = operation1()
    return process1(x)

def func2():
    y = operation2()
    return process2(y)

def func3():
    z = operation3()
    return process3(z)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


@pytest.mark.skip(reason="100% duplicate")
def test_violation_messages_reference_same_file(tmp_path):
    """Test that within-file violations reference the same file."""
    file1 = tmp_path / "duplicates.py"
    file1.write_text("""
def handler1():
    result = execute()
    validated = validate(result)
    return store(validated)

def handler2():
    result = execute()
    validated = validate(result)
    return store(validated)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2

    for v in violations:
        assert "duplicates.py" in v.file_path
        assert v.line is not None
