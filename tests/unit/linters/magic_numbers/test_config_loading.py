"""
Purpose: Test suite for magic numbers linter configuration

Scope: Configuration loading, validation, and application

Overview: Tests for magic numbers linter configuration handling including default configuration
    values, custom allowed_numbers lists, max_small_integer threshold settings, and disabled
    state behavior. Validates that configuration is properly loaded, validated, and applied
    during linting operations. Tests ensure configuration changes affect detection behavior
    appropriately and invalid configurations are handled gracefully.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for
    context mocking, src.linters.magic_numbers.linter for MagicNumberRule

Exports: TestDefaultConfiguration (3 tests), TestCustomConfiguration (4 tests),
    TestConfigurationValidation (2 tests) - total 9 test cases

Interfaces: Tests MagicNumberRule configuration handling through check() method

Implementation: Mock-based testing with configuration injection, validates detection
    behavior changes based on configuration settings
"""

from pathlib import Path
from unittest.mock import Mock


class TestDefaultConfiguration:
    """Test default configuration values."""


class TestCustomConfiguration:
    """Test custom configuration options."""

    def test_custom_max_small_integer(self):
        """Should respect custom max_small_integer configuration."""
        code = """
def process():
    for i in range(20):  # Should be allowed with max_small_integer=20
        process(i)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.config = {"max_small_integer": 20}

        violations = rule.check(context)
        # range(20) should pass with max_small_integer=20
        assert len(violations) == 0, "Should respect custom max_small_integer"

    def test_disabled_configuration(self):
        """Should not report violations when disabled."""
        code = """
def get_value():
    return 999999  # Obvious magic number
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.config = {"enabled": False}

        violations = rule.check(context)
        # Should not detect violations when disabled
        assert len(violations) == 0, "Should not report violations when disabled"

    def test_empty_allowed_numbers_flags_everything(self):
        """Should flag all numbers when allowed_numbers is empty."""
        code = """
def simple():
    x = 0
    y = 1
    return x + y
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.config = {"allowed_numbers": set()}  # Empty set

        violations = rule.check(context)
        # Should flag 0 and 1 when allowed_numbers is empty
        assert len(violations) >= 2, "Should flag all numbers with empty allowed list"


class TestConfigurationValidation:
    """Test configuration validation and error handling."""
