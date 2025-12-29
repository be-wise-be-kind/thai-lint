"""
Purpose: Tests for LBYL linter configuration

Scope: Unit tests for LBYLConfig dataclass defaults, validation, and loading

Overview: TDD test suite for LBYL configuration. Tests default values for all pattern
    toggles, from_dict() loading from YAML configuration, and validation of config
    options. Verifies that isinstance and none_check are disabled by default due to
    many valid use cases. All tests are marked as skip pending implementation.

Dependencies: pytest, src.linters.lbyl.config

Exports: Test classes for configuration

Interfaces: pytest test discovery and execution

Implementation: TDD tests for configuration validation
"""

import pytest

from src.linters.lbyl.config import LBYLConfig


class TestConfigDataclassDefaults:
    """Tests for LBYLConfig dataclass default values."""

    def test_enabled_by_default(self) -> None:
        """Config is enabled by default."""
        config = LBYLConfig()
        assert config.enabled is True

    def test_dict_key_enabled_by_default(self) -> None:
        """Dict key detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_dict_key is True

    def test_hasattr_enabled_by_default(self) -> None:
        """Hasattr detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_hasattr is True

    def test_isinstance_disabled_by_default(self) -> None:
        """Isinstance detection is disabled by default (many valid uses)."""
        config = LBYLConfig()
        assert config.detect_isinstance is False

    def test_file_exists_enabled_by_default(self) -> None:
        """File exists detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_file_exists is True

    def test_len_check_enabled_by_default(self) -> None:
        """Length check detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_len_check is True

    def test_none_check_disabled_by_default(self) -> None:
        """None check detection is disabled by default (many valid uses)."""
        config = LBYLConfig()
        assert config.detect_none_check is False

    def test_string_validation_enabled_by_default(self) -> None:
        """String validation detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_string_validation is True

    def test_division_check_enabled_by_default(self) -> None:
        """Division check detection is enabled by default."""
        config = LBYLConfig()
        assert config.detect_division_check is True

    def test_ignore_empty_by_default(self) -> None:
        """Ignore list is empty by default."""
        config = LBYLConfig()
        assert config.ignore == []


class TestConfigFromDict:
    """Tests for LBYLConfig.from_dict() loading."""

    def test_loads_empty_dict(self) -> None:
        """Empty dict uses all defaults."""
        config = LBYLConfig.from_dict({})
        assert config.enabled is True
        assert config.detect_dict_key is True

    def test_loads_enabled_false(self) -> None:
        """Loads enabled: false from dict."""
        config = LBYLConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_loads_pattern_toggles(self) -> None:
        """Loads pattern toggle overrides."""
        config = LBYLConfig.from_dict(
            {
                "detect_isinstance": True,
                "detect_none_check": True,
                "detect_dict_key": False,
            }
        )
        assert config.detect_isinstance is True
        assert config.detect_none_check is True
        assert config.detect_dict_key is False

    def test_loads_ignore_patterns(self) -> None:
        """Loads ignore patterns from dict."""
        config = LBYLConfig.from_dict(
            {
                "ignore": ["tests/**", "**/*_test.py"],
            }
        )
        assert "tests/**" in config.ignore
        assert "**/*_test.py" in config.ignore

    def test_ignores_unknown_keys(self) -> None:
        """Unknown keys in dict are ignored."""
        config = LBYLConfig.from_dict(
            {
                "unknown_key": "value",
                "another_unknown": 123,
            }
        )
        assert config.enabled is True  # Still uses defaults


class TestConfigValidation:
    """Tests for configuration validation."""

    @pytest.mark.skip(reason="TDD: Not yet implemented - lbyl PR1")
    def test_validates_ignore_is_list(self) -> None:
        """Ignore must be a list."""
        # from_dict should handle string -> list conversion or raise error
        # config = LBYLConfig.from_dict({"ignore": "tests/**"})
        # assert isinstance(config.ignore, list)
        pass

    @pytest.mark.skip(reason="TDD: Not yet implemented - lbyl PR1")
    def test_validates_pattern_toggles_are_bool(self) -> None:
        """Pattern toggles must be boolean."""
        # from_dict should handle string -> bool conversion or raise error
        # config = LBYLConfig.from_dict({"detect_dict_key": "true"})
        # assert config.detect_dict_key is True
        pass
