"""
Purpose: Unit tests for UnwrapAbuseConfig

Scope: Tests for configuration loading, defaults, and from_dict() behavior

Overview: Comprehensive test suite for UnwrapAbuseConfig dataclass. Tests cover default
    values, from_dict() loading with various configurations, partial configurations,
    and edge cases like empty dictionaries.

Dependencies: pytest, UnwrapAbuseConfig

Exports: Test classes for configuration behavior

Interfaces: Standard pytest test methods

Implementation: Parameterized tests for configuration scenarios
"""

from src.linters.unwrap_abuse.config import UnwrapAbuseConfig


class TestUnwrapAbuseConfigDefaults:
    """Tests for default configuration values."""

    def test_enabled_by_default(self) -> None:
        """Should be enabled by default."""
        config = UnwrapAbuseConfig()
        assert config.enabled is True

    def test_allow_in_tests_by_default(self) -> None:
        """Should allow unwrap in tests by default."""
        config = UnwrapAbuseConfig()
        assert config.allow_in_tests is True

    def test_allow_expect_true_by_default(self) -> None:
        """Should allow expect calls by default (they provide error context)."""
        config = UnwrapAbuseConfig()
        assert config.allow_expect is True

    def test_default_ignore_patterns(self) -> None:
        """Should have examples/ and benches/ in ignore by default."""
        config = UnwrapAbuseConfig()
        assert "examples/" in config.ignore
        assert "benches/" in config.ignore


class TestUnwrapAbuseConfigFromDict:
    """Tests for from_dict() configuration loading."""

    def test_from_empty_dict(self) -> None:
        """Should use defaults for empty dict."""
        config = UnwrapAbuseConfig.from_dict({})
        assert config.enabled is True
        assert config.allow_in_tests is True
        assert config.allow_expect is True

    def test_from_dict_disabled(self) -> None:
        """Should respect enabled=false."""
        config = UnwrapAbuseConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_from_dict_allow_expect(self) -> None:
        """Should allow expect when configured."""
        config = UnwrapAbuseConfig.from_dict({"allow_expect": True})
        assert config.allow_expect is True

    def test_from_dict_disallow_tests(self) -> None:
        """Should flag test code when configured."""
        config = UnwrapAbuseConfig.from_dict({"allow_in_tests": False})
        assert config.allow_in_tests is False

    def test_from_dict_custom_ignore(self) -> None:
        """Should use custom ignore patterns."""
        config = UnwrapAbuseConfig.from_dict({"ignore": ["tests/", "scripts/"]})
        assert config.ignore == ["tests/", "scripts/"]

    def test_from_dict_full_config(self) -> None:
        """Should load all fields from complete config."""
        config = UnwrapAbuseConfig.from_dict(
            {
                "enabled": True,
                "allow_in_tests": False,
                "allow_expect": True,
                "ignore": ["vendor/"],
            }
        )
        assert config.enabled is True
        assert config.allow_in_tests is False
        assert config.allow_expect is True
        assert config.ignore == ["vendor/"]

    def test_from_dict_ignores_language_param(self) -> None:
        """Should accept language parameter without error."""
        config = UnwrapAbuseConfig.from_dict({}, language="rust")
        assert config.enabled is True
