"""
Purpose: Configuration schema for performance linter rules

Scope: PerformanceConfig dataclass with settings for string-concat-loop and regex-in-loop

Overview: Defines configuration schema for performance linter rules. Provides PerformanceConfig
    dataclass with enabled flag and optional rule-specific settings. Supports loading from
    YAML/JSON configuration files. Integrates with the orchestrator's configuration system
    to allow users to customize performance rule settings via .thailint.yaml files.

Dependencies: dataclasses, typing

Exports: PerformanceConfig dataclass

Interfaces: PerformanceConfig(enabled: bool = True), from_dict class method for loading config

Implementation: Dataclass with validation and defaults, simple enabled flag (extensible)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PerformanceConfig:
    """Configuration for performance linter rules."""

    enabled: bool = True

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "PerformanceConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values
            language: Programming language (reserved for language-specific config)

        Returns:
            PerformanceConfig instance with values from dictionary
        """
        return cls(
            enabled=config.get("enabled", True),
        )
