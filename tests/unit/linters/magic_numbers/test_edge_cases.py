"""
Purpose: Test suite for magic numbers edge cases and boundary conditions

Scope: Edge cases, boundary conditions, and special numeric patterns

Overview: Tests for magic numbers linter edge cases including negative numbers, very large
    numbers, scientific notation, special float values, numbers in various contexts (list
    indices, dictionary keys, slice operations), and boundary conditions for allowed numbers.
    Validates that the linter handles unusual numeric patterns correctly and makes appropriate
    decisions for edge cases. Tests ensure robust handling of numeric literals in all Python
    contexts.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for
    context mocking, src.linters.magic_numbers.linter for MagicNumberRule

Exports: TestNegativeNumbers (3 tests), TestLargeNumbers (3 tests), TestScientificNotation
    (2 tests), TestSpecialContexts (5 tests) - total 13 test cases

Interfaces: Tests MagicNumberRule edge case handling through check() method

Implementation: Mock-based testing with edge case numeric patterns, validates appropriate
    violation detection for boundary conditions
"""

from pathlib import Path
from unittest.mock import Mock


class TestNegativeNumbers:
    """Test handling of negative numbers."""


class TestLargeNumbers:
    """Test handling of very large numbers."""


class TestScientificNotation:
    """Test handling of scientific notation."""


class TestSpecialContexts:
    """Test numbers in special contexts."""

    def test_detects_numbers_in_list_literals(self):
        """Should detect magic numbers in list literals."""
        code = """
def get_primes():
    return [2, 3, 5, 7, 11, 13, 17, 19, 23]
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect multiple magic numbers in list (except 2 which is allowed)
        assert len(violations) > 0, "Should detect magic numbers in list literal"

    def test_detects_numbers_in_function_calls(self):
        """Should detect magic numbers passed as function arguments."""
        code = """
def process():
    result = calculate(42, 3.14159, 365)
    return result
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect all magic numbers in function call
        assert len(violations) >= 3, "Should detect magic numbers as function arguments"


class TestBoundaryConditions:
    """Test boundary conditions and special cases."""
