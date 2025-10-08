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


def test_duplicate_in_two_files(tmp_path):
    """Test detecting duplicate in exactly 2 files."""
    duplicate_code = """
    result = []
    for item in data:
        if item.valid:
            result.append(item)
    return result
"""

    file1 = tmp_path / "module1.py"
    file1.write_text(f"def process1(data):\n{duplicate_code}\n")

    file2 = tmp_path / "module2.py"
    file2.write_text(f"def process2(data):\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert violations[0].file_path != violations[1].file_path


def test_duplicate_in_three_files(tmp_path):
    """Test detecting duplicate in 3 different files."""
    duplicate_code = """
    for item in items:
        if item.valid:
            item.save()
"""

    for i in range(1, 4):
        file = tmp_path / f"file{i}.py"
        file.write_text(f"def func{i}():\n{duplicate_code}\n    print('done')\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3

    for v in violations:
        current_file = Path(v.file_path).name
        other_files = [f"file{i}.py" for i in range(1, 4) if f"file{i}.py" != current_file]
        assert any(f in v.message for f in other_files)


def test_duplicate_in_five_files(tmp_path):
    """Test detecting duplicate in 5 files."""
    duplicate_code = """
    try:
        result = operation()
        return result
    except Exception as e:
        log_error(e)
        raise
"""

    for i in range(1, 6):
        file = tmp_path / f"handler{i}.py"
        file.write_text(f"def execute{i}():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 5
    assert all(v.rule_id == "dry.duplicate-code" for v in violations)


def test_duplicate_in_ten_files(tmp_path):
    """Test detecting duplicate in 10 files."""
    duplicate_code = """
    x = fetch()
    y = transform(x)
    z = validate(y)
"""

    for i in range(1, 11):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"def process{i}():\n{duplicate_code}\n    return z\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 10


def test_duplicate_across_subdirectories(tmp_path):
    """Test detecting duplicates across different subdirectories."""
    duplicate_code = """
    users = fetch_users()
    active = filter_active(users)
    return process(active)
"""

    (tmp_path / "services").mkdir()
    (tmp_path / "handlers").mkdir()
    (tmp_path / "utils").mkdir()

    file1 = tmp_path / "services" / "user_service.py"
    file1.write_text(f"def get_users():\n{duplicate_code}\n")

    file2 = tmp_path / "handlers" / "user_handler.py"
    file2.write_text(f"def handle_users():\n{duplicate_code}\n")

    file3 = tmp_path / "utils" / "user_utils.py"
    file3.write_text(f"def process_users():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3


def test_duplicate_in_nested_directories(tmp_path):
    """Test detecting duplicates in deeply nested directory structures."""
    duplicate_code = """
    if not data:
        raise ValueError("Data required")
    if not data.id:
        raise ValueError("ID required")
    return data
"""

    (tmp_path / "src" / "core" / "services").mkdir(parents=True)
    (tmp_path / "src" / "api" / "handlers").mkdir(parents=True)

    file1 = tmp_path / "src" / "core" / "services" / "validator.py"
    file1.write_text(f"def validate1(data):\n{duplicate_code}\n")

    file2 = tmp_path / "src" / "api" / "handlers" / "validator.py"
    file2.write_text(f"def validate2(data):\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_one_file_with_duplicate_one_without(tmp_path):
    """Test detecting duplicates when one file has it and another doesn't."""
    duplicate_code = """
    result = compute()
    validated = validate(result)
    return save(validated)
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"def process1():\n{duplicate_code}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def process2():\n{duplicate_code}\n")

    file3 = tmp_path / "file3.py"
    file3.write_text("""
def unique_function():
    x = unique_operation()
    y = different_operation(x)
    return completely_different(y)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    violation_files = {Path(v.file_path).name for v in violations}
    assert "file1.py" in violation_files
    assert "file2.py" in violation_files
    assert "file3.py" not in violation_files


def test_multiple_different_duplicates_across_files(tmp_path):
    """Test detecting multiple different duplicates across various files."""
    duplicate_a = """
    data = fetch_data()
    cleaned = clean(data)
    return store(cleaned)
"""

    duplicate_b = """
    users = get_users()
    filtered = filter_active(users)
    return transform(filtered)
"""

    file1 = tmp_path / "mod1.py"
    file1.write_text(f"def func1():\n{duplicate_a}\n")

    file2 = tmp_path / "mod2.py"
    file2.write_text(f"def func2():\n{duplicate_a}\n")

    file3 = tmp_path / "mod3.py"
    file3.write_text(f"def func3():\n{duplicate_b}\n")

    file4 = tmp_path / "mod4.py"
    file4.write_text(f"def func4():\n{duplicate_b}\n")

    file5 = tmp_path / "mod5.py"
    file5.write_text(f"def func5():\n{duplicate_b}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 5


def test_same_file_has_duplicates_with_different_files(tmp_path):
    """Test file that has duplicate code matching two different files."""
    code_block = """
    x = process()
    y = validate(x)
    return y
"""

    file1 = tmp_path / "file1.py"
    file1.write_text(f"def func1():\n{code_block}\n")

    file2 = tmp_path / "file2.py"
    file2.write_text(f"def func2():\n{code_block}\n")

    file3 = tmp_path / "file3.py"
    file3.write_text(f"def func3():\n{code_block}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3


def test_circular_duplicates(tmp_path):
    """Test circular duplicates where A matches B, B matches C, A matches C."""
    duplicate_code = """
    if status == 'active':
        return process()
    elif status == 'pending':
        return wait()
    else:
        return reject()
"""

    file_a = tmp_path / "file_a.py"
    file_a.write_text(f"def check_a(status):\n{duplicate_code}\n")

    file_b = tmp_path / "file_b.py"
    file_b.write_text(f"def check_b(status):\n{duplicate_code}\n")

    file_c = tmp_path / "file_c.py"
    file_c.write_text(f"def check_c(status):\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3

    for v in violations:
        current = Path(v.file_path).name
        others = ["file_a.py", "file_b.py", "file_c.py"]
        others.remove(current)
        assert any(other in v.message for other in others)


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
