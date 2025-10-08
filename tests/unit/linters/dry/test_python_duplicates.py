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
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from src import Linter


def test_exact_3_line_duplicate_across_two_files(tmp_path):
    """Test detecting exact 3-line duplicate in 2 files."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process_items(items):
    for item in items:
        if item.is_valid():
            item.save()
    return True
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle_data(data):
    for item in items:
        if item.is_valid():
            item.save()
    return False
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

    assert len(violations) == 2

    v1 = violations[0]
    assert v1.rule_id == "dry.duplicate-code"
    assert "3 lines" in v1.message or "duplicate" in v1.message.lower()
    assert "file2.py" in v1.message or "file1.py" in v1.message

    v2 = violations[1]
    assert v2.rule_id == "dry.duplicate-code"
    assert "file1.py" in v2.message or "file2.py" in v2.message


def test_exact_5_line_duplicate_across_three_files(tmp_path):
    """Test detecting exact 5-line duplicate in 3 files."""
    duplicate_code = """
    result = []
    for item in data:
        if item.active:
            processed = transform(item)
            result.append(processed)
"""

    for i in range(1, 4):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"""
def function_{i}(data):
{duplicate_code}
    return result
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 3
    for v in violations:
        assert v.rule_id == "dry.duplicate-code"
        assert "duplicate" in v.message.lower() or "5" in v.message


def test_exact_10_line_duplicate(tmp_path):
    """Test detecting exact 10-line duplicate block."""
    duplicate_block = """
    try:
        connection = establish_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        processed = [process_row(r) for r in results]
        cursor.close()
        connection.close()
        return processed
    except Exception as e:
        log_error(e)
"""

    file1 = tmp_path / "database_a.py"
    file1.write_text(f"def query_users():\n{duplicate_block}\n")

    file2 = tmp_path / "database_b.py"
    file2.write_text(f"def query_products():\n{duplicate_block}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 10\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert all(v.rule_id == "dry.duplicate-code" for v in violations)


def test_exact_20_line_duplicate(tmp_path):
    """Test detecting exact 20+ line duplicate block."""
    large_duplicate = "\n".join([f"    line_{i} = process_{i}(data)" for i in range(20)])

    file1 = tmp_path / "handler_a.py"
    file1.write_text(f"def handler_a():\n{large_duplicate}\n    return result\n")

    file2 = tmp_path / "handler_b.py"
    file2.write_text(f"def handler_b():\n{large_duplicate}\n    return result\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 20\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_below_threshold_no_violation(tmp_path):
    """Test that 2-line duplicates are ignored when threshold is 3."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_near_duplicate_with_whitespace_variation(tmp_path):
    """Test near-duplicate detection with whitespace differences."""
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

    assert len(violations) == 2


def test_near_duplicate_with_comment_differences(tmp_path):
    """Test near-duplicate detection with comment variations."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    # Process items
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    # Handle items differently
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_function_definitions(tmp_path):
    """Test detection of duplicate function patterns."""
    file1 = tmp_path / "utils_a.py"
    file1.write_text("""
def validate_email(email):
    if not email:
        return False
    if '@' not in email:
        return False
    return True
""")

    file2 = tmp_path / "utils_b.py"
    file2.write_text("""
def check_email(email):
    if not email:
        return False
    if '@' not in email:
        return False
    return True
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_duplicate_loop_structures(tmp_path):
    """Test detection of duplicate loop patterns."""
    file1 = tmp_path / "processor_a.py"
    file1.write_text("""
def process_batch(items):
    for item in items:
        item.validate()
        item.transform()
        item.save()
    return len(items)
""")

    file2 = tmp_path / "processor_b.py"
    file2.write_text("""
def handle_batch(records):
    for item in items:
        item.validate()
        item.transform()
        item.save()
    return len(records)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_if_elif_chains(tmp_path):
    """Test detection of duplicate conditional chains."""
    conditional_chain = """
    if status == 'pending':
        return 0
    elif status == 'active':
        return 1
    elif status == 'completed':
        return 2
    else:
        return -1
"""

    file1 = tmp_path / "status_a.py"
    file1.write_text(f"def get_code_a(status):\n{conditional_chain}\n")

    file2 = tmp_path / "status_b.py"
    file2.write_text(f"def get_code_b(status):\n{conditional_chain}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_try_except_blocks(tmp_path):
    """Test detection of duplicate error handling."""
    error_handler = """
    try:
        result = risky_operation()
        return result
    except ValueError as e:
        log_error(e)
        return None
    except Exception as e:
        log_critical(e)
        raise
"""

    file1 = tmp_path / "service_a.py"
    file1.write_text(f"def execute_a():\n{error_handler}\n")

    file2 = tmp_path / "service_b.py"
    file2.write_text(f"def execute_b():\n{error_handler}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 6\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_duplicate_class_methods(tmp_path):
    """Test detection of duplicate methods in different classes."""
    file1 = tmp_path / "class_a.py"
    file1.write_text("""
class UserManager:
    def validate(self, user):
        if not user.email:
            raise ValueError("Email required")
        if not user.name:
            raise ValueError("Name required")
        return True
""")

    file2 = tmp_path / "class_b.py"
    file2.write_text("""
class ProductManager:
    def validate(self, product):
        if not user.email:
            raise ValueError("Email required")
        if not user.name:
            raise ValueError("Name required")
        return True
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_multiple_duplicates_in_project(tmp_path):
    """Test detection of multiple different duplicates."""
    duplicate_a = """
    x = fetch_data()
    y = process(x)
    z = validate(y)
"""

    duplicate_b = """
    result = query_db()
    filtered = filter_results(result)
    return sorted(filtered)
"""

    file1 = tmp_path / "mod1.py"
    file1.write_text(f"def func1():\n{duplicate_a}\n    return z\n")

    file2 = tmp_path / "mod2.py"
    file2.write_text(f"def func2():\n{duplicate_a}\n    return z\n")

    file3 = tmp_path / "mod3.py"
    file3.write_text(f"def func3():\n{duplicate_b}\n")

    file4 = tmp_path / "mod4.py"
    file4.write_text(f"def func4():\n{duplicate_b}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 4


def test_no_duplicates_all_unique(tmp_path):
    """Test that unique code produces no violations."""
    file1 = tmp_path / "unique1.py"
    file1.write_text("""
def process_users():
    users = fetch_users()
    return transform_users(users)
""")

    file2 = tmp_path / "unique2.py"
    file2.write_text("""
def process_products():
    products = fetch_products()
    return transform_products(products)
""")

    file3 = tmp_path / "unique3.py"
    file3.write_text("""
def process_orders():
    orders = fetch_orders()
    return transform_orders(orders)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

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
