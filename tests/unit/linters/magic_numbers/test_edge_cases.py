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

import pytest


class TestNegativeNumbers:
    """Test handling of negative numbers."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_negative_magic_numbers(self):
        """Should detect negative magic numbers outside allowed set."""
        code = """
def adjust_value(x):
    return x + -999
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # -999 should be flagged
        assert len(violations) > 0, "Should detect negative magic number -999"

    @pytest.mark.skip(reason="100% duplicate")
    def test_allows_negative_one_by_default(self):
        """Should allow -1 as it's in default allowed_numbers."""
        code = """
def find_index(item, items):
    if item not in items:
        return -1
    return items.index(item)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # -1 is in default allowed_numbers
        assert len(violations) == 0, "Should allow -1 by default"

    @pytest.mark.skip(reason="100% duplicate")
    def test_negative_floats(self):
        """Should detect negative float magic numbers."""
        code = """
def calculate():
    return x * -3.14159
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # -3.14159 should be flagged
        assert len(violations) > 0, "Should detect negative float magic number"


class TestLargeNumbers:
    """Test handling of very large numbers."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_very_large_integers(self):
        """Should detect very large integer literals."""
        code = """
def get_limit():
    return 99999999
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect very large magic number"

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_large_floats(self):
        """Should detect large float literals."""
        code = """
def calculate_distance():
    return distance * 299792458.0  # Speed of light
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect large float magic number"

    @pytest.mark.skip(reason="100% duplicate")
    def test_allows_configured_large_numbers(self):
        """Should allow large numbers if in allowed_numbers."""
        code = """
def get_kilobyte():
    return 1024  # Common in computing
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # 1024 is typically in allowed_numbers for byte calculations
        context.config = {"allowed_numbers": {0, 1, 2, 1024}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should allow 1024 when configured"


class TestScientificNotation:
    """Test handling of scientific notation."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_scientific_notation_numbers(self):
        """Should detect numbers in scientific notation."""
        code = """
def avogadro_constant():
    return 6.02214076e23
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Scientific notation should be detected
        assert len(violations) > 0, "Should detect scientific notation magic number"

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_small_scientific_notation(self):
        """Should detect small numbers in scientific notation."""
        code = """
def planck_constant():
    return 6.62607015e-34
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) > 0, "Should detect small scientific notation"


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

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_numbers_in_dictionary_values(self):
        """Should detect magic numbers in dictionary values."""
        code = """
def get_config():
    return {
        'timeout': 3600,
        'retries': 5,
        'buffer_size': 8192
    }
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect magic numbers in dict values (3600, 5, 8192)
        assert len(violations) > 0, "Should detect magic numbers in dict values"

    @pytest.mark.skip(reason="100% duplicate")
    def test_detects_numbers_in_tuple_assignments(self):
        """Should detect magic numbers in tuple assignments."""
        code = """
def get_coordinates():
    x, y = 42, 365
    return x, y
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Should detect 42 and 365
        assert len(violations) >= 2, "Should detect magic numbers in tuple assignment"

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

    @pytest.mark.skip(reason="100% duplicate")
    def test_zero_and_one_allowed_by_default(self):
        """Should allow 0 and 1 by default in most contexts."""
        code = """
def initialize():
    count = 0
    index = 1
    flag = 1
    return count + index + flag
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # 0 and 1 are in default allowed_numbers
        assert len(violations) == 0, "Should allow 0 and 1 by default"


class TestBoundaryConditions:
    """Test boundary conditions and special cases."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_float_with_decimal_point(self):
        """Should detect floats even with trailing zeros."""
        code = """
def get_value():
    return 42.0
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # 42.0 should be detected as magic number
        assert len(violations) > 0, "Should detect float with trailing zero"

    @pytest.mark.skip(reason="100% duplicate")
    def test_hexadecimal_literals(self):
        """Should detect hexadecimal number literals."""
        code = """
def get_color():
    return 0xFF00AA
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Hex literals should be detected
        assert len(violations) > 0, "Should detect hexadecimal literals"

    @pytest.mark.skip(reason="100% duplicate")
    def test_binary_literals(self):
        """Should detect binary number literals."""
        code = """
def get_mask():
    return 0b11111111
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # Binary literals should be detected
        assert len(violations) > 0, "Should detect binary literals"
