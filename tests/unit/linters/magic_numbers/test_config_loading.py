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

    def test_default_allowed_numbers_include_common_values(self):
        """Should use default allowed_numbers including -1, 0, 1, 2, 10, 100, 1000."""
        code = """
def check_values(x):
    if x == -1:
        return "negative one"
    if x == 0:
        return "zero"
    if x == 1:
        return "one"
    if x == 2:
        return "two"
    if x == 10:
        return "ten"
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # All these numbers should be in default allowed_numbers
        assert len(violations) == 0, "Default configuration should allow -1, 0, 1, 2, 10"

    def test_default_max_small_integer_is_ten(self):
        """Should use default max_small_integer of 10 for range context."""
        code = """
def process():
    for i in range(10):  # Should be allowed
        process(i)
    for j in range(11):  # Should violate
        process(j)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        # range(10) should pass, range(11) should fail
        assert len(violations) > 0, "Should flag 11 which exceeds max_small_integer"

    def test_default_enabled_is_true(self):
        """Should be enabled by default."""
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
        # Should detect violations when enabled (default)
        assert len(violations) > 0, "Rule should be enabled by default"


class TestCustomConfiguration:
    """Test custom configuration options."""

    def test_custom_allowed_numbers(self):
        """Should respect custom allowed_numbers configuration."""
        code = """
def calculate():
    return 60  # Adding 60 to allowed list
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        # Mock configuration with custom allowed_numbers
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.config = {"allowed_numbers": {-1, 0, 1, 2, 10, 60, 100, 1000}}

        violations = rule.check(context)
        # 60 is in allowed list, should not violate
        assert len(violations) == 0, "Should allow custom configured numbers"

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

    def test_handles_missing_config_gracefully(self):
        """Should use defaults when config is not provided."""
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
        context.config = None  # No config provided

        violations = rule.check(context)
        # Should still work with defaults
        assert len(violations) > 0, "Should use defaults when config missing"

    def test_handles_partial_config(self):
        """Should merge partial config with defaults."""
        code = """
def get_value():
    return 42  # Not in default allowed
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # Only specify allowed_numbers, other settings should use defaults
        context.config = {"allowed_numbers": {42}}

        violations = rule.check(context)
        # 42 is now allowed, should not violate
        assert len(violations) == 0, "Should merge partial config with defaults"
