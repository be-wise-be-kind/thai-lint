"""
Purpose: Tests for Python duplicate code detection in DRY linter

Scope: Python language duplicate detection with various patterns and thresholds

Overview: Comprehensive test suite covering exact duplicates, near-duplicates, and
    threshold boundaries for Python code. Tests 3-line, 5-line, 10-line, and 20-line
    duplicates across files, along with whitespace/comment variations. Validates detection
    accuracy and threshold enforcement.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 15 test functions for Python duplicate scenarios

Interfaces: Uses Linter class with config file and rules=['dry.duplicate-code']

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
"""

from src import Linter


def test_exact_3_line_duplicate_across_two_files(
    tmp_path, create_python_file, create_config, duplicate_code_3_lines
):
    """Test detecting exact 3-line duplicate in 2 files."""
    create_python_file(
        "file1.py",
        f"""
def process_items(items):
{duplicate_code_3_lines}
    return True
""",
    )

    create_python_file(
        "file2.py",
        f"""
def handle_data(data):
{duplicate_code_3_lines}
    return False
""",
    )

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2

    v1 = violations[0]
    assert v1.rule_id == "dry.duplicate-code"
    assert "3 lines" in v1.message or "duplicate" in v1.message.lower()
    assert "file2.py" in v1.message or "file1.py" in v1.message

    v2 = violations[1]
    assert v2.rule_id == "dry.duplicate-code"
    assert "file1.py" in v2.message or "file2.py" in v2.message


def test_exact_5_line_duplicate_across_three_files(
    tmp_path, create_duplicate_files, create_config, duplicate_code_5_lines
):
    """Test detecting exact 5-line duplicate in 3 files."""
    create_duplicate_files(duplicate_code_5_lines, count=3, prefix="module")

    config = create_config(min_duplicate_lines=5)

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    for v in violations:
        assert v.rule_id == "dry.duplicate-code"
        assert "duplicate" in v.message.lower() or "5" in v.message


def test_exact_10_line_duplicate(
    tmp_path, create_duplicate_files, create_config, duplicate_code_10_lines
):
    """Test detecting exact 10-line duplicate block."""
    create_duplicate_files(duplicate_code_10_lines, count=2, prefix="database_")

    config = create_config(min_duplicate_lines=10)

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert all(v.rule_id == "dry.duplicate-code" for v in violations)


def test_exact_20_line_duplicate(tmp_path, create_python_file, create_config):
    """Test detecting exact 20+ line duplicate block."""
    large_duplicate = "\n".join([f"    line_{i} = process_{i}(data)" for i in range(20)])

    create_python_file("handler_a", f"def handler_a():\n{large_duplicate}\n    return result\n")
    create_python_file("handler_b", f"def handler_b():\n{large_duplicate}\n    return result\n")

    config = create_config(min_duplicate_lines=20)

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_below_threshold_no_violation(tmp_path, create_python_file, create_config):
    """Test that 2-line duplicates are ignored when threshold is 3."""
    two_line_code = """    x = 1
    y = 2"""

    create_python_file("file1", f"def foo():\n{two_line_code}\n")
    create_python_file("file2", f"def bar():\n{two_line_code}\n")

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_near_duplicate_with_whitespace_variation(tmp_path, create_python_file, create_config):
    """Test near-duplicate detection with whitespace differences."""
    create_python_file(
        "file1",
        """
def process():
    for item in items:
        if item.valid:
            item.save()
""",
    )

    create_python_file(
        "file2",
        """
def handle():
    for item in items:
            if item.valid:
                    item.save()
""",
    )

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_near_duplicate_with_comment_differences(tmp_path, create_python_file, create_config):
    """Test near-duplicate detection with comment variations."""
    create_python_file(
        "file1",
        """
def process():
    # Process items
    for item in items:
        if item.valid:
            item.save()
""",
    )

    create_python_file(
        "file2",
        """
def handle():
    # Handle items differently
    for item in items:
        if item.valid:
            item.save()
""",
    )

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_function_definitions(tmp_path, create_python_file, create_config):
    """Test detection of duplicate function patterns."""
    duplicate_logic = """    if not email:
        return False
    if '@' not in email:
        return False
    return True"""

    create_python_file("utils_a", f"def validate_email(email):\n{duplicate_logic}\n")
    create_python_file("utils_b", f"def check_email(email):\n{duplicate_logic}\n")

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_duplicate_loop_structures(tmp_path, create_python_file, create_config):
    """Test detection of duplicate loop patterns."""
    loop_code = """    for item in items:
        item.validate()
        item.transform()
        item.save()"""

    create_python_file(
        "processor_a", f"def process_batch(items):\n{loop_code}\n    return len(items)\n"
    )
    create_python_file(
        "processor_b", f"def handle_batch(records):\n{loop_code}\n    return len(records)\n"
    )

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_if_elif_chains(tmp_path, create_python_file, create_config):
    """Test detection of duplicate conditional chains."""
    conditional_chain = """    if status == 'pending':
        return 0
    elif status == 'active':
        return 1
    elif status == 'completed':
        return 2
    else:
        return -1"""

    create_python_file("status_a", f"def get_code_a(status):\n{conditional_chain}\n")
    create_python_file("status_b", f"def get_code_b(status):\n{conditional_chain}\n")

    config = create_config(min_duplicate_lines=5)

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_try_except_blocks(tmp_path, create_python_file, create_config):
    """Test detection of duplicate error handling."""
    error_handler = """    try:
        result = risky_operation()
        return result
    except ValueError as e:
        log_error(e)
        return None
    except Exception as e:
        log_critical(e)
        raise"""

    create_python_file("service_a", f"def execute_a():\n{error_handler}\n")
    create_python_file("service_b", f"def execute_b():\n{error_handler}\n")

    config = create_config(min_duplicate_lines=6)

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_class_methods(tmp_path, create_python_file, create_config):
    """Test detection of duplicate methods in different classes."""
    validation_code = """        if not user.email:
            raise ValueError("Email required")
        if not user.name:
            raise ValueError("Name required")
        return True"""

    create_python_file(
        "class_a",
        f"""
class UserManager:
    def validate(self, user):
{validation_code}
""",
    )

    create_python_file(
        "class_b",
        f"""
class ProductManager:
    def validate(self, product):
{validation_code}
""",
    )

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_multiple_duplicates_in_project(tmp_path, create_python_file, create_config):
    """Test detection of multiple different duplicates."""
    duplicate_a = """    x = fetch_data()
    y = process(x)
    z = validate(y)"""

    duplicate_b = """    result = query_db()
    filtered = filter_results(result)
    return sorted(filtered)"""

    create_python_file("mod1", f"def func1():\n{duplicate_a}\n    return z\n")
    create_python_file("mod2", f"def func2():\n{duplicate_a}\n    return z\n")
    create_python_file("mod3", f"def func3():\n{duplicate_b}\n")
    create_python_file("mod4", f"def func4():\n{duplicate_b}\n")

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 4


def test_no_duplicates_all_unique(tmp_path, create_unique_files, create_config):
    """Test that unique code produces no violations."""
    create_unique_files(count=3)

    config = create_config()

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_duplicate_with_different_variable_names_should_not_match(tmp_path):
    """Test that code with different variable names should NOT match (token-based)."""
    file1 = tmp_path / "vars1.py"
    file1.write_text("""
def process():
    result = []
    for user in users:
        if user.active:
            result.append(user)
""")

    file2 = tmp_path / "vars2.py"
    file2.write_text("""
def handle():
    output = []
    for product in products:
        if product.available:
            output.append(product)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0
