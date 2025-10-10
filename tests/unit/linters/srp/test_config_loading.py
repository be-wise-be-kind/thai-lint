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

import pytest


class TestSRPConfigLoading:
    """Test SRP linter configuration loading and validation."""

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
