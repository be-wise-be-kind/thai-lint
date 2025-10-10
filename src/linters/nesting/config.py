"""
Purpose: Configuration schema for nesting depth linter

Scope: NestingConfig dataclass with max_nesting_depth setting

Overview: Defines configuration schema for nesting depth linter. Provides NestingConfig dataclass
    with max_nesting_depth field (default 4), validation logic, and config loading from YAML/JSON.
    Supports per-file and per-directory config overrides. Validates that max_depth is positive
    integer. Integrates with the orchestrator's configuration system to allow users to customize
    nesting depth limits via .thailint.yaml configuration files.

Dependencies: dataclasses, typing

Exports: NestingConfig dataclass

Interfaces: NestingConfig(max_nesting_depth: int = 4), from_dict class method for loading config

Implementation: Dataclass with validation and defaults, matches reference implementation default
"""

from dataclasses import dataclass
from typing import Any

# Default nesting threshold constant
DEFAULT_MAX_NESTING_DEPTH = 4


@dataclass
class NestingConfig:
    """Configuration for nesting depth linter."""

    max_nesting_depth: int = DEFAULT_MAX_NESTING_DEPTH  # Default from reference implementation
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_nesting_depth <= 0:
            raise ValueError(f"max_nesting_depth must be positive, got {self.max_nesting_depth}")

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "NestingConfig":
        """Load configuration from dictionary with language-specific overrides.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (python, typescript, javascript) for language-specific thresholds

        Returns:
            NestingConfig instance with values from dictionary
        """
        # Get language-specific config if available
        if language and language in config:
            lang_config = config[language]
            max_nesting_depth = lang_config.get(
                "max_nesting_depth", config.get("max_nesting_depth", DEFAULT_MAX_NESTING_DEPTH)
            )
        else:
            max_nesting_depth = config.get("max_nesting_depth", DEFAULT_MAX_NESTING_DEPTH)

        return cls(
            max_nesting_depth=max_nesting_depth,
            enabled=config.get("enabled", True),
        )
