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
