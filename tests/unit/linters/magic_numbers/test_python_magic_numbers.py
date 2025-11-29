"""
Purpose: Unit tests for Python magic number detection

Scope: Testing Python numeric literal detection and acceptable context filtering

Overview: Comprehensive test suite for Python magic number detection covering basic numeric literal
    identification including integers and floats, acceptable contexts where numbers are allowed such
    as constant definitions and range() calls, test file handling, configuration contexts, ignore
    directive support, and various code patterns. Validates that the linter correctly distinguishes
    between magic numbers requiring extraction to named constants and legitimate numeric literals in
    acceptable contexts.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock, src.linters.magic_numbers.linter.MagicNumberRule

Exports: TestBasicDetection, TestAcceptableContexts, TestViolationDetails test classes

Interfaces: test_detects_magic_integers, test_ignores_constant_definitions, test_flags_numbers_in_calculations,
    and other test methods validating MagicNumberRule.check(context)

Implementation: Uses Mock objects for context creation, inline Python code strings as test fixtures,
    validates violation detection with line numbers and descriptive assertions
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicDetection:
    """Test basic magic number detection in Python code."""


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


class TestViolationDetails:
    """Test that violations contain appropriate details."""
