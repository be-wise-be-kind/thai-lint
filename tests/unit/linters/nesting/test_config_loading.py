"""
Purpose: Test configuration loading for nesting depth linter

Scope: YAML/JSON configuration parsing, max_nesting_depth validation, and config overrides

Overview: Validates configuration loading and validation for the nesting depth linter including
    default max_nesting_depth value (4), custom limits loaded from YAML and JSON config files,
    invalid configuration handling and rejection, limit enforcement in violation detection,
    per-file and per-directory configuration overrides, linter enable/disable functionality,
    and comprehensive config validation error messages. Ensures configuration system provides
    flexible control over nesting depth limits while maintaining sensible defaults and preventing
    invalid settings.

Dependencies: pytest for testing framework, src.linters.nesting.config for NestingConfig,
    src.linters.nesting.linter for NestingDepthRule, unittest.mock for Mock objects

Exports: TestConfigLoading (8 tests) covering defaults, custom values, validation, and overrides

Interfaces: Tests NestingConfig dataclass, NestingConfig.from_dict(), and config integration
    with NestingDepthRule.check()

Implementation: Uses inline config dictionaries and YAML/JSON strings, creates NestingConfig
    instances, verifies validation logic and limit application
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestConfigLoading:
    """Test nesting depth configuration."""

    def test_disabled_linter_skips_checks(self):
        """When enabled: false, should skip all checks."""
        from src.linters.nesting.linter import NestingDepthRule

        # Code with excessive nesting
        code = """
def test_func():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                for m in range(5):
                    print(i, j, k, m)
"""
        rule = NestingDepthRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"nesting": {"enabled": False}}

        violations = rule.check(context)
        # Should skip checks when disabled
        assert len(violations) == 0, "Disabled linter should not report violations"

    def test_config_validation_on_creation(self):
        """Should validate configuration values on creation."""
        from src.linters.nesting.config import NestingConfig

        # Valid configs should work
        valid_configs = [
            {"max_nesting_depth": 1},
            {"max_nesting_depth": 10},
            {"max_nesting_depth": 100},
        ]
        for config_dict in valid_configs:
            config = NestingConfig.from_dict(config_dict)
            assert config.max_nesting_depth == config_dict["max_nesting_depth"]

        # Invalid configs should raise
        with pytest.raises(ValueError):
            NestingConfig(max_nesting_depth=0)

        with pytest.raises(ValueError):
            NestingConfig(max_nesting_depth=-5)
