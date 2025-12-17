"""
Purpose: Configuration schema for method-should-be-property linter

Scope: Method property linter configuration for Python files

Overview: Defines configuration schema for method-should-be-property linter. Provides
    MethodPropertyConfig dataclass with enabled flag, max_body_statements threshold (default 3)
    for determining when a method body is too complex to be a property candidate, and ignore
    patterns list for excluding specific files or directories. Supports per-file and per-directory
    config overrides through from_dict class method. Integrates with orchestrator's configuration
    system to allow users to customize detection via .thailint.yaml configuration.

Dependencies: dataclasses module for configuration structure, typing module for type hints

Exports: MethodPropertyConfig dataclass

Interfaces: from_dict(config, language) -> MethodPropertyConfig for configuration loading

Implementation: Dataclass with defaults matching Pythonic conventions and common use cases
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MethodPropertyConfig:  # thailint: ignore[dry]
    """Configuration for method-should-be-property linter."""

    enabled: bool = True
    max_body_statements: int = 3
    ignore: list[str] = field(default_factory=list)

    # dry: ignore-block
    @classmethod
    def from_dict(
        cls, config: dict[str, Any] | None, language: str | None = None
    ) -> "MethodPropertyConfig":
        """Load configuration from dictionary.

        Args:
            config: Dictionary containing configuration values, or None
            language: Programming language (unused, for interface compatibility)

        Returns:
            MethodPropertyConfig instance with values from dictionary
        """
        if config is None:
            return cls()

        ignore_patterns = config.get("ignore", [])
        if not isinstance(ignore_patterns, list):
            ignore_patterns = []

        return cls(
            enabled=config.get("enabled", True),
            max_body_statements=config.get("max_body_statements", 3),
            ignore=ignore_patterns,
        )
