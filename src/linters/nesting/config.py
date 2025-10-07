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


@dataclass
class NestingConfig:
    """Configuration for nesting depth linter."""

    max_nesting_depth: int = 4  # Default from reference implementation
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_nesting_depth <= 0:
            raise ValueError(f"max_nesting_depth must be positive, got {self.max_nesting_depth}")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "NestingConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values

        Returns:
            NestingConfig instance with values from dictionary
        """
        return cls(
            max_nesting_depth=config.get("max_nesting_depth", 4),
            enabled=config.get("enabled", True),
        )
