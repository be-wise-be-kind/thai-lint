"""
Purpose: Test suite for decimal number matching in allowed_numbers

Scope: Decimal and integer equivalence in allowed_numbers configuration

Overview: Tests that verify both integer and decimal forms of numbers are properly matched
    against the allowed_numbers configuration. Validates that if 60 is in allowed_numbers,
    then 60.0 should also be allowed (and vice versa). Tests that 1024 and 1024.0 are treated
    as equivalent. Ensures numeric equivalence matching works correctly to prevent false
    positives when users specify integers but code uses floats or decimals.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for
    context mocking, src.linters.magic_numbers.linter for MagicNumberRule

Exports: TestDecimalAllowedNumbers (6 tests) - integer/decimal equivalence both directions

Interfaces: Tests MagicNumberRule configuration handling through check() method

Implementation: Mock-based testing with configuration containing both integer and decimal
    forms, validates that equivalent numeric values are treated as allowed
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.linters.magic_numbers.linter import MagicNumberRule


class TestDecimalAllowedNumbers:
    """Test that integers and decimals are treated as equivalent in allowed_numbers."""

    def test_allows_decimal_when_integer_in_config(self):
        """Should allow 60.0 when 60 is in allowed_numbers.

        RED TEST: This currently fails - 60.0 is flagged even though 60 is allowed.
        """
        code = """
def calculate_timeout():
    timeout = 60.0  # 60 is in allowed_numbers, so 60.0 should be too
    return timeout
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [60],  # Integer form only
            }
        }

        violations = rule.check(context)

        # EXPECTATION: 0 violations (60.0 should match 60)
        # ACTUAL: 1 violation (60.0 not recognized as equivalent to 60)
        assert len(violations) == 0, (
            f"Should allow 60.0 when 60 is in allowed_numbers, but got {len(violations)} violations"
        )

    def test_allows_integer_when_decimal_in_config(self):
        """Should allow 1024 when 1024.0 is in allowed_numbers.

        RED TEST: This might fail - 1024 might not match 1024.0.
        """
        code = """
def get_buffer_size():
    size = 1024  # 1024.0 is in allowed_numbers, so 1024 should be too
    return size
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [1024.0],  # Decimal form only
            }
        }

        violations = rule.check(context)

        # EXPECTATION: 0 violations (1024 should match 1024.0)
        # ACTUAL: Possibly 1 violation (1024 not recognized as equivalent to 1024.0)
        assert len(violations) == 0, (
            f"Should allow 1024 when 1024.0 is in allowed_numbers, "
            f"but got {len(violations)} violations"
        )

    def test_allows_both_forms_with_both_in_config(self):
        """Should allow both 60 and 60.0 when both are in allowed_numbers.

        This test should PASS (GREEN) as a baseline - explicit listing should work.
        """
        code = """
def calculate():
    a = 60    # Explicitly allowed
    b = 60.0  # Explicitly allowed
    return a + b
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [60, 60.0],  # Both forms explicitly listed
            }
        }

        violations = rule.check(context)

        # Both forms explicitly in config, should work
        assert len(violations) == 0, (
            f"Should allow both forms when explicitly listed, got {len(violations)} violations"
        )

    def test_real_world_example_circuit_breaker(self):
        """Should allow 60.0 in circuit breaker timeout calculation.

        RED TEST: Real-world example from user's bug report.
        """
        code = """
class CircuitBreaker:
    def is_open(self):
        if time.time() - self.last_failure > 60.0:  # 60 is in allowed_numbers
            self.status = 0
        return self.status
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("backend/app/core/circuit_breaker.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [0, 60],  # User has 60 in config, 0 for assignment
            }
        }

        violations = rule.check(context)

        # EXPECTATION: 0 violations (60.0 should match 60 in config)
        # ACTUAL: 1 violation at line with "60.0"
        assert len(violations) == 0, (
            f"Should allow 60.0 when 60 is in allowed_numbers (circuit breaker timeout), "
            f"but got {len(violations)} violations"
        )

    def test_real_world_example_oscilloscope(self):
        """Should allow 1024 in buffer size calculation.

        RED TEST: Real-world example from user's bug report.
        """
        code = """
class Oscilloscope:
    def init_buffer(self):
        buffer = bytearray(1024)  # 1024.0 is in allowed_numbers
        return buffer
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("backend/app/oscilloscope.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [1024.0],  # User has 1024.0 in config
            }
        }

        violations = rule.check(context)

        # EXPECTATION: 0 violations (1024 should match 1024.0 in config)
        # ACTUAL: 1 violation at line with "1024"
        assert len(violations) == 0, (
            f"Should allow 1024 when 1024.0 is in allowed_numbers (buffer size), "
            f"but got {len(violations)} violations"
        )

    def test_does_not_allow_different_numbers(self):
        """Should still flag numbers that aren't equivalent to allowed numbers.

        This test should PASS (GREEN) to verify we're not over-allowing.
        """
        code = """
def calculate():
    return 59.0 + 61.0  # Neither should match allowed_numbers=[60]
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "magic_numbers": {
                "enabled": True,
                "allowed_numbers": [60],  # Only 60/60.0 allowed
            }
        }

        violations = rule.check(context)

        # 59.0 and 61.0 should NOT match 60, should be flagged
        assert len(violations) == 2, (
            f"Should flag non-equivalent numbers (59.0, 61.0), expected 2, got {len(violations)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
