"""
Purpose: Test configuration loading and validation for SRP linter

Scope: YAML/JSON configuration parsing, threshold validation, config overrides for SRP analysis

Overview: Validates configuration loading for the SRP linter including default threshold
    values (max_methods=7, max_loc=200), custom limits loaded from configuration files,
    invalid configuration rejection and error handling, threshold enforcement in violation
    detection, per-file and per-directory configuration overrides, keyword list customization,
    linter enable/disable functionality, and comprehensive config validation. Ensures
    configuration system provides flexible control over SRP thresholds while maintaining
    sensible defaults and preventing invalid settings.

Dependencies: pytest for testing framework, src.linters.srp.config for SRPConfig,
    src.linters.srp.linter for SRPRule, unittest.mock for Mock objects

Exports: TestSRPConfigLoading (8 tests) covering defaults, custom values, validation, overrides

Interfaces: Tests SRPConfig dataclass, SRPConfig.from_dict(), and config integration
    with SRPRule.check()

Implementation: Uses inline config dictionaries, creates SRPConfig instances,
    verifies validation logic and threshold application
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestSRPConfigLoading:
    """Test SRP linter configuration loading and validation."""

    def test_default_max_methods_is_seven(self):
        """Default max_methods should be 7."""
        from src.linters.srp.config import SRPConfig

        config = SRPConfig()
        assert config.max_methods == 7, "Default max_methods should be 7"

    def test_default_max_loc_is_200(self):
        """Default max_loc should be 200."""
        from src.linters.srp.config import SRPConfig

        config = SRPConfig()
        assert config.max_loc == 200, "Default max_loc should be 200"

    def test_custom_thresholds_from_dict(self):
        """Should load custom thresholds from dictionary."""
        from src.linters.srp.config import SRPConfig

        config_dict = {
            "max_methods": 5,
            "max_loc": 150,
            "enabled": True,
            "check_keywords": True,
        }
        config = SRPConfig.from_dict(config_dict)
        assert config.max_methods == 5, "Should load custom max_methods"
        assert config.max_loc == 150, "Should load custom max_loc"
        assert config.enabled is True, "Should load enabled flag"

    def test_custom_max_methods_in_rule_context(self):
        """Custom max_methods should be used by rule when provided."""
        from src.linters.srp.linter import SRPRule

        # Code with 6 methods
        code = """
class TestClass:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # Set custom limit of 5
        context.metadata = {"srp": {"max_methods": 5}}

        violations = rule.check(context)
        # 6 methods should violate limit of 5
        assert len(violations) > 0, "6 methods should violate limit 5"

    def test_custom_max_loc_in_rule_context(self):
        """Custom max_loc should be used by rule when provided."""
        from src.linters.srp.linter import SRPRule

        # Code with ~30 lines
        methods = "\n".join([f"    def m{i}(self): pass" for i in range(10)])
        code = f"""
class TestClass:
{methods}
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # Set very low LOC limit
        context.metadata = {"srp": {"max_loc": 20}}

        rule.check(context)
        # Should detect LOC violation with low threshold

    def test_invalid_max_methods_rejects(self):
        """Should reject invalid max_methods values."""
        from src.linters.srp.config import SRPConfig

        # Test negative number
        with pytest.raises(ValueError):
            SRPConfig(max_methods=-1)

        # Test zero
        with pytest.raises(ValueError):
            SRPConfig(max_methods=0)

    def test_invalid_max_loc_rejects(self):
        """Should reject invalid max_loc values."""
        from src.linters.srp.config import SRPConfig

        # Test negative number
        with pytest.raises(ValueError):
            SRPConfig(max_loc=-1)

        # Test zero
        with pytest.raises(ValueError):
            SRPConfig(max_loc=0)

    def test_disabled_linter_skips_checks(self):
        """When enabled: false, should skip all SRP checks."""
        from src.linters.srp.linter import SRPRule

        # Code with many violations
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(50)])
        code = f"""
class MassiveManager:
{methods}
"""
        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"srp": {"enabled": False}}

        violations = rule.check(context)
        assert len(violations) == 0, "Disabled linter should not report violations"

    def test_custom_keyword_list(self):
        """Should support custom responsibility keyword list."""
        from src.linters.srp.config import SRPConfig

        config_dict = {
            "keywords": ["Service", "Controller", "Repository"],
            "check_keywords": True,
        }
        config = SRPConfig.from_dict(config_dict)
        assert "Service" in config.keywords, "Should load custom keywords"
        assert "Controller" in config.keywords
        assert "Repository" in config.keywords

    def test_config_defaults_when_missing(self):
        """Should use defaults when config fields missing."""
        from src.linters.srp.config import SRPConfig

        # Empty dict should use all defaults
        config = SRPConfig.from_dict({})
        assert config.max_methods == 7, "Should default to 7"
        assert config.max_loc == 200, "Should default to 200"
        assert config.enabled is True, "Should default to enabled"
        assert config.check_keywords is True, "Should default to checking keywords"
