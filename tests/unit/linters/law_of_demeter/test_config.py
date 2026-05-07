"""
Purpose: Test configuration loading for Law of Demeter linter

Scope: LawOfDemeterConfig dataclass, from_dict(), defaults, validation

Overview: Validates configuration loading and validation for the Law of Demeter linter including
    default min_chain_depth value (3), custom limits loaded from config dicts, invalid config
    rejection, enabled/disabled behavior, safe_prefixes/fluent_methods/exempt_modules list
    merging, and check_test_files toggle. Ensures configuration system provides flexible
    control over LoD detection while maintaining sensible defaults.

Dependencies: pytest, src.linters.law_of_demeter.config for LawOfDemeterConfig

Exports: TestConfigDefaults (4 tests), TestConfigFromDict (4 tests),
    TestConfigValidation (3 tests) - total 11 test cases

Interfaces: Tests LawOfDemeterConfig dataclass and LawOfDemeterConfig.from_dict()

Implementation: Creates config instances directly and via from_dict(), verifies defaults,
    custom values, validation errors, and list merging behavior
"""

import pytest


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_min_chain_depth(self) -> None:
        """Should default min_chain_depth to 3."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig()
        assert config.min_chain_depth == 3

    def test_default_enabled(self) -> None:
        """Should default enabled to True."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig()
        assert config.enabled is True

    def test_default_check_test_files(self) -> None:
        """Should default check_test_files to False."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig()
        assert config.check_test_files is False

    def test_default_lists_not_empty(self) -> None:
        """Should have non-empty default safe_prefixes and fluent_methods."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig()
        assert len(config.safe_prefixes) > 0
        assert len(config.fluent_methods) > 0


class TestConfigFromDict:
    """Test config loading from dictionary."""

    def test_from_dict_with_defaults(self) -> None:
        """Should use defaults when dict is empty."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig.from_dict({})
        assert config.min_chain_depth == 3
        assert config.enabled is True

    def test_from_dict_with_custom_depth(self) -> None:
        """Should respect custom min_chain_depth."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig.from_dict({"min_chain_depth": 4})
        assert config.min_chain_depth == 4

    def test_from_dict_disabled(self) -> None:
        """Should respect enabled: false."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_from_dict_merges_safe_prefixes(self) -> None:
        """Should merge user safe_prefixes with defaults."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        config = LawOfDemeterConfig.from_dict({"safe_prefixes": ["custom."]})
        # Should contain both defaults and custom
        assert "custom." in config.safe_prefixes
        assert "self." in config.safe_prefixes


class TestConfigValidation:
    """Test config validation."""

    def test_rejects_zero_depth(self) -> None:
        """Should reject min_chain_depth of 0."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        with pytest.raises(ValueError):
            LawOfDemeterConfig(min_chain_depth=0)

    def test_rejects_negative_depth(self) -> None:
        """Should reject negative min_chain_depth."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        with pytest.raises(ValueError):
            LawOfDemeterConfig(min_chain_depth=-1)

    def test_accepts_valid_depths(self) -> None:
        """Should accept positive min_chain_depth values."""
        from src.linters.law_of_demeter.config import LawOfDemeterConfig

        for depth in [1, 2, 3, 5, 10]:
            config = LawOfDemeterConfig(min_chain_depth=depth)
            assert config.min_chain_depth == depth
