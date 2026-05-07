"""
Purpose: Unit tests for VersionFreshnessConfig

Scope: Configuration loading, defaults, validation, and partial config handling

Overview: Tests the VersionFreshnessConfig dataclass for correct defaults, from_dict
    construction, validation of invalid values, and partial configuration handling.
"""

import pytest

from src.linters.version_freshness.config import (
    DEFAULT_CACHE_TTL_HOURS,
    VersionFreshnessConfig,
)


class TestVersionFreshnessConfigDefaults:
    """Tests for default configuration values."""

    def test_defaults(self):
        """Should have sensible defaults."""
        config = VersionFreshnessConfig()
        assert config.enabled is True
        assert config.check_eol is True
        assert config.check_outdated is False
        assert config.cache_ttl_hours == DEFAULT_CACHE_TTL_HOURS
        assert config.ignore == []

    def test_default_cache_ttl_is_24(self):
        """Default cache TTL should be 24 hours."""
        assert DEFAULT_CACHE_TTL_HOURS == 24


class TestVersionFreshnessConfigFromDict:
    """Tests for from_dict class method."""

    def test_from_empty_dict(self):
        """Should use defaults for empty dict."""
        config = VersionFreshnessConfig.from_dict({})
        assert config.enabled is True
        assert config.check_eol is True
        assert config.check_outdated is False

    def test_from_full_dict(self):
        """Should load all values from dict."""
        config = VersionFreshnessConfig.from_dict(
            {
                "enabled": False,
                "check_eol": False,
                "check_outdated": True,
                "cache_ttl_hours": 48,
                "ignore": ["Dockerfile.legacy"],
            }
        )
        assert config.enabled is False
        assert config.check_eol is False
        assert config.check_outdated is True
        assert config.cache_ttl_hours == 48
        assert config.ignore == ["Dockerfile.legacy"]

    def test_from_partial_dict(self):
        """Should mix provided values with defaults."""
        config = VersionFreshnessConfig.from_dict({"check_outdated": True})
        assert config.enabled is True  # default
        assert config.check_eol is True  # default
        assert config.check_outdated is True  # overridden

    def test_ignores_unknown_keys(self):
        """Should ignore unknown configuration keys."""
        config = VersionFreshnessConfig.from_dict({"unknown_key": "value"})
        assert config.enabled is True


class TestVersionFreshnessConfigValidation:
    """Tests for configuration validation."""

    def test_negative_cache_ttl_raises(self):
        """Should reject negative cache TTL."""
        with pytest.raises(ValueError, match="cache_ttl_hours must be non-negative"):
            VersionFreshnessConfig(cache_ttl_hours=-1)

    def test_zero_cache_ttl_allowed(self):
        """Should allow zero cache TTL (always refresh)."""
        config = VersionFreshnessConfig(cache_ttl_hours=0)
        assert config.cache_ttl_hours == 0
