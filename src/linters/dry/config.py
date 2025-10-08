"""
Purpose: Configuration schema for DRY linter with caching support

Scope: DRYConfig dataclass with validation, defaults, and loading from dictionary

Overview: Defines configuration structure for the DRY linter including duplicate detection thresholds,
    caching settings, and ignore patterns. Provides validation of configuration values to ensure
    sensible defaults and prevent misconfiguration. Supports loading from YAML configuration files
    through from_dict classmethod. Cache enabled by default for performance on large codebases.

Dependencies: Python dataclasses module

Exports: DRYConfig dataclass

Interfaces: DRYConfig.__init__, DRYConfig.from_dict(config: dict) -> DRYConfig

Implementation: Dataclass with field defaults, __post_init__ validation, and dict-based construction
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DRYConfig:
    """Configuration for DRY linter."""

    enabled: bool = False  # Must be explicitly enabled
    min_duplicate_lines: int = 3
    min_duplicate_tokens: int = 30

    # Cache settings
    cache_enabled: bool = True  # ON by default for performance
    cache_path: str = ".thailint-cache/dry.db"
    cache_max_age_days: int = 30

    # Ignore patterns
    ignore_patterns: list[str] = field(default_factory=lambda: ["tests/", "__init__.py"])

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.min_duplicate_lines <= 0:
            raise ValueError(
                f"min_duplicate_lines must be positive, got {self.min_duplicate_lines}"
            )
        if self.min_duplicate_tokens <= 0:
            raise ValueError(
                f"min_duplicate_tokens must be positive, got {self.min_duplicate_tokens}"
            )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "DRYConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values

        Returns:
            DRYConfig instance with values from dictionary
        """
        return cls(
            enabled=config.get("enabled", False),
            min_duplicate_lines=config.get("min_duplicate_lines", 3),
            min_duplicate_tokens=config.get("min_duplicate_tokens", 30),
            cache_enabled=config.get("cache_enabled", True),
            cache_path=config.get("cache_path", ".thailint-cache/dry.db"),
            cache_max_age_days=config.get("cache_max_age_days", 30),
            ignore_patterns=config.get("ignore", []),
        )
