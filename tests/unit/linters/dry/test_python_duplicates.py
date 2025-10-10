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
