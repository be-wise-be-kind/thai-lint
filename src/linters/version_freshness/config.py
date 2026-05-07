"""
Purpose: Configuration dataclass for version-freshness linter

Scope: Define configurable options for runtime version freshness detection

Overview: Provides VersionFreshnessConfig for customizing linter behavior including
    EOL detection, outdated version detection, cache TTL, and ignore patterns.
    Integrates with the configuration system to allow users to customize version
    freshness checking via .thailint.yaml configuration files.

Dependencies: dataclasses, typing

Exports: VersionFreshnessConfig dataclass, DEFAULT_CACHE_TTL_HOURS constant

Interfaces: VersionFreshnessConfig.from_dict() class method for configuration loading

Implementation: Dataclass with sensible defaults and config loading from dictionary
"""

from dataclasses import dataclass, field
from typing import Any

DEFAULT_CACHE_TTL_HOURS = 24


@dataclass
class VersionFreshnessConfig:
    """Configuration for version-freshness linter."""

    enabled: bool = True
    """Whether the linter is enabled."""

    check_eol: bool = True
    """Whether to flag end-of-life versions."""

    check_outdated: bool = False
    """Whether to flag non-latest supported versions (stricter, opt-in)."""

    cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS
    """Hours before refreshing endoflife.date data."""

    ignore: list[str] = field(default_factory=list)
    """File patterns to ignore."""

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.cache_ttl_hours < 0:
            raise ValueError(f"cache_ttl_hours must be non-negative, got {self.cache_ttl_hours}")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "VersionFreshnessConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values

        Returns:
            VersionFreshnessConfig instance with values from dictionary
        """
        return cls(
            enabled=config.get("enabled", True),
            check_eol=config.get("check_eol", True),
            check_outdated=config.get("check_outdated", False),
            cache_ttl_hours=config.get("cache_ttl_hours", DEFAULT_CACHE_TTL_HOURS),
            ignore=config.get("ignore", []),
        )
