"""
Purpose: Test suite for Python magic number detection

Scope: Python numeric literal detection and violation reporting

Overview: Comprehensive tests for Python magic number detection covering basic numeric literal
    identification (integers and floats), acceptable contexts where numbers are allowed (constant
    definitions, range() calls, test files, configuration contexts), ignore directive support,
    and various code patterns. Validates that the linter correctly distinguishes between magic
    numbers requiring extraction to constants and legitimate numeric literals in acceptable
    contexts. Tests follow TDD approach with all tests initially failing before implementation.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for context
    mocking, src.linters.magic_numbers.linter for MagicNumberRule (will be imported when exists)

Exports: TestBasicDetection (5 tests), TestAcceptableContexts (6 tests), TestViolationDetails
    (3 tests) - total 14 test cases

Interfaces: Tests MagicNumberRule.check(context) -> list[Violation] with Python code samples

Implementation: Uses Mock objects for context creation, inline Python code strings as test
    fixtures, validates violation detection with descriptive assertions
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicDetection:
    """Test basic magic number detection in Python code."""

    def test_detects_integer_in_return_statement(self):
        """Should detect integer magic number in return statement."""
        code = """
def get_timeout():
    return 3600
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 3600 in return"
        assert "3600" in str(violations[0].message), "Violation should mention the number"

    def test_detects_float_in_calculation(self):
        """Should detect float magic number in calculation."""
        code = """
def calculate_area(radius):
    return 3.14159 * radius * radius
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 3.14159 (PI)"
        assert "3.14159" in str(violations[0].message), "Violation should mention PI value"

    def test_detects_integer_in_comparison(self):
        """Should detect integer magic number in comparison."""
        code = """
def is_valid_age(age):
    return age >= 18
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 18 in comparison"

    def test_detects_multiple_magic_numbers(self):
        """Should detect all magic numbers in a function."""
        code = """
def complex_calculation(x):
    result = x * 42 + 365 - 7
    return result
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) >= 3, "Should detect at least 3 magic numbers (42, 365, 7)"

    def test_detects_negative_magic_number(self):
        """Should detect negative magic numbers outside allowed set."""
        code = """
def adjust_value(x):
    return x - 999
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect magic number 999"


class TestAcceptableContexts:
    """Test contexts where numbers are acceptable and should not violate."""

    def test_ignores_constant_definitions(self):
        """Should not flag numbers in UPPERCASE constant definitions."""
        code = """
TIMEOUT_SECONDS = 3600
MAX_RETRIES = 5
PI_VALUE = 3.14159

def use_constants():
    return TIMEOUT_SECONDS
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag constant definitions"

    def test_ignores_small_integers_in_range(self):
        """Should not flag small integers used in range() calls."""
        code = """
def process_batch():
    for i in range(10):
        process(i)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag small integers in range()"

    def test_ignores_allowed_numbers_from_config(self):
        """Should not flag numbers in allowed_numbers configuration."""
        code = """
def check_value(x):
    if x == -1:
        return False
    if x == 0:
        return True
    if x == 100:
        return True
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # -1, 0, 100 are in default allowed_numbers
        assert len(violations) == 0, "Should not flag allowed numbers"

    def test_ignores_numbers_in_test_files(self):
        """Should not flag numbers in test files."""
        code = """
def test_calculation():
    assert calculate(5) == 42
    assert get_timeout() == 3600
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test_my_module.py")  # Test file
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag numbers in test files"

    def test_ignores_small_integers_in_enumerate(self):
        """Should not flag small integers in enumerate() calls."""
        code = """
def process_items(items):
    for index, item in enumerate(items, 1):
        handle(index, item)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("process.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag small integers in enumerate()"

    def test_detects_large_numbers_even_in_range(self):
        """Should flag large numbers in range() that exceed max_small_integer."""
        code = """
def process_many():
    for i in range(5000):
        process(i)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("process.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # 5000 exceeds max_small_integer (10), should be flagged even in range()
        assert len(violations) > 0, "Should flag large numbers even in range()"


class TestViolationDetails:
    """Test that violations contain appropriate details."""

    def test_violation_contains_line_number(self):
        """Should include line number in violation."""
        code = """
def get_value():
    return 42
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        # Line number should be present (line 3 for return 42)
        assert violations[0].line is not None, "Violation should have line number"

    def test_violation_contains_rule_id(self):
        """Should include magic-numbers rule ID."""
        code = """
def get_value():
    return 999
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        assert "magic-numbers" in violations[0].rule_id, "Should have magic-numbers rule ID"

    def test_violation_contains_helpful_message(self):
        """Should provide helpful message suggesting constant extraction."""
        code = """
def get_timeout():
    return 3600
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should have violations"
        message = violations[0].message.lower()
        # Should suggest extracting to constant
        assert any(word in message for word in ["constant", "extract", "named"]), (
            "Message should suggest constant extraction"
        )
